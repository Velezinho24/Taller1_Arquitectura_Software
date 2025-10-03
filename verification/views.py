import os
import re
import requests
from urllib.parse import urlparse
from datetime import datetime

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_datetime

from .forms import VerificationForm
from .models import Publisher, Article, AnalyzedNews

from openai import OpenAI
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv('./API.env')

client = OpenAI(api_key=os.environ.get("openai_apikey"))


def verify_link(request):
    """
    Renderiza el formulario para verificar una noticia por URL o texto.
    """
    form = VerificationForm()
    return render(request, 'form.html', {'form': form})


def process_link(request):
    """
    Valida el formulario y guarda en sesión la URL o el texto,
    luego muestra una pantalla de 'processing'.
    """
    if request.method == 'POST':
        form = VerificationForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data.get('url', '').strip()
            text = form.cleaned_data.get('text', '').strip()
            request.session['url'] = url or ''
            request.session['text'] = text or ''
            return render(request, 'processing.html', {'url': url if url else None})
        else:
            return render(request, 'form.html', {'form': form})
    return redirect('verification:verify_link')


def _extract_article_from_url(url: str):
    """
    Descarga y extrae información básica (title, author, date, text) desde una URL.
    Devuelve (title, author, date_str, article_text). date_str puede venir formateada
    o en bruto si no se pudo parsear.
    """
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.content, 'html.parser')

    paragraphs = soup.find_all('p')
    article_text = ' '.join(p.get_text() for p in paragraphs).strip()
    if len(article_text) > 4000:
        article_text = article_text[:4000]

    title = soup.title.string.strip() if soup.title and soup.title.string else 'not available'

    author = None
    author_meta = soup.find('meta', attrs={'name': 'author'}) or soup.find('meta', attrs={'property': 'article:author'})
    if author_meta and author_meta.get('content'):
        author = author_meta.get('content').strip()
    else:
        author_tag = soup.find(attrs={'class': (lambda x: x and 'author' in x.lower())})
        author = author_tag.get_text().strip() if author_tag and author_tag.get_text() else 'not available'
    if not author:
        author = 'not available'

    date_str = None
    date_meta = soup.find('meta', attrs={'property': 'article:published_time'}) or soup.find('meta', attrs={'name': 'date'})
    if date_meta and date_meta.get('content'):
        date_str = date_meta.get('content').strip()
    else:
        time_tag = soup.find('time')
        if time_tag and time_tag.get('datetime'):
            date_str = time_tag['datetime'].strip()
        elif time_tag and time_tag.get_text():
            date_str = time_tag.get_text().strip()

    if not date_str:
        date_str = 'not available'
    else:
        try:
            parsed = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            date_str = parsed.strftime('%d %B %Y, %H:%M')
        except Exception:
            pass

    return title, author, date_str, article_text


def _infer_publisher_from_url(url: str):
    """
    Intenta inferir el Publisher a partir del dominio de la URL.
    """
    try:
        netloc = urlparse(url).netloc if url else None
        if netloc:
            publisher, _ = Publisher.objects.get_or_create(
                name=netloc,
                defaults={"website": f"https://{netloc}"}
            )
            return publisher
    except Exception:
        pass
    return None


def _parse_published_at(date_str: str):
    """
    Intenta convertir date_str a datetime. Devuelve None si no es posible.
    """
    if not date_str or date_str == 'not available':
        return None

    dt = parse_datetime(date_str)
    if dt:
        return dt

    COMMON_FORMATS = [
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%d %B %Y, %H:%M',
        '%d %b %Y',
        '%d/%m/%Y',
        '%m/%d/%Y',
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%dT%H:%M:%S.%f%z',
    ]
    for fmt in COMMON_FORMATS:
        try:
            return datetime.strptime(date_str, fmt)
        except Exception:
            continue

    return None


@login_required
def show_result(request):
    """
    Ejecuta el flujo:
    - Toma URL o texto de la sesión.
    - Extrae (o recibe) title/author/date/text.
    - Crea/Reusa Publisher y Article (normalización).
    - Llama a OpenAI para obtener score/explicación.
    - Guarda AnalyzedNews con FK al Article.
    """
    url = request.session.get('url', '')
    text = request.session.get('text', '')

    if url:
        try:
            title, author, date_str, article_text = _extract_article_from_url(url)
        except Exception as e:
            result = f"Could not get link content: {str(e)}"
            return render(request, 'ai_result.html', {'url': url, 'result': result})
    elif text:
        article_text = text.strip()[:4000] if len(text.strip()) > 4000 else text.strip()
        title = 'Provided directly'
        author = 'not available'
        date_str = 'not available'
    else:
        return redirect('verification:verify_link')

    idioma = getattr(request, "LANGUAGE_CODE", "en")
    if idioma == 'es':
        lang_instruction = "Responde en español."
    elif idioma == 'pt':
        lang_instruction = "Responda em português."
    else:
        lang_instruction = "Respond in English."

    prompt = f"""{lang_instruction}
        News Title: {title}
        Author: {author}
        Publication Date: {date_str}

        Analyze the following news story and return a credibility score from 1 to 100 based on:
        - Source reliability
        - Author
        - Date of the news story
        - Evidence presented in the text

        Assign a score from 1 to 25 to each of these, and a short explanation on why this scores.

        News Text:
        \"\"\"
        {article_text}
        \"\"\"

        Return the total score (1-100) and a brief explanation (maximum 3 sentences).
        """

    try:
        ai_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in news verification."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=500,
        )
        result = ai_response.choices[0].message.content.strip()
    except Exception as e:
        result = f"There was an error querying the OpenAI API: {str(e)}"

    score_match = re.search(
        r"(?:Total\s*Score|Score\s*total|Puntaje\s*total)[:\s]*([0-9]{1,3})",
        result,
        re.IGNORECASE
    )
    score = int(score_match.group(1)) if score_match else 0
    score = max(0, min(score, 100))

    publisher = _infer_publisher_from_url(url) if url else None
    published_at_dt = _parse_published_at(date_str)

    if url:
        article, _created = Article.objects.get_or_create(
            url=url,
            defaults={
                "publisher": publisher,
                "title": title or "not available",
                "author": author or "",
                "published_at": published_at_dt,
                "text": article_text,
            },
        )
        updated = False
        if not article.title and title:
            article.title = title; updated = True
        if (not article.author) and author and author != 'not available':
            article.author = author; updated = True
        if (not article.published_at) and published_at_dt:
            article.published_at = published_at_dt; updated = True
        if (not article.publisher) and publisher:
            article.publisher = publisher; updated = True
        if (not article.text) and article_text:
            article.text = article_text; updated = True
        if updated:
            article.save()
    else:
        article, _created = Article.objects.get_or_create(
            title=title or "Provided directly",
            author=author or "",
            text=article_text,
            published_at=published_at_dt,
            defaults={"publisher": publisher, "url": None},
        )

    AnalyzedNews.objects.create(
        user=request.user,
        article=article,
        score=score,
        explanation=result
    )

    return render(request, 'ai_result.html', {
        'url': article.url,
        'result': result,
        'title': article.title,
        'author': article.author or 'not available',
        'date': (article.published_at.strftime('%d %B %Y, %H:%M') if article.published_at else 'not available'),
        'text': article.text,
    })