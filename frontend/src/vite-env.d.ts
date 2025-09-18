/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_WEBSOCKET_URL: string
  readonly VITE_FRONTEND_PORT: string
  readonly VITE_BACKEND_PORT: string
  readonly VITE_CORS_ORIGINS: string
  readonly VITE_TELEMETRY_UPDATE_INTERVAL: string
  readonly VITE_IOT_API_KEY: string
  readonly VITE_LOG_LEVEL: string
  readonly VITE_NODE_ENV: string
  readonly VITE_DEBUG: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
