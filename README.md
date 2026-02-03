# Chemical Equipment Parameter Visualizer (Hybrid Web + Desktop)

A hybrid application for data visualization and analytics of chemical equipment. Upload CSV files with columns **Equipment Name**, **Type**, **Flowrate**, **Pressure**, and **Temperature**. The Django backend parses data with Pandas, stores the last 5 datasets in SQLite, and exposes a REST API. Both a **React (Web)** and **PyQt5 (Desktop)** frontend consume this API to show tables, charts, summaries, and PDF reports.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python Django + Django REST Framework |
| Data | Pandas, SQLite |
| Web Frontend | React.js + Chart.js |
| Desktop Frontend | PyQt5 + Matplotlib |
| PDF Reports | ReportLab |
| Auth | Basic Authentication (optional) |

## Project Structure

```
fossee/
├── backend/                    # Django project
│   ├── equipment_api/         # REST API app (upload, summary, history, PDF)
│   ├── equipment_visualizer/   # Django settings
│   ├── manage.py
│   └── requirements.txt
├── frontend_web/               # React app (Chart.js)
│   ├── src/
│   └── package.json
├── frontend_desktop/           # PyQt5 + Matplotlib
│   ├── main.py
│   ├── api_client.py
│   └── requirements.txt
├── sample_equipment_data.csv   # Sample CSV for demo
├── README.md
└── .gitignore
```

## Quick Start

### 1. Backend (Django)

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

API base: **http://127.0.0.1:8000/api/**

Optional: create a superuser for Basic Auth and admin:

```bash
python manage.py createsuperuser
```

### 2. Web Frontend (React)

```bash
cd frontend_web
npm install
npm start
```

Uses proxy to `http://127.0.0.1:8000`. Open **http://localhost:3000**.

### 3. Desktop Frontend (PyQt5)

Ensure the Django server is running, then:

```bash
cd frontend_desktop
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
python main.py
```

## Features

- **CSV Upload** — Web and Desktop: upload CSV with Equipment Name, Type, Flowrate, Pressure, Temperature.
- **Data Summary API** — Total count, averages (flowrate, pressure, temperature), equipment type distribution.
- **Visualization** — Chart.js (Web): doughnut + bar charts; Matplotlib (Desktop): pie + bar charts.
- **History** — Last 5 uploaded datasets stored in SQLite; both UIs show history and switch between datasets.
- **PDF Report** — Download a PDF report per dataset (summary + type distribution + data table sample).
- **Basic Authentication** — Optional; Web has an “Basic Auth” modal; Desktop has “Basic Auth” dialog. Backend supports Session + Basic auth.

## Sample Data

Use **sample_equipment_data.csv** in the project root for testing. Columns: Equipment Name, Type, Flowrate, Pressure, Temperature.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload/` | Upload CSV (multipart `file`, optional `name`) |
| GET | `/api/summary/<id>/` | Get summary for dataset |
| GET | `/api/history/` | List last 5 datasets |
| GET | `/api/report/<id>/pdf/` | Download PDF report |


"# fossee-webBasedApp" 
