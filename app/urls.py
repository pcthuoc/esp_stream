# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django.urls import path, re_path
from app import views
from app.views import AudioListView


urlpatterns = [

    # The home page
    path('', views.home, name='home'),
    path('listfile/', AudioListView.as_view(), name='list_file'),
    path('download/<str:filename>/', views.download_audio, name='download_audio'),
    path('delete/<str:filename>/', views.delete_audio, name='delete_audio'),
    path('upload/', views.upload_audio, name='upload'),
    path('steam/', views.stream_audio, name='stream'),
    path('rawdata/', views.receive_audio, name='receive_audio'),

]
