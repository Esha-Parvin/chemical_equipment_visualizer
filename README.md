# Chemical Equipment Parameter Visualizer

A hybrid data visualization application for analyzing chemical equipment parameters, available as both a **Web Application** (React + Chart.js) and a **Desktop Application** (PyQt5 + Matplotlib). Both frontends consume a shared Django REST API backend.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
  - [Backend Setup](#backend-setup)
  - [Web Frontend Setup](#web-frontend-setup)
  - [Desktop Frontend Setup](#desktop-frontend-setup)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Authentication Flow](#authentication-flow)
- [Sample CSV Format](#sample-csv-format)
- [Screenshots](#screenshots)
- [Author](#author)

---

## Overview

This project enables users to upload CSV files containing chemical equipment data, automatically parse and analyze the data using Pandas, visualize key metrics through interactive charts, and maintain a history of uploaded datasets. The application features JWT-based authentication to secure all endpoints and supports both browser-based and native desktop access.

---

## Features

- **CSV File Upload** — Upload equipment data from both Web and Desktop interfaces
- **Automated Data Parsing** — Backend processes CSV files using Pandas for analytics
- **Summary Statistics** — View total record count, average capacity, average pressure
- **Equipment Distribution Charts** — Bar and Pie charts showing equipment type breakdown
- **Upload History** — Track the last 5 uploaded datasets with metadata
- **JWT Authentication** — Secure login required for all protected endpoints
- **Responsive Web UI** — Mobile-friendly React interface with modern styling
- **Desktop Application** — Native Windows/macOS/Linux app with Matplotlib visualizations

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend (Web)** | React.js, Chart.js, Axios, React Router |
| **Frontend (Desktop)** | PyQt5, Matplotlib, Requests |
| **Backend** | Django, Django REST Framework |
| **Data Processing** | Pandas |
| **Database** | SQLite |
| **Authentication** | Django REST Framework SimpleJWT |
| **Version Control** | Git & GitHub |

---

## Project Structure

```
chemical-equipment-visualizer/
│
├── README.md                          # Project documentation (this file)
│
├── backend/                           # Django REST API Backend
│   ├── manage.py                      # Django management script
│   ├── db.sqlite3                     # SQLite database file
│   │
│   ├── api/                           # Main API application
│   │   ├── __init__.py
│   │   ├── admin.py                   # Django admin configuration
│   │   ├── apps.py                    # App configuration
│   │   ├── models.py                  # Database models (Dataset)
│   │   ├── views.py                   # API views (Upload, Summary, History)
│   │   ├── urls.py                    # API URL routing
│   │   ├── tests.py                   # Unit tests
│   │   └── migrations/                # Database migrations
│   │       ├── __init__.py
│   │       └── 0001_initial.py
│   │
│   ├── chemical_api/                  # Django project settings
│   │   ├── __init__.py
│   │   ├── settings.py                # Project settings (JWT, CORS, etc.)
│   │   ├── urls.py                    # Root URL configuration
│   │   ├── wsgi.py                    # WSGI entry point
│   │   └── asgi.py                    # ASGI entry point
│   │
│   └── uploaded_files/                # Uploaded CSV file storage
│       └── sample_equipment_data.csv
│
├── frontend/                          # React Web Frontend
│   ├── package.json                   # Node.js dependencies
│   ├── package-lock.json
│   │
│   ├── public/                        # Static public assets
│   │   ├── index.html
│   │   ├── favicon.ico
│   │   └── manifest.json
│   │
│   └── src/                           # React source code
│       ├── index.js                   # React entry point
│       ├── index.css                  # Global styles
│       ├── App.js                     # Main App component with routing
│       ├── App.css                    # App styles
│       ├── api.js                     # Axios instance with JWT interceptors
│       ├── Login.js                   # Login page component
│       ├── Login.css                  # Login page styles
│       ├── Dashboard.jsx              # Main dashboard component
│       ├── Dashboard.css              # Dashboard styles
│       └── ProtectedRoute.jsx         # Route guard for authentication
│
└── desktop-frontend/                  # PyQt5 Desktop Application
    ├── main.py                        # Application entry point
    ├── api.py                         # API client with JWT handling
    ├── login.py                       # Login window UI
    ├── dashboard.py                   # Dashboard window UI
    └── app.py                         # Legacy/standalone app
```

---

## Setup Instructions

### Prerequisites

Ensure you have the following installed:

- **Python 3.10+** — [Download Python](https://www.python.org/downloads/)
- **Node.js 18+** — [Download Node.js](https://nodejs.org/)
- **Git** — [Download Git](https://git-scm.com/)

---

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install django djangorestframework djangorestframework-simplejwt pandas django-cors-headers
   ```

4. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser account:**
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to set username, email, and password.

6. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

   The API will be available at: `http://127.0.0.1:8000`

---

### Web Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

   The web application will be available at: `http://localhost:3000`

---

### Desktop Frontend Setup

1. **Navigate to the desktop-frontend directory:**
   ```bash
   cd desktop-frontend
   ```

2. **Install Python dependencies:**
   ```bash
   pip install PyQt5 matplotlib requests
   ```

3. **Run the desktop application:**
   ```bash
   python main.py
   ```

   The login window will appear. Use your Django superuser credentials to log in.

---

## Running the Application

### Quick Start (All Components)

Open three separate terminal windows and run:

**Terminal 1 — Backend:**
```bash
cd backend
venv\Scripts\activate    # Windows
python manage.py runserver
```

**Terminal 2 — Web Frontend:**
```bash
cd frontend
npm start
```

**Terminal 3 — Desktop Frontend:**
```bash
cd desktop-frontend
python main.py
```

### Access Points

| Application | URL / Method |
|-------------|--------------|
| Backend API | http://127.0.0.1:8000 |
| Web Frontend | http://localhost:3000 |
| Desktop App | Run `python main.py` |
| Django Admin | http://127.0.0.1:8000/admin |

---

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/token/` | Obtain JWT access and refresh tokens | No |
| `POST` | `/api/token/refresh/` | Refresh expired access token | No |
| `POST` | `/api/upload/` | Upload CSV file for processing | Yes |
| `GET` | `/api/summary/` | Get analytics summary of latest dataset | Yes |
| `GET` | `/api/history/` | Get list of last 5 uploaded datasets | Yes |

### Example: Get Summary Response

```json
{
  "total_rows": 150,
  "average_capacity_liters": 245.8,
  "average_max_pressure_bar": 12.4,
  "equipment_type_counts": {
    "Reactor": 45,
    "Storage Tank": 38,
    "Heat Exchanger": 32,
    "Distillation Column": 20,
    "Pump": 15
  }
}
```

---

## Authentication Flow

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Client    │         │   Backend   │         │  Database   │
└──────┬──────┘         └──────┬──────┘         └──────┬──────┘
       │                       │                       │
       │  POST /api/token/     │                       │
       │  {username, password} │                       │
       │──────────────────────>│                       │
       │                       │  Validate credentials │
       │                       │──────────────────────>│
       │                       │<──────────────────────│
       │  {access, refresh}    │                       │
       │<──────────────────────│                       │
       │                       │                       │
       │  GET /api/summary/    │                       │
       │  Authorization: Bearer│                       │
       │──────────────────────>│                       │
       │                       │  Verify JWT token     │
       │  {summary data}       │                       │
       │<──────────────────────│                       │
       │                       │                       │
```

- **Access Token:** Valid for 30 minutes
- **Refresh Token:** Valid for 1 day

---

## Sample CSV Format

The application expects CSV files with the following structure:

```csv
Equipment_ID,Name,Type,Capacity_Liters,Max_Pressure_Bar,Installation_Date,Status
EQ001,Reactor Alpha,Reactor,500,15.5,2023-01-15,Active
EQ002,Storage Tank B,Storage Tank,1000,8.0,2022-06-20,Active
EQ003,Heat Exchanger C,Heat Exchanger,250,12.0,2023-03-10,Maintenance
EQ004,Distillation Unit D,Distillation Column,750,18.5,2021-11-05,Active
EQ005,Transfer Pump E,Pump,50,25.0,2024-02-28,Active
```

### Required Columns

| Column | Type | Description |
|--------|------|-------------|
| `Equipment_ID` | String | Unique identifier |
| `Name` | String | Equipment name |
| `Type` | String | Equipment category |
| `Capacity_Liters` | Number | Capacity in liters |
| `Max_Pressure_Bar` | Number | Maximum pressure rating |

---

## Screenshots

### Web Application

| Login Page | Dashboard |
|------------|-----------|
| ![Web Login](screenshots/web-login.png) | ![Web Dashboard](screenshots/web-dashboard.png) |

### Desktop Application

| Login Window | Dashboard Window |
|--------------|------------------|
| ![Desktop Login](screenshots/desktop-login.png) | ![Desktop Dashboard](screenshots/desktop-dashboard.png) |

> **Note:** Create a `screenshots/` folder and add actual screenshots before final submission.

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| CORS errors in browser | Ensure `django-cors-headers` is installed and configured |
| "Cannot connect to server" | Make sure Django backend is running on port 8000 |
| PyQt5 not found | Run `pip install PyQt5` in the correct virtual environment |
| JWT token expired | Login again or implement token refresh |

---

## Author

**[Your Name]**

- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

---

## License

This project is licensed under the MIT License.

---

*Last Updated: February 2026*
