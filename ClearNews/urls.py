"""
URL configuration for ClearNews project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns, set_language
from Search.views import search_view, news_search, loading_view, search, home_view

urlpatterns = [
    path('i18n/setlang/', set_language, name='set_language'),
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('search/', search_view, name='search'),
    path('loading/', loading_view, name='loading_view'),
    path('searchloged/', search, name='searchloged'),
    path('accounts/', include('accounts.urls')),
    path('verification/', include('verification.urls')),
    path('', include(('Search.urls', 'search'), namespace='search')),
]
