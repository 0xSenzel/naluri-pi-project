import React, { useState, useEffect, useCallback } from 'react';
import { RefreshCw, Play, XCircle, Loader } from 'lucide-react';

const API_STREAM_URL = 'http://localhost:8000/pi-stream';
const MAX_DIGITS = 100;

// Helper function to format large numbers (circumference)
const formatNumber = (numStr) => {
  if (!numStr || numStr.includes('e')) return numStr; // Handle scientific notation or empty string
  
  // Split the number into integer and decimal parts
  const parts = numStr.split('.');
  const integerPart = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  
  // Keep the entire decimal part as is, since it's the high-precision data
  const decimalPart = parts[1] || '';
  
  return decimalPart ? `${integerPart}.${decimalPart}` : integerPart;
};


const App = () => {
  const [pi, setPi] = useState("3");
  const [circumference, setCircumference] = useState("0");
  const [status, setStatus] = useState('IDLE'); // IDLE, CONNECTING, ACTIVE, ERROR, COMPLETE
  const [error, setError] = useState('');

  // Derived state for display
  // Precision = pi string length - 2 (for '3.')
  const currentPrecision = pi.length > 2 ? pi.length - 2 : 0;
  const progressPercentage = (currentPrecision / MAX_DIGITS) * 100;
  
  // Reference for the EventSource object
  const [eventSource, setEventSource] = useState(null);
  const [lastMessageTime, setLastMessageTime] = useState(Date.now());

  const connectStream = useCallback(() => {
    if (eventSource) {
      eventSource.close();
      setEventSource(null);
    }
    
    setStatus('CONNECTING');
    setError('');
    
    try {
        const newEventSource = new EventSource(API_STREAM_URL);
        setEventSource(newEventSource);

        newEventSource.onopen = () => {
            console.log('SSE connection opened.');
            setStatus('ACTIVE');
        };

        newEventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                setPi(data.pi);
                setCircumference(data.circumference);
                setLastMessageTime(Date.now());
                
                const newPrecision = data.pi.length - 2;
                if (newPrecision >= MAX_DIGITS) {
                    setStatus('COMPLETE');
                    newEventSource.close();
                } else {
                    setStatus('ACTIVE');
                }
            } catch (e) {
                console.error('Error parsing SSE data:', e);
                setError('Failed to parse incoming data.');
                setStatus('ERROR');
            }
        };

        newEventSource.onerror = (err) => {
            console.error('SSE Error event:', err);
            
            // Check if we've received recent data
            const timeSinceLastMessage = Date.now() - lastMessageTime;
            
            if (timeSinceLastMessage < 5000) {
                // We received data recently, so the connection is working
                // This error might be a temporary blip - just try to close and let it reconnect
                console.log('Recent data received, connection appears healthy');
                newEventSource.close();
                setEventSource(null);
            } else if (status === 'COMPLETE') {
                // Calculation is complete, expected to close
                console.log('Stream closed: calculation complete');
                newEventSource.close();
                setEventSource(null);
            } else {
                // No recent data and not complete = real connection issue
                console.log('No recent data, showing error');
                newEventSource.close();
                setEventSource(null);
                setError('Connection lost. Please ensure the worker is running.');
                setStatus('ERROR');
            }
        };
        
        // Cleanup function for useEffect
        return () => {
            newEventSource.close();
            console.log('SSE connection closed.');
        };
        
    } catch (e) {
        console.error('Failed to create EventSource:', e);
        setError('Failed to initialize connection. Check backend URL.');
        setStatus('ERROR');
    }
    
  }, [MAX_DIGITS, currentPrecision]);

  useEffect(() => {
    connectStream();
    
    // Cleanup on unmount
    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  }, []); // Run only once on mount

  const getStatusColor = () => {
    switch (status) {
      case 'ACTIVE':
        return 'bg-green-600';
      case 'CONNECTING':
        return 'bg-yellow-500 animate-pulse';
      case 'COMPLETE':
        return 'bg-blue-600';
      case 'ERROR':
        return 'bg-red-600';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'ACTIVE':
        return 'Calculating';
      case 'CONNECTING':
        return 'Connecting...';
      case 'COMPLETE':
        return 'Complete';
      case 'ERROR':
        return 'Error';
      default:
        return 'Idle';
    }
  };

  const ProgressDisplay = ({ label, value, max, percentage }) => (
    <div className="w-full mb-6">
      <div className="flex justify-between items-center mb-1">
        <span className="text-gray-300 font-semibold">{label}</span>
        <span className="text-lg font-mono text-white">
          {value} / {max}
        </span>
      </div>
      <div className="w-full bg-gray-700 rounded-full h-2.5">
        <div 
          className="bg-purple-500 h-2.5 rounded-full transition-all duration-1000 ease-out" 
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  );
  
  // Split Pi for highlighting the new precision
  const piParts = pi.split('.');
  const integerPart = piParts[0] + '.';
  const decimalPart = piParts[1] || '';
  const calculatedDigits = decimalPart.slice(0, currentPrecision);
  const paddingZeros = decimalPart.slice(currentPrecision);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4 sm:p-8 font-inter">
      <div className="max-w-4xl mx-auto">
        
        {/* Header and Status */}
        <header className="py-6 border-b border-gray-700 flex justify-between items-center flex-wrap">
          <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">
            Pi Streamer
          </h1>
          <div className="flex items-center space-x-4 mt-4 sm:mt-0">
            <span className={`px-3 py-1 text-sm font-bold rounded-full flex items-center ${getStatusColor()}`}>
              {status === 'CONNECTING' && <Loader className="w-4 h-4 mr-2 animate-spin" />}
              {status === 'ACTIVE' && <Play className="w-4 h-4 mr-2" />}
              {status === 'ERROR' && <XCircle className="w-4 h-4 mr-2" />}
              {getStatusText()}
            </span>
            <button
              onClick={() => connectStream()}
              className="p-2 rounded-full bg-purple-600 hover:bg-purple-700 transition duration-150 shadow-lg"
              title="Reconnect Stream"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
          </div>
        </header>

        {/* Error Message */}
        {error && (
            <div className="mt-4 p-4 bg-red-800 border-l-4 border-red-500 rounded-lg shadow-md">
                <p className="font-semibold text-red-100">Connection Error:</p>
                <p className="text-sm text-red-200">{error}</p>
            </div>
        )}

        {/* Progress Bar */}
        <div className="mt-8 bg-gray-800 p-6 rounded-xl shadow-2xl">
          <ProgressDisplay 
            label="Calculation Progress"
            value={currentPrecision}
            max={MAX_DIGITS}
            percentage={progressPercentage}
          />
        </div>

        {/* Pi Value Card */}
        <div className="mt-8 bg-gray-800 p-6 rounded-xl shadow-2xl transition duration-300 hover:shadow-purple-500/50">
          <h2 className="text-2xl font-bold mb-4 flex items-center text-purple-400">
            <span className="mr-3">π</span> Pi Value
          </h2>
          <div className="bg-gray-900 p-4 rounded-lg overflow-x-auto">
            <code className="font-mono text-lg sm:text-2xl break-all">
              <span className="text-pink-400 font-bold">{integerPart}</span>
              {/* Highlight the dynamically calculated digits */}
              <span className="text-green-300 font-medium">{calculatedDigits}</span>
              {/* Show the remaining zeros/padding */}
              <span className="text-gray-500">{paddingZeros}</span>
            </code>
          </div>
        </div>

        {/* Circumference Card */}
        <div className="mt-8 bg-gray-800 p-6 rounded-xl shadow-2xl transition duration-300 hover:shadow-pink-500/50">
          <h2 className="text-2xl font-bold mb-4 text-pink-400">
            Circumference of the Sun
          </h2>
          <p className="text-sm text-gray-400 mb-2">
            Using the calculated π and the Sun's radius (695,700 km).
          </p>
          <div className="bg-gray-900 p-4 rounded-lg overflow-x-auto">
            <code className="font-mono text-xl sm:text-3xl text-white">
              {formatNumber(circumference)} km
            </code>
          </div>
        </div>

      </div>
    </div>
  );
};

export default App;