import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Chip,
  Avatar,
  LinearProgress,
} from '@mui/material';
import {
  People,
  MonitorHeart,
  Science,
  Warning,
  CheckCircle,
} from '@mui/icons-material';

interface DashboardStats {
  totalPatients: number;
  activeDevices: number;
  criticalAlerts: number;
  normalReadings: number;
}

const MedicDashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalPatients: 0,
    activeDevices: 0,
    criticalAlerts: 0,
    normalReadings: 0,
  });
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // TODO: Fetch dashboard stats from API
    // For now, using mock data
    setTimeout(() => {
      setStats({
        totalPatients: 12,
        activeDevices: 8,
        criticalAlerts: 2,
        normalReadings: 156,
      });
      setLoading(false);
    }, 1000);
  }, []);

  const StatCard: React.FC<{
    title: string;
    value: number;
    icon: React.ReactNode;
    color: string;
    onClick?: () => void;
  }> = ({ title, value, icon, color, onClick }) => (
    <Card
      sx={{
        height: '100%',
        cursor: onClick ? 'pointer' : 'default',
        '&:hover': onClick ? { boxShadow: 4 } : {},
      }}
      onClick={onClick}
    >
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="h6">
              {title}
            </Typography>
            <Typography variant="h4" component="h2">
              {value}
            </Typography>
          </Box>
          <Avatar sx={{ bgcolor: color, width: 56, height: 56 }}>{icon}</Avatar>
        </Box>
      </CardContent>
    </Card>
  );

  if (loading) {
    return <LinearProgress />;
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Welcome back, Doctor
      </Typography>
      <Typography variant="body1" color="textSecondary" sx={{ mb: 4 }}>
        Here's an overview of your patients and monitoring systems
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Patients"
            value={stats.totalPatients}
            icon={<People />}
            color="#1976d2"
            onClick={() => navigate('/patients')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Devices"
            value={stats.activeDevices}
            icon={<MonitorHeart />}
            color="#2e7d32"
            onClick={() => navigate('/telemetry')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Critical Alerts"
            value={stats.criticalAlerts}
            icon={<Warning />}
            color="#d32f2f"
            onClick={() => navigate('/telemetry')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Normal Readings"
            value={stats.normalReadings}
            icon={<CheckCircle />}
            color="#388e3c"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Box display="flex" flexDirection="column" gap={2}>
                <Button
                  variant="outlined"
                  startIcon={<People />}
                  onClick={() => navigate('/patients')}
                  fullWidth
                >
                  View All Patients
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<MonitorHeart />}
                  onClick={() => navigate('/telemetry')}
                  fullWidth
                >
                  Monitor Telemetry
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Science />}
                  onClick={() => navigate('/simulator')}
                  fullWidth
                >
                  Test Device Simulation
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Status
              </Typography>
              <Box display="flex" flexDirection="column" gap={2}>
                <Box
                  display="flex"
                  justifyContent="space-between"
                  alignItems="center"
                >
                  <Typography variant="body2">IoT Devices</Typography>
                  <Chip
                    label="Online"
                    color="success"
                    size="small"
                    icon={<CheckCircle />}
                  />
                </Box>
                <Box
                  display="flex"
                  justifyContent="space-between"
                  alignItems="center"
                >
                  <Typography variant="body2">Database</Typography>
                  <Chip
                    label="Connected"
                    color="success"
                    size="small"
                    icon={<CheckCircle />}
                  />
                </Box>
                <Box
                  display="flex"
                  justifyContent="space-between"
                  alignItems="center"
                >
                  <Typography variant="body2">WebSocket</Typography>
                  <Chip
                    label="Active"
                    color="success"
                    size="small"
                    icon={<CheckCircle />}
                  />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default MedicDashboard;
