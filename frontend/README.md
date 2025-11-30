# Pi Streamer Frontend

A real-time React application that displays the calculation of Pi (π) digits streamed from a FastAPI backend using Server-Sent Events (SSE). The application also calculates and displays the circumference of the Sun using the computed Pi value.


## Prerequisites

- Node.js (v22 or higher recommended)
- npm or yarn
- FastAPI backend running on `http://localhost:8000` with the `/pi-stream` endpoint

## Installation

1. Install dependencies:
```bash
npm install
```

## Development

Start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:3000`.

### Configuration

The backend API URL can be configured in `src/App.jsx`:

```javascript
const API_STREAM_URL = 'http://localhost:8000/pi-stream'
```

The maximum number of digits to calculate can be adjusted:

```javascript
const MAX_DIGITS = 100
```

## Build

Build the application for production:

```bash
npm run build
```

The built files will be in the `dist` directory.

## Preview Production Build

Preview the production build locally:

```bash
npm run preview
```

## Project Structure

```
pi-frontend/
├── src/
│   ├── App.jsx          # Main application component
│   ├── App.css          # Application styles
│   ├── index.css        # Global styles
│   └── main.jsx         # Application entry point
├── public/              # Static assets
├── vite.config.js       # Vite configuration
└── package.json         # Dependencies and scripts
```

## Technologies Used

- **React 19** - UI library
- **Vite** - Build tool and dev server
- **lucide-react** - Icon library
- **Tailwind CSS** - Utility-first CSS framework (via CDN or configuration)

## How It Works

1. The application establishes a Server-Sent Events (SSE) connection to the backend
2. The backend streams Pi digits incrementally as they are calculated
3. Each update includes:
   - The current Pi value
   - The calculated circumference of the Sun
4. The UI updates in real-time, highlighting newly calculated digits in green
5. Progress is tracked and displayed via a progress bar
6. The stream completes when 100 digits are reached (configurable)

## Status Indicators

- **Connecting...** (Yellow) - Establishing connection to backend
- **Calculating** (Green) - Actively receiving and displaying Pi digits
- **Complete** (Blue) - Reached maximum digits (100)
- **Error** (Red) - Connection error or parsing failure
