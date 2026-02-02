from django.urls import path
from .views import RegisterAPI, UploadCSV, SummaryAPI, HistoryAPI, PDFReportAPIView

urlpatterns = [
    # Public endpoint (no auth required)
    path('register/', RegisterAPI.as_view()),
    
    # Protected endpoints (JWT auth required)
    path('upload/', UploadCSV.as_view()),
    path('summary/', SummaryAPI.as_view()),
    path('history/', HistoryAPI.as_view()),
    path('report/', PDFReportAPIView.as_view()),
]
