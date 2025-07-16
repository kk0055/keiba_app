from django.urls import path
from .views import RaceDetailView

urlpatterns = [
    path("races/<str:race_id>/", RaceDetailView.as_view(), name="race-detail"),
]
