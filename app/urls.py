"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path

from farkle import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('start/', views.Start.as_view(), name='new_game'),
    path('play/', views.PlayGame.as_view(), name='play_game'),
    path('roll/', views.Roll.as_view(), name='roll_dice'),
    path('checkselection/', views.CheckSelection.as_view(), name='check_selection'),
    path('makeselection/', views.MakeSelection.as_view(), name='make_selection'),
    path('history/', views.History.as_view(), name='history'),
    path('winner/', views.PreviewWinner.as_view(), name='winner')
]
