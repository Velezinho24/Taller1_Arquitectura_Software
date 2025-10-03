from django.contrib import admin
from .models import Publisher, Article, AnalyzedNews
admin.site.register(Publisher)
admin.site.register(Article)
admin.site.register(AnalyzedNews)