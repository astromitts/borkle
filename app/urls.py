from django.urls import path

from farkle import views

urlpatterns = [
    path('', views.Start.as_view(), name='new_game'),
    path('play/', views.PlayGame.as_view(), name='play_game'),
    path('roll/', views.Roll.as_view(), name='roll_dice'),
    path('checkselection/', views.CheckSelection.as_view(), name='check_selection'),
    path('makeselection/', views.MakeSelection.as_view(), name='make_selection'),
    path('undoselection/<int:selection_id>/', views.UndoSelection.as_view(), name='undo_selection'),
    path('history/', views.History.as_view(), name='history'),
    path('winner/', views.PreviewWinner.as_view(), name='winner')
]
