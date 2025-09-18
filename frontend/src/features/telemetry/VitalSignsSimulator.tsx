import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Paper,
  Button,
  Grid,
  Card,
  CardContent,
  Chip,
} from '@mui/material';
import {
  Stop,
  Warning,
  Error,
  CheckCircle,
  MonitorHeart,
} from '@mui/icons-material';

interface VitalSigns {
  heartRate: number;
  bloodOxygen: number;
  bodyTemperature: number;
  timestamp: string;
}

interface SimulationState {
  name: string;
  color: 'success' | 'warning' | 'error';
  icon: React.ReactNode;
  description: string;
}

const VitalSignsSimulator: React.FC = () => {
  const [isSimulating, setIsSimulating] = useState(false);
  const [currentState, setCurrentState] = useState<string>('normal');
  const [vitalSigns, setVitalSigns] = useState<VitalSigns | null>(null);
  const [simulationInterval, setSimulationInterval] = useState<number | null>(
    null
  );

  const simulationStates: Record<string, SimulationState> = {
    normal: {
      name: 'Normal State',
      color: 'success',
      icon: <CheckCircle />,
      description: 'Patient shows healthy vital signs within normal ranges',
    },
    critical: {
      name: 'Critical State',
      color: 'warning',
      icon: <Warning />,
      description:
        'Patient shows concerning vital signs requiring immediate attention',
    },
    death: {
      name: 'Death State',
      color: 'error',
      icon: <Error />,
      description:
        'Patient shows critical vital signs indicating life-threatening condition',
    },
  };

  const generateVitalSigns = (state: string): VitalSigns => {
    const now = new Date();
    let heartRate, bloodOxygen, bodyTemperature;

    switch (state) {
      case 'normal':
        heartRate = Math.floor(Math.random() * 20) + 60; // 60-80 bpm
        bloodOxygen = Math.floor(Math.random() * 5) + 95; // 95-100%
        bodyTemperature = Math.random() * 1.2 + 36.5; // 36.5-37.7°C
        break;
      case 'critical':
        heartRate = Math.floor(Math.random() * 40) + 100; // 100-140 bpm
        bloodOxygen = Math.floor(Math.random() * 10) + 85; // 85-95%
        bodyTemperature = Math.random() * 2 + 38.5; // 38.5-40.5°C
        break;
      case 'death':
        heartRate = Math.floor(Math.random() * 30) + 20; // 20-50 bpm
        bloodOxygen = Math.floor(Math.random() * 15) + 70; // 70-85%
        bodyTemperature = Math.random() * 3 + 35; // 35-38°C
        break;
      default:
        heartRate = 70;
        bloodOxygen = 98;
        bodyTemperature = 37;
    }

    return {
      heartRate,
      bloodOxygen,
      bodyTemperature,
      timestamp: now.toLocaleTimeString(),
    };
  };

  const startSimulation = (state: string) => {
    setCurrentState(state);
    setIsSimulating(true);

    // Generate initial vital signs
    setVitalSigns(generateVitalSigns(state));

    // Start continuous simulation
    const interval = setInterval(() => {
      setVitalSigns(generateVitalSigns(state));
    }, 2000); // Update every 2 seconds

    setSimulationInterval(interval);
  };

  const stopSimulation = () => {
    setIsSimulating(false);
    setVitalSigns(null);
    if (simulationInterval) {
      clearInterval(simulationInterval);
      setSimulationInterval(null);
    }
  };

  const getVitalSignsStatus = (type: string, value: number) => {
    let status: 'normal' | 'warning' | 'critical' = 'normal';
    let color: 'success' | 'warning' | 'error' = 'success';

    switch (type) {
      case 'heartRate':
        if (value < 60 || value > 100) status = 'warning';
        if (value < 50 || value > 120) status = 'critical';
        break;
      case 'bloodOxygen':
        if (value < 95) status = 'warning';
        if (value < 90) status = 'critical';
        break;
      case 'bodyTemperature':
        if (value < 36 || value > 37.5) status = 'warning';
        if (value < 35 || value > 38.5) status = 'critical';
        break;
    }

    switch (status) {
      case 'normal':
        color = 'success';
        break;
      case 'warning':
        color = 'warning';
        break;
      case 'critical':
        color = 'error';
        break;
    }

    return { status, color };
  };

  useEffect(() => {
    return () => {
      if (simulationInterval) {
        clearInterval(simulationInterval);
      }
    };
  }, [simulationInterval]);

  return (
    <Box>
      <Typography
        variant="h4"
        gutterBottom
        sx={{ display: 'flex', alignItems: 'center', gap: 1 }}
      >
        <MonitorHeart color="primary" />
        Vital Signs Simulator
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Simulation Controls
        </Typography>

        <Grid container spacing={2} sx={{ mb: 3 }}>
          {Object.entries(simulationStates).map(([key, state]) => (
            <Grid item xs={12} sm={4} key={key}>
              <Button
                variant={
                  currentState === key && isSimulating
                    ? 'contained'
                    : 'outlined'
                }
                color={state.color}
                fullWidth
                size="large"
                startIcon={state.icon}
                onClick={() => startSimulation(key)}
                disabled={isSimulating && currentState === key}
                sx={{ height: 60 }}
              >
                {state.name}
              </Button>
            </Grid>
          ))}
        </Grid>

        {isSimulating && (
          <Box sx={{ textAlign: 'center' }}>
            <Button
              variant="contained"
              color="error"
              size="large"
              startIcon={<Stop />}
              onClick={stopSimulation}
              sx={{ minWidth: 120 }}
            >
              Stop Simulation
            </Button>
          </Box>
        )}
      </Paper>

      {/* Current State Display */}
      {isSimulating && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Current Simulation State
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Chip
              icon={simulationStates[currentState].icon as React.ReactElement}
              label={simulationStates[currentState].name}
              color={simulationStates[currentState].color}
              size="medium"
            />
            <Typography variant="body2" color="text.secondary">
              {simulationStates[currentState].description}
            </Typography>
          </Box>
        </Paper>
      )}

      {/* Real-time Vital Signs Display */}
      {isSimulating && vitalSigns ? (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Real-time Vital Signs
          </Typography>

          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" color="primary" gutterBottom>
                    Heart Rate
                  </Typography>
                  <Typography variant="h3" component="div" sx={{ mb: 1 }}>
                    {vitalSigns.heartRate}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    BPM
                  </Typography>
                  <Chip
                    label={
                      getVitalSignsStatus('heartRate', vitalSigns.heartRate)
                        .status
                    }
                    color={
                      getVitalSignsStatus('heartRate', vitalSigns.heartRate)
                        .color
                    }
                    size="small"
                    sx={{ mt: 1 }}
                  />
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" color="primary" gutterBottom>
                    Blood Oxygen
                  </Typography>
                  <Typography variant="h3" component="div" sx={{ mb: 1 }}>
                    {vitalSigns.bloodOxygen}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    SpO2
                  </Typography>
                  <Chip
                    label={
                      getVitalSignsStatus('bloodOxygen', vitalSigns.bloodOxygen)
                        .status
                    }
                    color={
                      getVitalSignsStatus('bloodOxygen', vitalSigns.bloodOxygen)
                        .color
                    }
                    size="small"
                    sx={{ mt: 1 }}
                  />
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" color="primary" gutterBottom>
                    Body Temperature
                  </Typography>
                  <Typography variant="h3" component="div" sx={{ mb: 1 }}>
                    {vitalSigns.bodyTemperature.toFixed(1)}°C
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Core Temp
                  </Typography>
                  <Chip
                    label={
                      getVitalSignsStatus(
                        'bodyTemperature',
                        vitalSigns.bodyTemperature
                      ).status
                    }
                    color={
                      getVitalSignsStatus(
                        'bodyTemperature',
                        vitalSigns.bodyTemperature
                      ).color
                    }
                    size="small"
                    sx={{ mt: 1 }}
                  />
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Box sx={{ mt: 3, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Last Updated: {vitalSigns.timestamp}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Updates every 2 seconds
            </Typography>
          </Box>
        </Paper>
      ) : (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No Active Simulation
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Click one of the simulation buttons above to start monitoring vital
            signs
          </Typography>
        </Paper>
      )}

      {/* Instructions */}
      <Paper sx={{ p: 3, mt: 3, bgcolor: 'grey.50' }}>
        <Typography variant="h6" gutterBottom>
          How to Use the Simulator
        </Typography>
        <Typography variant="body2" paragraph>
          This simulator helps medical staff understand how IoT devices behave
          in different patient scenarios:
        </Typography>
        <Box component="ul" sx={{ pl: 2 }}>
          <Typography component="li" variant="body2">
            <strong>Normal State:</strong> Simulates healthy patient with normal
            vital signs
          </Typography>
          <Typography component="li" variant="body2">
            <strong>Critical State:</strong> Simulates patient requiring
            immediate medical attention
          </Typography>
          <Typography component="li" variant="body2">
            <strong>Death State:</strong> Simulates life-threatening condition
            requiring emergency response
          </Typography>
        </Box>
        <Typography variant="body2" sx={{ mt: 2, fontStyle: 'italic' }}>
          The simulator updates vital signs every 2 seconds to mimic real-time
          IoT device behavior.
        </Typography>
      </Paper>
    </Box>
  );
};

export default VitalSignsSimulator;
