from django.urls import path
from .views import RaceDetailView

urlpatterns = [
    path("race/<str:race_id>/", RaceDetailView.as_view(), name="race-detail"),
]
