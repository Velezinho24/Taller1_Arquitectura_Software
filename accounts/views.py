from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Avg
from verification.models import AnalyzedNews
from .services.auth_service import AuthService


def signup_view(request):
    form = UserCreationForm()
    if request.method == 'GET':
        return render(request, 'signup.html', {'form': form})
    else:
        try:
            AuthService.signup(
                request,
                request.POST.get('username', ''),
                request.POST.get('password1', ''),
                request.POST.get('password2', '')
            )
            return redirect('search')
        except ValueError as e:
            return render(request, 'signup.html', {'form': form, 'error': str(e)})
        except IntegrityError as e:
            return render(request, 'signup.html', {'form': form, 'error': str(e)})


def login_view(request):
    form = AuthenticationForm()
    if request.method == 'GET':
        return render(request, 'login.html', {'form': form})
    else:
        user = AuthService.signin(
            request,
            request.POST.get('username', ''),
            request.POST.get('password', '')
        )
        if user is None:
            return render(
                request,
                'login.html',
                {'form': form, 'error': 'Username and password did not match'}
            )
        return redirect('search')


def logout_view(request):
    AuthService.signout(request)
    return redirect('search')


@login_required
def dashboard(request):
    """
    Muestra el historial de verificaciones del usuario.
    Ahora lee a través de la relación:
      AnalyzedNews -> Article (normalización de modelos)
    y optimiza consultas con select_related('article', 'article__publisher').
    """
    user_news = (
        AnalyzedNews.objects
        .filter(user=request.user)
        .select_related('article', 'article__publisher')
        .order_by('-created_at')
    )

    total_news = user_news.count()
    average_score = user_news.aggregate(avg_score=Avg('score'))['avg_score'] or 0
    average_score = round(average_score)

    context = {
        'news_list': user_news,
        'total_news': total_news,
        'average_score': average_score,
    }
    return render(request, 'dashboard.html', context)