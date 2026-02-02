from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
import pandas as pd
import os
import io
from datetime import datetime
from django.conf import settings
from .models import Dataset
from .serializers import UserRegistrationSerializer

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# Matplotlib for chart generation (non-interactive backend for server)
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for server-side rendering
import matplotlib.pyplot as plt


# ==================== USER REGISTRATION API ====================
@method_decorator(csrf_exempt, name='dispatch')
class RegisterAPI(APIView):
    """
    POST /api/register/
    Public endpoint for user registration.
    No authentication required.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """Register a new user account."""
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Registration successful! You can now sign in.",
                "username": user.username
            }, status=status.HTTP_201_CREATED)
        
        # Return validation errors
        return Response({
            "error": self._format_errors(serializer.errors)
        }, status=status.HTTP_400_BAD_REQUEST)

    def _format_errors(self, errors):
        """Format serializer errors into a single message."""
        messages = []
        for field, error_list in errors.items():
            for error in error_list:
                if field == 'non_field_errors':
                    messages.append(str(error))
                else:
                    messages.append(f"{field}: {error}")
        return " | ".join(messages) if messages else "Validation failed."


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
                "uploaded_at": dataset.uploaded_at.isoformat()
            })

        return Response({
            "count": len(history),
            "datasets": history
        }, status=status.HTTP_200_OK)

    def delete(self, request):
        """Delete all upload history."""
        # Delete all uploaded files from disk
        datasets = Dataset.objects.all()
        for dataset in datasets:
            try:
                if os.path.exists(dataset.file_name):
                    os.remove(dataset.file_name)
            except Exception:
                pass  # Continue even if file deletion fails

        # Delete all records from database
        Dataset.objects.all().delete()

        return Response({
            "message": "All history cleared successfully"
        }, status=status.HTTP_200_OK)


class PDFReportAPIView(APIView):
    """
    GET /api/report/
    Generates and returns a professional PDF report with summary statistics and charts.
    Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    def _generate_averages_chart(self, avg_flowrate, avg_pressure, avg_temperature):
        """
        Generate a bar chart showing average parameter values.
        Returns an in-memory image buffer.
        """
        # Create figure with specific size for PDF
        fig, ax = plt.subplots(figsize=(6, 3.5), dpi=150)
        
        # Data
        parameters = ['Flowrate\n(L/min)', 'Pressure\n(bar)', 'Temperature\n(°C)']
        values = [avg_flowrate, avg_pressure, avg_temperature]
        bar_colors = ['#3b82f6', '#f59e0b', '#10b981']  # Blue, Orange, Green
        
        # Create bars
        bars = ax.bar(parameters, values, color=bar_colors, width=0.6, edgecolor='white', linewidth=1.5)
        
        # Add value labels on top of bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.annotate(f'{value}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 5),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize=11, fontweight='bold', color='#2c3e50')
        
        # Styling
        ax.set_ylabel('Average Value', fontsize=11, fontweight='bold', color='#2c3e50')
        ax.set_title('Average Parameter Values', fontsize=14, fontweight='bold', color='#1e3a5f', pad=15)
        ax.set_facecolor('#f8fafc')
        fig.patch.set_facecolor('#ffffff')
        
        # Remove top and right spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#bdc3c7')
        ax.spines['bottom'].set_color('#bdc3c7')
        
        # Grid
        ax.yaxis.grid(True, linestyle='--', alpha=0.7, color='#e0e0e0')
        ax.set_axisbelow(True)
        
        # Tick styling
        ax.tick_params(axis='x', labelsize=10, colors='#475569')
        ax.tick_params(axis='y', labelsize=9, colors='#475569')
        
        plt.tight_layout()
        
        # Save to in-memory buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close(fig)  # Close figure to free memory
        img_buffer.seek(0)
        
        return img_buffer

    def _generate_distribution_chart(self, type_counts, total_rows):
        """
        Generate a pie chart showing equipment type distribution.
        Returns an in-memory image buffer.
        """
        # Create figure with specific size for PDF
        fig, ax = plt.subplots(figsize=(5, 4), dpi=150)
        
        # Data
        labels = list(type_counts.keys())
        sizes = list(type_counts.values())
        
        # Professional color palette
        chart_colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16']
        colors_to_use = chart_colors[:len(labels)]
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            sizes, 
            labels=labels,
            autopct=lambda pct: f'{pct:.1f}%' if pct > 5 else '',
            colors=colors_to_use,
            startangle=90,
            explode=[0.02] * len(labels),  # Slight separation between wedges
            shadow=False,
            wedgeprops={'edgecolor': 'white', 'linewidth': 2}
        )
        
        # Style the percentage labels
        for autotext in autotexts:
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')
            autotext.set_color('white')
        
        # Style the labels
        for text in texts:
            text.set_fontsize(9)
            text.set_color('#2c3e50')
        
        # Title
        ax.set_title('Equipment Type Distribution', fontsize=14, fontweight='bold', color='#1e3a5f', pad=15)
        
        # Equal aspect ratio ensures pie is circular
        ax.axis('equal')
        
        fig.patch.set_facecolor('#ffffff')
        plt.tight_layout()
        
        # Save to in-memory buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close(fig)  # Close figure to free memory
        img_buffer.seek(0)
        
        return img_buffer

    def get(self, request):
        # Get the latest dataset
        dataset = Dataset.objects.order_by('-uploaded_at').first()

        if not dataset:
            return Response(
                {"error": "No dataset uploaded yet. Please upload a CSV file first."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Read the CSV file
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

        # ==================== CALCULATE STATISTICS ====================
        total_rows = len(df)
        avg_flowrate = round(df["Flowrate"].mean(), 2)
        avg_pressure = round(df["Pressure"].mean(), 2)
        avg_temperature = round(df["Temperature"].mean(), 2)
        
        # Additional statistics for professional report
        min_flowrate = round(df["Flowrate"].min(), 2)
        max_flowrate = round(df["Flowrate"].max(), 2)
        min_pressure = round(df["Pressure"].min(), 2)
        max_pressure = round(df["Pressure"].max(), 2)
        min_temperature = round(df["Temperature"].min(), 2)
        max_temperature = round(df["Temperature"].max(), 2)
        
        type_counts = df["Type"].value_counts().to_dict()

        # ==================== CREATE PDF ====================
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter, 
            topMargin=0.5*inch, 
            bottomMargin=0.5*inch,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch
        )
        elements = []
        styles = getSampleStyleSheet()

        # ==================== CUSTOM STYLES ====================
        # Main title style
        title_style = ParagraphStyle(
            'MainTitle',
            parent=styles['Heading1'],
            fontSize=26,
            spaceAfter=6,
            textColor=colors.HexColor('#1e3a5f'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Subtitle style
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=4,
            textColor=colors.HexColor('#5a6c7d'),
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        # Date/time style
        datetime_style = ParagraphStyle(
            'DateTime',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=20,
            textColor=colors.HexColor('#7f8c8d'),
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        )
        
        # Section heading style
        section_heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceBefore=16,
            spaceAfter=10,
            textColor=colors.HexColor('#1e3a5f'),
            fontName='Helvetica-Bold',
            borderPadding=(0, 0, 4, 0)
        )
        
        # Footer style
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#95a5a6'),
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        )

        # ==================== HEADER SECTION ====================
        elements.append(Paragraph("CHEMICAL EQUIPMENT", title_style))
        elements.append(Paragraph("ANALYSIS REPORT", title_style))
        elements.append(Spacer(1, 8))
        elements.append(Paragraph("Chemical Equipment Parameter Visualizer", subtitle_style))
        elements.append(Spacer(1, 4))
        
        # Horizontal divider line
        elements.append(HRFlowable(
            width="80%", 
            thickness=2, 
            color=colors.HexColor('#3498db'),
            spaceAfter=8,
            spaceBefore=8
        ))
        
        # Generation timestamp (IST)
        from datetime import timezone, timedelta
        ist = timezone(timedelta(hours=5, minutes=30))
        generated_time = datetime.now(ist).strftime("%d %B %Y at %I:%M %p IST")
        elements.append(Paragraph(f"Report Generated: {generated_time}", datetime_style))
        elements.append(Spacer(1, 12))

        # ==================== OVERVIEW SECTION ====================
        elements.append(Paragraph("📊 Overview", section_heading_style))
        
        overview_data = [
            ["Total Equipment Records", str(total_rows)],
            ["Equipment Types Analyzed", str(len(type_counts))],
            ["Data Source", os.path.basename(dataset.file_name)],
        ]
        
        overview_table = Table(overview_data, colWidths=[3.5*inch, 3*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
            ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#ffffff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
            ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#eeeeee')),
        ]))
        elements.append(overview_table)
        elements.append(Spacer(1, 16))

        # ==================== PARAMETER STATISTICS SECTION ====================
        elements.append(Paragraph("📈 Parameter Statistics", section_heading_style))
        
        stats_data = [
            ["Parameter", "Average", "Minimum", "Maximum"],
            ["Flowrate (L/min)", f"{avg_flowrate}", f"{min_flowrate}", f"{max_flowrate}"],
            ["Pressure (bar)", f"{avg_pressure}", f"{min_pressure}", f"{max_pressure}"],
            ["Temperature (°C)", f"{avg_temperature}", f"{min_temperature}", f"{max_temperature}"],
        ]
        
        stats_table = Table(stats_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        stats_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            # Data rows
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#e3f2fd')),
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#fff8e1')),
            ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#e8f5e9')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2c3e50')),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            # Borders
            ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#1e3a5f')),
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#1e3a5f')),
            ('LINEBELOW', (0, 1), (-1, -2), 0.5, colors.HexColor('#bdc3c7')),
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 20))

        # ==================== CHARTS SECTION ====================
        elements.append(Paragraph("📊 Visual Analytics", section_heading_style))
        elements.append(Spacer(1, 8))
        
        # Generate Average Values Bar Chart
        try:
            avg_chart_buffer = self._generate_averages_chart(avg_flowrate, avg_pressure, avg_temperature)
            avg_chart_img = Image(avg_chart_buffer, width=5.5*inch, height=3*inch)
            elements.append(avg_chart_img)
        except Exception as e:
            # Fallback if chart generation fails
            elements.append(Paragraph(f"[Chart could not be generated: {str(e)}]", styles['Normal']))
        
        elements.append(Spacer(1, 16))
        
        # Generate Equipment Distribution Pie Chart
        try:
            dist_chart_buffer = self._generate_distribution_chart(type_counts, total_rows)
            dist_chart_img = Image(dist_chart_buffer, width=4.5*inch, height=3.5*inch)
            # Center the pie chart using a table
            chart_table = Table([[dist_chart_img]], colWidths=[7*inch])
            chart_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
            elements.append(chart_table)
        except Exception as e:
            # Fallback if chart generation fails
            elements.append(Paragraph(f"[Chart could not be generated: {str(e)}]", styles['Normal']))
        
        elements.append(Spacer(1, 20))

        # ==================== EQUIPMENT DISTRIBUTION TABLE SECTION ====================
        elements.append(Paragraph("🔧 Equipment Type Distribution", section_heading_style))
        
        # Calculate percentage for each type
        type_data = [["Equipment Type", "Count", "Percentage"]]
        for eq_type, count in type_counts.items():
            percentage = round((count / total_rows) * 100, 1)
            type_data.append([str(eq_type), str(count), f"{percentage}%"])
        
        type_table = Table(type_data, colWidths=[3*inch, 1.75*inch, 1.75*inch])
        type_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            # Data rows - alternating colors
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2c3e50')),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            # Borders
            ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#27ae60')),
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#27ae60')),
            ('LINEBELOW', (0, 1), (-1, -2), 0.5, colors.HexColor('#bdc3c7')),
        ]))
        
        # Alternating row colors for data rows
        for i in range(1, len(type_data)):
            bg_color = colors.HexColor('#f8f9fa') if i % 2 == 0 else colors.HexColor('#ffffff')
            type_table.setStyle(TableStyle([('BACKGROUND', (0, i), (-1, i), bg_color)]))
        
        elements.append(type_table)
        elements.append(Spacer(1, 24))

        # ==================== FOOTER SECTION ====================
        elements.append(HRFlowable(
            width="100%", 
            thickness=1, 
            color=colors.HexColor('#e0e0e0'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        elements.append(Paragraph(
            "Chemical Equipment Parameter Visualizer | Internship Project Report",
            footer_style
        ))
        elements.append(Paragraph(
            "Generated automatically from uploaded CSV data",
            footer_style
        ))

        # ==================== BUILD PDF ====================
        doc.build(elements)

        # Return PDF response
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="chemical_equipment_report.pdf"'
        return response
