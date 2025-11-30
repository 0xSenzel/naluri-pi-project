# Pi Calculation Service

A distributed system for calculating π to high precision and computing the circumference of the Sun, with real-time updates via Server-Sent Events (SSE).

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd naluri-pi-project
```

### 2. Backend Setup (Docker Recommended)

```bash
cd backend
docker-compose up --build
```

This will start:
- Redis on port 6379
- API server on port 8000
- Worker process (background)

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Accessing the Application

Once both services are running:

- **Frontend:** http://localhost:5173
- **API Documentation (Swagger UI):** http://localhost:8000/docs
- **Status Endpoint:** http://localhost:8000/status
- **SSE Stream Endpoint:** http://localhost:8000/pi-stream

## Project Structure

```
naluri-pi-project/
├── backend/           # FastAPI backend with Pi calculation
│   ├── src/
│   ├── docker-compose.yaml
│   ├── requirements.txt
│   └── README.md
├── frontend/          # React frontend for visualization
│   ├── src/
│   ├── package.json
│   └── README.md
└── README.md         # This file
```

## Documentation

- **[Backend Documentation](./backend/README.md)** - API endpoints, configuration, and local setup
- **[Frontend Documentation](./frontend/README.md)** - Frontend setup and build instructions
