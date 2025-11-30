# Pi Calculation Service

A distributed system for calculating π to high precision and computing the circumference of the Sun, with real-time updates via Server-Sent Events (SSE).

## Project Structure

```
naluri-pi-project/
├── src/
│   ├── api/              # FastAPI routes and services
│   ├── calculation/      # Pi calculation algorithms
│   ├── config.py         # Configuration constants
│   ├── main.py           # FastAPI application entry point
│   └── worker.py         # Background worker for pi calculation
├── docker-compose.yaml   # Docker Compose configuration
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Getting Started

### Prerequisites

1. **Python 3.13+** (or compatible version)
2. **Redis** - Must be running on port 6379 (for local development)
3. **Docker & Docker Compose** (optional, for containerized setup)

### Step 1: Set Up Virtual Environment

**On macOS/Linux:**
```bash
# Create a new virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**On Windows:**
```bash
# Create a new virtual environment
python -m venv venv

# Activate it (Command Prompt)
venv\Scripts\activate

# Or (PowerShell)
venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

When activated, you'll see `(venv)` at the beginning of your terminal prompt.

**To deactivate:**
```bash
deactivate
```

### Step 2: Configure Redis (Local Development Only)

Edit `src/config.py` and set `REDIS_HOST = 'localhost'` for local development, or set to `'redis'` in run with docker:

## Running the Application

### Option 1: Run Locally with Worker Only

Start the worker to calculate Pi digits:

```bash
source venv/bin/activate  # macOS/Linux

docker-compose up -d redis

python -m src.worker
```

This will start the Pi calculation worker and store results in Redis.

### Option 3: Run with Docker Compose

```bash
docker-compose up --build
```

This will start:
- Redis on port 6379
- API server on port 8000
- Worker process (background)

## Accessing the API

Once running, you can access:

- **API Documentation (Swagger UI):** http://localhost:8000/docs
- **Status Endpoint:** http://localhost:8000/status
- **SSE Stream Endpoint:** http://localhost:8000/pi-stream

## API Endpoints

### `GET /status`
Returns the current π value and circumference calculation.

**Response:**
```json
{
  "pi": "3.14159...",
  "circumference": "4376756.123..."
}
```

### `GET /pi-stream`
Server-Sent Events (SSE) stream that pushes real-time updates whenever the worker calculates new Pi digits.

**Response Format:**
Each event contains JSON with:
```json
{
  "pi": "3.14159265358979323846...",
  "circumference": "40075.017"
}
```

## Configuration

Edit `src/config.py` to modify:

- `SUN_RADIUS_KM`: Radius of the Sun in kilometers (default: 696340)
- `MAX_DIGITS`: Maximum precision for π calculation (default: 10000)
- `SESSION_LIMIT`: Max concurrent SSE connections per session (default: 3)
- `REDIS_HOST`: Redis server hostname (default: 'localhost' for local, 'redis' for Docker)