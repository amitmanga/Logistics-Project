# Logistics Planning Tool

React + Flask logistics planning control tower for UK utility field operations.

## What It Includes

- React enterprise dashboard with left navigation, top filters, KPI cards, charts, map, alerts, AI recommendations, scenario simulation, and agent workflows.
- Flask backend with Python calculation logic and REST APIs.
- Simulated datasets in `datasets/` as both JSON and CSV.
- Recharts for dashboard visuals.
- React Leaflet for the UK logistics network map.
- Rule-based and ML-style simulated AI agents for SLA risk, route optimization, inventory risk, supplier risk, carrier allocation, cost optimization, shipment visibility, and engineer parts availability.

## Project Structure

```text
backend/
  agents.py
  app.py
  data_generator.py
  data_service.py
  planner.py
datasets/
  *.csv
  *.json
frontend/
  src/
    main.jsx
    styles.css
  package.json
  vite.config.js
requirements.txt
```

## Backend APIs

- `GET /api/overview`
- `GET /api/demand`
- `GET /api/inventory`
- `GET /api/shipments`
- `GET /api/wms-events`
- `GET /api/routes`
- `GET /api/transport-cost`
- `GET /api/suppliers`
- `GET /api/carriers`
- `GET /api/sla-risk`
- `GET /api/engineer-parts`
- `GET /api/ai-recommendations`
- `POST /api/scenario-simulation`
- `GET /api/agent/delivery-risk`
- `GET /api/agent/route-optimization`
- `GET /api/agent/inventory-risk`
- `GET /api/agent/carrier-allocation`
- `GET /api/agent/supplier-risk`

## Setup

Install Python dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Install frontend dependencies:

```bash
cd frontend
npm install
```

Regenerate simulated datasets if needed:

```bash
python3 backend/data_generator.py
```

## Run In Development

Start Flask:

```bash
flask --app backend.app run --host 127.0.0.1 --port 5001
```

Start React:

```bash
cd frontend
npm run dev
```

Open `http://127.0.0.1:5173`.

## Production-Style Run

Build React:

```bash
cd frontend
npm run build
```

Serve built React app through Flask:

```bash
flask --app backend.app run --host 127.0.0.1 --port 5001
```

Open `http://127.0.0.1:5001`.
