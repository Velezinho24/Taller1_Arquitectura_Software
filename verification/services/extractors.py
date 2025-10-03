import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Tuple
from .interfaces import NewsExtractor

class WebNewsExtractor(NewsExtractor):
    """Implementación concreta para extraer noticias de páginas web"""
    
    def extract_content(self, url: str) -> Tuple[str, str, str, str]:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extraer texto del artículo
        paragraphs = soup.find_all('p')
        article_text = ' '.join(p.get_text() for p in paragraphs).strip()
        if len(article_text) > 4000:
            article_text = article_text[:4000]

        # Extraer título
        title = soup.title.string.strip() if soup.title else 'not available'

        # Extraer autor
        author = self._extract_author(soup)

        # Extraer fecha
        date = self._extract_date(soup)

        return article_text, title, author, date

    def _extract_author(self, soup: BeautifulSoup) -> str:
        author_meta = soup.find('meta', attrs={'name': 'author'}) or \
                     soup.find('meta', attrs={'property': 'article:author'})
        if author_meta:
            return author_meta.get('content', 'not available')
        
        author_tag = soup.find(attrs={'class': lambda x: x and 'author' in x.lower()})
        return author_tag.get_text().strip() if author_tag else 'not available'

    def _extract_date(self, soup: BeautifulSoup) -> str:
        date_meta = soup.find('meta', attrs={'property': 'article:published_time'}) or \
                   soup.find('meta', attrs={'name': 'date'})
        if date_meta:
            date = date_meta.get('content', None)
        else:
            time_tag = soup.find('time')
            if time_tag and time_tag.get('datetime'):
                date = time_tag['datetime']
            elif time_tag:
                date = time_tag.get_text().strip()
            else:
                return 'not available'

        try:
            parsed_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
            return parsed_date.strftime('%d %B %Y, %H:%M')
        except ValueError:
            return date