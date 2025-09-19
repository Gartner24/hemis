import { io, Socket } from 'socket.io-client';
import { config } from '../config/environment';

export interface TelemetryData {
  device_id: number;
  patient_id?: number;  // Optional since it might not always be present
  heart_rate: number;
  spo2: number;
  temperature: number;
  timestamp: string;
  is_simulated: boolean;
}

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
}

class WebSocketService {
  private socket: Socket | null = null;
  private isConnected: boolean = false;

  // Event callbacks
  private onTelemetryUpdate: ((data: TelemetryData) => void) | null = null;
  private onConnectionChange: ((connected: boolean) => void) | null = null;
  private onError: ((error: string) => void) | null = null;

  constructor() {
    this.setupSocket();
  }

  private setupSocket(): void {
    try {
      // Connect to the backend Socket.IO server
      this.socket = io(config.WEBSOCKET_URL, {
        transports: ['websocket', 'polling'],
        autoConnect: false, // Don't auto-connect to prevent loops
        reconnection: false, // Disable auto-reconnection to prevent loops
        timeout: 20000,
      });

      this.setupEventHandlers();
    } catch (error) {
      console.error('Failed to setup WebSocket:', error);
      this.handleError('Failed to setup WebSocket connection');
    }
  }

  private setupEventHandlers(): void {
    if (!this.socket) return;

    // Connection events
    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      this.isConnected = true;
      this.onConnectionChange?.(true);
    });

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
      this.isConnected = false;
      this.onConnectionChange?.(false);
    });

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      this.handleError(`Connection error: ${error.message}`);
    });

    // Authentication events
    this.socket.on('authenticated', (data) => {
      console.log('WebSocket authenticated:', data);
    });

    this.socket.on('authentication_error', (data) => {
      console.error('WebSocket authentication error:', data);
      this.handleError(`Authentication error: ${data.message}`);
    });

    // Telemetry events
    this.socket.on('telemetry_update', (data: TelemetryData) => {
      console.log('Telemetry update received:', data);
      this.onTelemetryUpdate?.(data);
    });

    this.socket.on('vital_signs_update', (data: TelemetryData) => {
      console.log('Vital signs update received:', data);
      this.onTelemetryUpdate?.(data);
    });

    // Error events
    this.socket.on('error', (data) => {
      console.error('WebSocket error:', data);
      this.handleError(`WebSocket error: ${data.message}`);
    });

    // Reconnection events
    this.socket.on('reconnect', (attemptNumber: number) => {
      console.log(`WebSocket reconnected after ${attemptNumber} attempts`);
      this.isConnected = true;
      this.onConnectionChange?.(true);
    });

    this.socket.on('reconnect_failed', () => {
      console.error('WebSocket reconnection failed');
      this.handleError('Failed to reconnect to WebSocket server');
    });
  }

  // Public methods
  public connect(): void {
    if (this.socket && !this.isConnected) {
      this.socket.connect();
    }
  }

  public disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.isConnected = false;
    }
  }

  public authenticate(userId: number, userRole: string): void {
    if (this.socket && this.isConnected) {
      this.socket.emit('authenticate', {
        user_id: userId,
        user_role: userRole,
      });
    }
  }

  public joinTelemetryRoom(roomType: string, roomId: string | number): void {
    if (this.socket && this.isConnected) {
      this.socket.emit('join_telemetry_room', {
        room_type: roomType,
        room_id: roomId,
      });
    }
  }

  public leaveTelemetryRoom(roomType: string, roomId: string | number): void {
    if (this.socket && this.isConnected) {
      this.socket.emit('leave_telemetry_room', {
        room_type: roomType,
        room_id: roomId,
      });
    }
  }

  public subscribeToPatientTelemetry(patientId: number): void {
    this.joinTelemetryRoom('patient', patientId);
  }

  public subscribeToDeviceTelemetry(deviceId: number): void {
    this.joinTelemetryRoom('device', deviceId);
  }

  public subscribeToGlobalTelemetry(): void {
    this.joinTelemetryRoom('global', 'all');
  }

  public unsubscribeFromPatientTelemetry(patientId: number): void {
    this.leaveTelemetryRoom('patient', patientId);
  }

  public unsubscribeFromDeviceTelemetry(deviceId: number): void {
    this.leaveTelemetryRoom('device', deviceId);
  }

  public unsubscribeFromGlobalTelemetry(): void {
    this.leaveTelemetryRoom('global', 'all');
  }

  // Event handlers
  public setTelemetryUpdateHandler(
    callback: (data: TelemetryData) => void
  ): void {
    this.onTelemetryUpdate = callback;
  }

  public setConnectionChangeHandler(
    callback: (connected: boolean) => void
  ): void {
    this.onConnectionChange = callback;
  }

  public setErrorHandler(callback: (error: string) => void): void {
    this.onError = callback;
  }

  // Utility methods
  public isConnectedToServer(): boolean {
    return this.isConnected;
  }

  public getConnectionStatus(): string {
    if (this.isConnected) {
      return 'connected';
    } else if (this.socket?.connected) {
      return 'connecting';
    } else {
      return 'disconnected';
    }
  }

  private handleError(message: string): void {
    this.onError?.(message);
  }

  // Cleanup
  public destroy(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
    this.isConnected = false;
    this.onTelemetryUpdate = null;
    this.onConnectionChange = null;
    this.onError = null;
  }
}

// Export singleton instance
export const webSocketService = new WebSocketService();

// Export the class for testing purposes
export default WebSocketService;
