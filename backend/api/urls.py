from django.urls import path
from .views import UploadCSV, SummaryAPI, HistoryAPI

urlpatterns = [
    path('upload/', UploadCSV.as_view()),
    path('summary/', SummaryAPI.as_view()),
    path('history/', HistoryAPI.as_view()),
]
