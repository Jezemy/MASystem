# coding=utf-8
from django.urls import path
from . import views

app_name = 'robot'
urlpatterns=[
	path('',views.indexPage),
	path('receiveMsg/',views.receiveMsg),
	path('receiveBtn/', views.receiveBtn),
	path('test/',views.getTest),
]