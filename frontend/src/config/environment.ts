// Environment configuration
export const config = {
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api',
  WEBSOCKET_URL: import.meta.env.VITE_WEBSOCKET_URL || 'http://localhost:5000',
  FRONTEND_PORT: import.meta.env.VITE_FRONTEND_PORT || '5173',
  BACKEND_PORT: import.meta.env.VITE_BACKEND_PORT || '5000',
  CORS_ORIGINS: import.meta.env.VITE_CORS_ORIGINS || 'http://localhost:5173,http://127.0.0.1:5173',
  TELEMETRY_UPDATE_INTERVAL: parseInt(import.meta.env.VITE_TELEMETRY_UPDATE_INTERVAL || '1000'),
  IOT_API_KEY: import.meta.env.VITE_IOT_API_KEY || 'your_iot_device_api_key',
  LOG_LEVEL: import.meta.env.VITE_LOG_LEVEL || 'INFO',
  NODE_ENV: import.meta.env.VITE_NODE_ENV || 'production',
  DEBUG: import.meta.env.VITE_DEBUG === 'true' || false,
};
