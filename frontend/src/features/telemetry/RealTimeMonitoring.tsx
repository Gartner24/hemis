import React, { useState, useEffect, memo } from 'react';
import {Box, Grid, Card, CardContent, Typography, Chip, Avatar, Alert, IconButton, Tooltip, Paper, Fade, Skeleton} from '@mui/material';
import {Favorite, Air, Thermostat, Warning, CheckCircle, Refresh, SignalCellular4Bar, SignalCellular0Bar} from '@mui/icons-material';
import {webSocketService, type TelemetryData} from '../../services/websocketService';
import { config } from '../../config/environment';

interface VitalSigns {
  heart_rate: number;
  spo2: number;
  temp_skin: number;
  timestamp: string;
  is_simulated: boolean;
}

interface Patient {
  patient_id: number;
  full_name: string;
  age: number;
  assigned_devices: Device[];
}

interface Device {
  device_id: number;
  device_name: string;
  device_type: string;
  status: string;
  last_reading_time: string;
  vital_signs: VitalSigns;
}

const RealTimeMonitoring: React.FC = () => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [initialLoadComplete, setInitialLoadComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [wsConnected, setWsConnected] = useState(false);

  useEffect(() => {
    // Initialize WebSocket connection only once
    setupWebSocket();

    // Fetch initial data
    fetchRealData();

    // Set up polling every 1 second for real-time updates
    const interval = setInterval(() => {
      fetchRealDataSilently();
      setLastUpdate(new Date());
    }, 1000); // 1 second polling for real-time feel

    return () => {
      clearInterval(interval);
      webSocketService.disconnect();
    };
  }, []); // Empty dependency array - setup only once

  const setupWebSocket = () => {
    // Prevent multiple setups by checking if handlers are already set
    if (webSocketService.isConnectedToServer()) {
      return;
    }

    // Set up WebSocket event handlers
    webSocketService.setConnectionChangeHandler((connected: boolean) => {
      setWsConnected(connected);
      if (connected) {
        console.log('WebSocket connected, subscribing to global telemetry');
        webSocketService.subscribeToGlobalTelemetry();
        setError(null); // Clear any previous errors
      } else {
        console.log('WebSocket disconnected');
      }
    });

    webSocketService.setTelemetryUpdateHandler(
      (telemetryData: TelemetryData) => {
        console.log('Received telemetry update:', telemetryData);
        updatePatientTelemetry(telemetryData);
        setLastUpdate(new Date());
      }
    );

    webSocketService.setErrorHandler((errorMessage: string) => {
      console.error('WebSocket error:', errorMessage);
      setError(errorMessage);
      setWsConnected(false);
    });

    // Connect to WebSocket server with retry logic
    const connectWithRetry = (retryCount = 0) => {
      try {
        webSocketService.connect();
      } catch (error) {
        console.error('Failed to connect to WebSocket:', error);
        if (retryCount < 3) {
          console.log(`Retrying WebSocket connection in ${(retryCount + 1) * 2} seconds...`);
          setTimeout(() => connectWithRetry(retryCount + 1), (retryCount + 1) * 2000);
        } else {
          setError('Failed to connect to WebSocket server after multiple attempts');
          setWsConnected(false);
        }
      }
    };

    connectWithRetry();
  };

  const updatePatientTelemetry = (telemetryData: TelemetryData) => {
    setPatients((prevPatients) => {
      // Only update if we actually have changes to avoid unnecessary re-renders
      const updatedPatients = prevPatients.map((patient) => {
        if (patient.patient_id === telemetryData.patient_id) {
          const updatedDevices = patient.assigned_devices.map((device) => {
            if (device.device_id === telemetryData.device_id) {
              const newVitalSigns = {
                heart_rate: telemetryData.heart_rate,
                spo2: telemetryData.spo2,
                temp_skin: telemetryData.temperature,
                timestamp: telemetryData.timestamp,
                is_simulated: telemetryData.is_simulated,
              };
              
              // Only update if data actually changed
              const currentVitalSigns = device.vital_signs;
              if (
                currentVitalSigns.heart_rate === newVitalSigns.heart_rate &&
                currentVitalSigns.spo2 === newVitalSigns.spo2 &&
                currentVitalSigns.temp_skin === newVitalSigns.temp_skin &&
                currentVitalSigns.timestamp === newVitalSigns.timestamp
              ) {
                return device; // No change, return same reference
              }
              
              return {
                ...device,
                last_reading_time: telemetryData.timestamp,
                vital_signs: newVitalSigns,
              };
            }
            return device;
          });
          
          // Only update patient if devices changed
          if (updatedDevices === patient.assigned_devices) {
            return patient; // No change, return same reference
          }
          
          return {
            ...patient,
            assigned_devices: updatedDevices,
          };
        }
        return patient;
      });
      
      // Only update state if something actually changed
      return updatedPatients;
    });
  };

  const fetchRealData = async () => {
    try {
      setError(null);

      const response = await fetch(`${config.API_BASE_URL}/telemetry/patients-with-devices`, {
        method: 'GET',
        credentials: 'include', // Use cookies for authentication
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication required. Please log in.');
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Filter out patients without devices for cleaner display
      const patientsWithDevices = data.patients.filter((patient: Patient) => 
        patient.assigned_devices && patient.assigned_devices.length > 0
      );
      
      setPatients(patientsWithDevices);
      setInitialLoadComplete(true);
      setLastUpdate(new Date());
      
    } catch (err) {
      console.error('Error fetching real data:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch patient data');
      
      // Fallback to mock data if API fails
      console.log('Falling back to mock data');
      fetchMockData();
    }
  };

  const fetchRealDataSilently = async () => {
    try {
      const response = await fetch(`${config.API_BASE_URL}/telemetry/patients-with-devices`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        const patientsWithDevices = data.patients.filter((patient: Patient) => 
          patient.assigned_devices && patient.assigned_devices.length > 0
        );
        
        setPatients(patientsWithDevices);
        setLastUpdate(new Date());
        console.log('Silent data refresh completed');
      }
    } catch (err) {
      console.error('Silent data refresh failed:', err);
    }
  };

  const fetchMockData = () => {
    // Fallback mock data for demonstration
    const mockPatients: Patient[] = [
      {
        patient_id: 1,
        full_name: 'Juan Pérez',
        age: 34,
        assigned_devices: [
          {
            device_id: 1,
            device_name: 'ESP32-A1',
            device_type: 'multi_parameter',
            status: 'active',
            last_reading_time: new Date().toISOString(),
            vital_signs: {
              heart_rate: 0,
              spo2: 0,
              temp_skin: 25.6,
              timestamp: new Date().toISOString(),
              is_simulated: false,
            },
          },
        ],
      },
      {
        patient_id: 2,
        full_name: 'Ana Gómez',
        age: 36,
        assigned_devices: [
          {
            device_id: 2,
            device_name: 'ESP32-B2',
            device_type: 'multi_parameter',
            status: 'active',
            last_reading_time: new Date().toISOString(),
            vital_signs: {
              heart_rate: 0,
              spo2: 0,
              temp_skin: 25.6,
              timestamp: new Date().toISOString(),
              is_simulated: false,
            },
          },
        ],
      },
    ];

    setPatients(mockPatients);
    setInitialLoadComplete(true);
  };


  const getVitalSignsStatus = (vitalSigns: VitalSigns) => {
    const { heart_rate, spo2, temp_skin } = vitalSigns;

    // Check for critical values
    if (
      heart_rate < 50 ||
      heart_rate > 120 ||
      spo2 < 90 ||
      temp_skin < 35 ||
      temp_skin > 38.5
    ) {
      return { status: 'critical', color: 'error', icon: <Warning /> };
    }

    // Check for warning values
    if (
      heart_rate < 60 ||
      heart_rate > 100 ||
      spo2 < 95 ||
      temp_skin < 36 ||
      temp_skin > 37.5
    ) {
      return { status: 'warning', color: 'warning', icon: <Warning /> };
    }

    return { status: 'normal', color: 'success', icon: <CheckCircle /> };
  };

  const VitalSignsCard: React.FC<{
    vitalSigns: VitalSigns;
    device: Device;
  }> = memo(({ vitalSigns, device }) => {
    const status = getVitalSignsStatus(vitalSigns);

    return (
      <Fade in={true} timeout={300}>
        <Card sx={{ 
          height: '100%', 
          position: 'relative',
          transition: 'all 0.3s ease-in-out',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: 3
          }
        }}>
        <CardContent>
          <Box
            display="flex"
            justifyContent="space-between"
            alignItems="center"
            mb={2}
          >
            <Typography variant="h6" component="h3">
              {device.device_name}
            </Typography>
            <Chip
              label={status.status.toUpperCase()}
              color={status.color as any}
              icon={status.icon}
              size="small"
            />
          </Box>

          <Grid container spacing={2}>
            <Grid item xs={4}>
              <Box textAlign="center">
                <Avatar
                  sx={{
                    bgcolor: '#e3f2fd',
                    color: '#1976d2',
                    width: 48,
                    height: 48,
                    mx: 'auto',
                    mb: 1,
                  }}
                >
                  <Favorite />
                </Avatar>
                <Typography 
                  variant="h4" 
                  color="textPrimary"
                  sx={{
                    transition: 'all 0.3s ease-in-out',
                    '&:hover': { transform: 'scale(1.05)' }
                  }}
                >
                  {vitalSigns.heart_rate}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  BPM
                </Typography>
              </Box>
            </Grid>

            <Grid item xs={4}>
              <Box textAlign="center">
                <Avatar
                  sx={{
                    bgcolor: '#e8f5e8',
                    color: '#2e7d32',
                    width: 48,
                    height: 48,
                    mx: 'auto',
                    mb: 1,
                  }}
                >
                  <Air />
                </Avatar>
                <Typography 
                  variant="h4" 
                  color="textPrimary"
                  sx={{
                    transition: 'all 0.3s ease-in-out',
                    '&:hover': { transform: 'scale(1.05)' }
                  }}
                >
                  {vitalSigns.spo2}%
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  SpO2
                </Typography>
              </Box>
            </Grid>

            <Grid item xs={4}>
              <Box textAlign="center">
                <Avatar
                  sx={{
                    bgcolor: '#fff3e0',
                    color: '#f57c00',
                    width: 48,
                    height: 48,
                    mx: 'auto',
                    mb: 1,
                  }}
                >
                  <Thermostat />
                </Avatar>
                <Typography 
                  variant="h4" 
                  color="textPrimary"
                  sx={{
                    transition: 'all 0.3s ease-in-out',
                    '&:hover': { transform: 'scale(1.05)' }
                  }}
                >
                  {vitalSigns.temp_skin}°C
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  Temp
                </Typography>
              </Box>
            </Grid>
          </Grid>

          <Box
            mt={2}
            display="flex"
            justifyContent="space-between"
            alignItems="center"
          >
            <Typography variant="caption" color="textSecondary">
              Last update: {new Date(vitalSigns.timestamp).toLocaleTimeString()}
            </Typography>
            {vitalSigns.is_simulated && (
              <Chip label="SIMULATED" size="small" color="secondary" />
            )}
          </Box>
        </CardContent>
        </Card>
      </Fade>
    );
  });

  const PatientMonitor: React.FC<{ patient: Patient }> = memo(({ patient }) => (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        mb={2}
      >
        <Box>
          <Typography variant="h5" component="h2">
            {patient.full_name}
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Patient ID: {patient.patient_id} | Age: {patient.age}
          </Typography>
        </Box>
        <Chip
          label={`${patient.assigned_devices.length} Device(s)`}
          color="primary"
          variant="outlined"
        />
      </Box>

      <Grid container spacing={3}>
        {patient.assigned_devices.map((device) => (
          <Grid item xs={12} md={6} key={device.device_id}>
            <VitalSignsCard vitalSigns={device.vital_signs} device={device} />
          </Grid>
        ))}
      </Grid>
    </Paper>
  ));

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        mb={3}
      >
        <Box>
          <Typography variant="h4" gutterBottom>
            Real-time Patient Monitoring
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Live vital signs monitoring for all assigned patients
          </Typography>
        </Box>

        <Box display="flex" alignItems="center" gap={2}>
          {/* WebSocket Connection Status */}
          <Chip
            icon={wsConnected ? <SignalCellular4Bar /> : <SignalCellular0Bar />}
            label={wsConnected ? 'Live' : 'Offline'}
            color={wsConnected ? 'success' : 'error'}
            size="small"
          />
          <Typography variant="body2" color="textSecondary">
            Last update: {lastUpdate.toLocaleTimeString()}
          </Typography>
          <Tooltip title="Refresh data">
            <IconButton onClick={fetchRealData} size="small">
              <Refresh />
            </IconButton>
          </Tooltip>
          <Tooltip title="Reconnect WebSocket">
            <IconButton 
              onClick={() => {
                webSocketService.reconnect();
                setError(null);
              }} 
              size="small"
              disabled={wsConnected}
            >
              <SignalCellular4Bar />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Show skeleton loading only for initial load */}
      {!initialLoadComplete && (
        <Box>
          {[1, 2].map((i) => (
            <Paper key={i} sx={{ p: 3, mb: 3 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Box>
                  <Skeleton variant="text" width={200} height={40} />
                  <Skeleton variant="text" width={150} height={20} />
                </Box>
                <Skeleton variant="rectangular" width={100} height={32} />
              </Box>
              <Grid container spacing={3}>
                {[1, 2].map((j) => (
                  <Grid item xs={12} md={6} key={j}>
                    <Card sx={{ height: '100%' }}>
                      <CardContent>
                        <Skeleton variant="text" width={150} height={30} />
                        <Grid container spacing={2} sx={{ mt: 2 }}>
                          {[1, 2, 3].map((k) => (
                            <Grid item xs={4} key={k}>
                              <Box textAlign="center">
                                <Skeleton variant="circular" width={48} height={48} sx={{ mx: 'auto', mb: 1 }} />
                                <Skeleton variant="text" width={60} height={40} />
                                <Skeleton variant="text" width={40} height={20} />
                              </Box>
                            </Grid>
                          ))}
                        </Grid>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Paper>
          ))}
        </Box>
      )}

      {initialLoadComplete && (
        <Fade in={initialLoadComplete} timeout={500}>
          <Box>
            {patients.length === 0 ? (
              <Alert severity="info">
                No patients with assigned devices found. Please assign devices to
                patients to start monitoring.
              </Alert>
            ) : (
              <Box>
                {patients.map((patient) => (
                  <PatientMonitor key={patient.patient_id} patient={patient} />
                ))}
              </Box>
            )}
          </Box>
        </Fade>
      )}

      <Box mt={4}>
        <Typography variant="h6" gutterBottom>
          Monitoring Status
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h4" color="primary">
                  {patients.length}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Active Patients
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h4" color="success.main">
                  {patients.reduce(
                    (acc, p) => acc + p.assigned_devices.length,
                    0
                  )}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Active Devices
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h4" color="warning.main">
                  {patients.reduce((acc, p) => {
                    return (
                      acc +
                      p.assigned_devices.filter(
                        (d) =>
                          getVitalSignsStatus(d.vital_signs).status ===
                          'warning'
                      ).length
                    );
                  }, 0)}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Warning Alerts
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h4" color="error.main">
                  {patients.reduce((acc, p) => {
                    return (
                      acc +
                      p.assigned_devices.filter(
                        (d) =>
                          getVitalSignsStatus(d.vital_signs).status ===
                          'critical'
                      ).length
                    );
                  }, 0)}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Critical Alerts
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
};

export default RealTimeMonitoring;
