# Search/urls.py
from django.urls import path
from .views import NewList, NewDetail, NewCreate, NewUpdate, NewDelete

app_name = "search"

urlpatterns = [
    path("news/", NewList.as_view(), name="news_list"),                 # GET /news/
    path("news/create/", NewCreate.as_view(), name="news_create"),      # GET/POST /news/create/
    path("news/<int:pk>/", NewDetail.as_view(), name="news_detail"),    # GET /news/1/
    path("news/<int:pk>/edit/", NewUpdate.as_view(), name="news_edit"), # GET/POST /news/1/edit/
    path("news/<int:pk>/delete/", NewDelete.as_view(), name="news_del") # POST/GET /news/1/delete/
]