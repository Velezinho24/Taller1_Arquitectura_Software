# Search/views.py
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
import requests
import os
from dotenv import load_dotenv
from django.contrib.auth.decorators import login_required
from verification.models import AnalyzedNews
from .models import New

load_dotenv('./API.env')

def search_view(request):
    query = request.GET.get('q', '')
    return render(request, 'search.html', {'query': query})


def search(request):
    return render(request, 'about.html')


def news_search(request):
    """
    Búsqueda por headline O url (antes se sobreescribía el queryset).
    """
    searchTerm = request.GET.get('searchNew', '').strip()
    if searchTerm:
        news = New.objects.filter(
            Q(headline__icontains=searchTerm) | Q(url__icontains=searchTerm)
        ).order_by('-date')
    else:
        news = New.objects.all().order_by('-date')

    return render(
        request,
        'search_results.html',
        {'searchTerm': searchTerm, 'name': 'Santiago', 'news': news}
    )


def loading_view(request):
    query = request.GET.get("verifyNew", "").strip()

    if query:
        api_key = os.environ.get("google_apikey")
        api_url = (
            "https://factchecktools.googleapis.com/v1alpha1/claims:search"
            f"?query={query}&key={api_key}&languageCode=es&languageCode=en&languageCode=pt"
        )

        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            print(f"Respuesta de la API: {data}")
        else:
            data = {"error": f"Error calling the API: {response.status_code} - {response.text}"}
            print(data)

        return render(request, "results.html", {"query": query, "results": data.get("claims", [])})

    return render(request, "results.html", {"query": query, "results": None})


def home_view(request):
    user_verifications = AnalyzedNews.objects.order_by('-created_at')[:5]
    api_key = os.environ.get("google_apikey")
    latest_news = []

    if api_key:
        api_url = (
            "https://factchecktools.googleapis.com/v1alpha1/claims:search"
            f"?key={api_key}&query=news&languageCode=es&languageCode=en&languageCode=pt&pageSize=5"
        )

        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            print(f"API Answer: {data}")
            latest_news = data.get("claims", [])
        else:
            print(f"Error: {response.status_code} - {response.text}")
            latest_news = []
    else:
        print("API key not found in environment variables.")

    return render(request, 'home.html', {
        'authenticated': request.user.is_authenticated,
        'user': request.user,
        'latest_news': latest_news,
        'user_verifications': user_verifications,
        'news_pairs': zip(latest_news, user_verifications)
    })

class NewList(ListView):
    """
    Lista de noticias (CRUD - Read).
    Uso de Generic ListView para reducir boilerplate y estandarizar vistas.
    """
    model = New
    template_name = "search/new_list.html"
    context_object_name = "news"
    paginate_by = 10
    ordering = ["-date"]


class NewDetail(DetailView):
    """
    Detalle de una noticia.
    """
    model = New
    template_name = "search/new_detail.html"
    context_object_name = "new"


class NewCreate(LoginRequiredMixin, CreateView):
    """
    Crear noticia (CRUD - Create).
    Requiere login para mantener trazabilidad.
    """
    model = New
    fields = ["headline", "body", "url", "credibility_score"]
    template_name = "search/new_form.html"
    success_url = reverse_lazy("search:news_list")
    login_url = reverse_lazy("login")


class NewUpdate(LoginRequiredMixin, UpdateView):
    """
    Editar noticia (CRUD - Update).
    """
    model = New
    fields = ["headline", "body", "url", "credibility_score"]
    template_name = "search/new_form.html"
    success_url = reverse_lazy("search:news_list")
    login_url = reverse_lazy("login")


class NewDelete(LoginRequiredMixin, DeleteView):
    """
    Eliminar noticia (CRUD - Delete).
    """
    model = New
    template_name = "search/new_confirm_delete.html"
    success_url = reverse_lazy("search:news_list")
    login_url = reverse_lazy("login")