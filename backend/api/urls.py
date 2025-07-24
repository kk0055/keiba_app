from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AIPredictionViewSet, RaceDetailView

router = DefaultRouter()
router.register("predictions", AIPredictionViewSet, basename="prediction")

urlpatterns = [
    path("race/<str:race_id>/", RaceDetailView.as_view(), name="race-detail"),
]

urlpatterns += router.urls
