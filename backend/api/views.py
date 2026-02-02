from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import pandas as pd
import os
from django.conf import settings
from .models import Dataset


@method_decorator(csrf_exempt, name='dispatch')
class UploadCSV(APIView):
    """Upload CSV file - requires authentication"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        """Render a simple HTML form for file upload testing"""
        from django.http import HttpResponse
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Upload CSV</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 50px; }
                h1 { color: #333; }
                form { margin-top: 20px; }
                input[type="file"] { margin: 10px 0; }
                button { padding: 10px 20px; background: #4CAF50; color: white; border: none; cursor: pointer; }
                button:hover { background: #45a049; }
            </style>
        </head>
        <body>
            <h1>Upload CSV File</h1>
            <form method="POST" enctype="multipart/form-data">
                <input type="file" name="file" accept=".csv" required><br><br>
                <button type="submit">Upload</button>
            </form>
            <p>Required columns: Equipment Name, Type, Flowrate, Pressure, Temperature</p>
        </body>
        </html>
        '''
        return HttpResponse(html)

    def post(self, request):
        file = request.FILES.get('file')

        if not file:
            return Response(
                {"error": "No file uploaded"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Try reading CSV
        try:
            df = pd.read_csv(file)
        except Exception:
            return Response(
                {"error": "Invalid CSV file"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate required columns
        required_columns = [
            "Equipment Name",
            "Type",
            "Flowrate",
            "Pressure",
            "Temperature"
        ]

        for col in required_columns:
            if col not in df.columns:
                return Response(
                    {"error": f"Missing column: {col}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Save file to disk
        upload_dir = os.path.join(settings.BASE_DIR, "uploaded_files")
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, file.name)

        with open(file_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # Save file path to database
        Dataset.objects.create(file_name=file_path)

        return Response(
            {"message": "CSV uploaded successfully"},
            status=status.HTTP_200_OK
        )


class SummaryAPI(APIView):
    """
    GET /api/summary/
    Returns summary statistics from the latest uploaded CSV file.
    Output is formatted for easy use with Chart.js.
    Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Step 1: Get the latest uploaded dataset from the database
        dataset = Dataset.objects.order_by('-uploaded_at').first()

        # Check if any dataset exists
        if not dataset:
            return Response(
                {"error": "No dataset uploaded yet. Please upload a CSV file first."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Step 2: Try to read the CSV file
        try:
            df = pd.read_csv(dataset.file_name)
        except FileNotFoundError:
            return Response(
                {"error": "CSV file not found on server."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Error reading CSV file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Step 3: Calculate summary statistics
        total_rows = len(df)
        avg_flowrate = round(df["Flowrate"].mean(), 2)
        avg_pressure = round(df["Pressure"].mean(), 2)
        avg_temperature = round(df["Temperature"].mean(), 2)

        # Step 4: Count equipment per Type
        type_counts = df["Type"].value_counts().to_dict()

        # Step 5: Format response for Chart.js
        # Chart.js needs "labels" and "data" arrays for charts
        summary = {
            # Basic statistics
            "total_rows": total_rows,
            "averages": {
                "flowrate": avg_flowrate,
                "pressure": avg_pressure,
                "temperature": avg_temperature
            },

            # Bar chart data for averages (Chart.js format)
            "averages_chart": {
                "labels": ["Flowrate", "Pressure", "Temperature"],
                "datasets": [{
                    "label": "Average Values",
                    "data": [avg_flowrate, avg_pressure, avg_temperature],
                    "backgroundColor": [
                        "rgba(54, 162, 235, 0.6)",
                        "rgba(255, 99, 132, 0.6)",
                        "rgba(75, 192, 192, 0.6)"
                    ],
                    "borderColor": [
                        "rgba(54, 162, 235, 1)",
                        "rgba(255, 99, 132, 1)",
                        "rgba(75, 192, 192, 1)"
                    ],
                    "borderWidth": 1
                }]
            },

            # Pie/Doughnut chart data for equipment types (Chart.js format)
            "equipment_types_chart": {
                "labels": list(type_counts.keys()),
                "datasets": [{
                    "label": "Equipment Count",
                    "data": list(type_counts.values()),
                    "backgroundColor": [
                        "rgba(255, 99, 132, 0.6)",
                        "rgba(54, 162, 235, 0.6)",
                        "rgba(255, 206, 86, 0.6)",
                        "rgba(75, 192, 192, 0.6)",
                        "rgba(153, 102, 255, 0.6)",
                        "rgba(255, 159, 64, 0.6)"
                    ]
                }]
            },

            # Raw type counts for reference
            "equipment_type_counts": type_counts
        }

        return Response(summary, status=status.HTTP_200_OK)


class HistoryAPI(APIView):
    """
    GET /api/history/
    Returns the last 5 uploaded CSV datasets.
    Ordered by newest first.
    Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the last 5 datasets, ordered by newest first
        datasets = Dataset.objects.order_by('-uploaded_at')[:5]

        # Build the response list
        history = []
        for dataset in datasets:
            history.append({
                "file_name": dataset.file_name,
                "uploaded_at": dataset.uploaded_at.strftime("%B %d, %Y at %I:%M %p")
            })

        return Response({
            "count": len(history),
            "datasets": history
        }, status=status.HTTP_200_OK)
