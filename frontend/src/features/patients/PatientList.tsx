import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TablePagination, Chip, IconButton, Tooltip, Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField, Grid, Card, CardContent, Avatar, Alert, LinearProgress } from '@mui/material';
import { Add, Edit, Delete, Visibility, Person, MedicalServices, MonitorHeart, Search, FilterList, } from '@mui/icons-material';
import { config } from '../../config/environment';
import { useAuth } from '../../contexts/AuthContext';

interface Patient {
  patient_id: number;
  full_name: string;
  age: number;
  gender: string;
  admission_date: string;
  room_number: string;
  assigned_devices: Device[];
  status: 'active' | 'discharged' | 'critical';
  medical_record_number: string;
}

interface Device {
  device_id: number;
  device_name: string;
  device_type: string;
  status: 'active' | 'inactive' | 'maintenance';
}

const PatientList: React.FC = () => {
  const { user } = useAuth();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingPatient, setEditingPatient] = useState<Patient | null>(null);
  const [formData, setFormData] = useState({
    full_name: '',
    age: '',
    gender: '',
    room_number: '',
    medical_record_number: '',
  });

  // Check if user can manage patients (admin roles only)
  const canManagePatients = user?.role && ['super_admin', 'admin_medical', 'admin_hr'].includes(user.role);

  useEffect(() => {
    fetchPatients();
  }, []);

  const fetchPatients = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${config.API_BASE_URL}/patients`, {
        method: 'GET',
        credentials: 'include',
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
      setPatients(data.patients || []);
    } catch (err) {
      console.error('Error fetching patients:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch patients');
      // Fallback to mock data
      setPatients(getMockPatients());
    } finally {
      setLoading(false);
    }
  };

  const getMockPatients = (): Patient[] => [
    {
      patient_id: 1,
      full_name: 'Juan Pérez',
      age: 34,
      gender: 'Male',
      admission_date: '2024-01-15',
      room_number: '101',
      medical_record_number: 'MR001',
      status: 'active',
      assigned_devices: [
        { device_id: 1, device_name: 'ESP32-A1', device_type: 'multi_parameter', status: 'active' },
      ],
    },
    {
      patient_id: 2,
      full_name: 'Ana Gómez',
      age: 36,
      gender: 'Female',
      admission_date: '2024-01-16',
      room_number: '102',
      medical_record_number: 'MR002',
      status: 'active',
      assigned_devices: [
        { device_id: 2, device_name: 'ESP32-B2', device_type: 'multi_parameter', status: 'active' },
      ],
    },
    {
      patient_id: 3,
      full_name: 'Carlos Rodríguez',
      age: 28,
      gender: 'Male',
      admission_date: '2024-01-17',
      room_number: '103',
      medical_record_number: 'MR003',
      status: 'critical',
      assigned_devices: [
        { device_id: 3, device_name: 'ESP32-C3', device_type: 'multi_parameter', status: 'active' },
      ],
    },
  ];

  const filteredPatients = patients.filter((patient) => {
    const matchesSearch = patient.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         patient.medical_record_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         patient.room_number.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || patient.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleOpenDialog = (patient?: Patient) => {
    if (patient) {
      setEditingPatient(patient);
      setFormData({
        full_name: patient.full_name,
        age: patient.age.toString(),
        gender: patient.gender,
        room_number: patient.room_number,
        medical_record_number: patient.medical_record_number,
      });
    } else {
      setEditingPatient(null);
      setFormData({
        full_name: '',
        age: '',
        gender: '',
        room_number: '',
        medical_record_number: '',
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingPatient(null);
  };

  const handleSavePatient = async () => {
    try {
      const patientData = {
        ...formData,
        age: parseInt(formData.age),
        admission_date: editingPatient?.admission_date || new Date().toISOString().split('T')[0],
        status: editingPatient?.status || 'active',
      };

      const url = editingPatient 
        ? `${config.API_BASE_URL}/patients/${editingPatient.patient_id}`
        : `${config.API_BASE_URL}/patients`;
      
      const method = editingPatient ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(patientData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Refresh the patient list
      await fetchPatients();
      handleCloseDialog();
    } catch (err) {
      console.error('Error saving patient:', err);
      setError(err instanceof Error ? err.message : 'Failed to save patient');
    }
  };

  const handleDeletePatient = async (patientId: number) => {
    if (!window.confirm('Are you sure you want to delete this patient?')) {
      return;
    }

    try {
      const response = await fetch(`${config.API_BASE_URL}/patients/${patientId}`, {
        method: 'DELETE',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Refresh the patient list
      await fetchPatients();
    } catch (err) {
      console.error('Error deleting patient:', err);
      setError(err instanceof Error ? err.message : 'Failed to delete patient');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'critical': return 'error';
      case 'discharged': return 'default';
      default: return 'default';
    }
  };

  const getDeviceStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'error';
      case 'maintenance': return 'warning';
      default: return 'default';
    }
  };

  if (loading) {
    return <LinearProgress />;
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Patient Management
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Manage patient records and device assignments
          </Typography>
        </Box>
            {canManagePatients && (
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => handleOpenDialog()}
              >
                Add Patient
              </Button>
            )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                  <Person />
                </Avatar>
                <Box>
                  <Typography variant="h4" color="primary">
                    {patients.length}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Total Patients
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Avatar sx={{ bgcolor: 'success.main', mr: 2 }}>
                  <MedicalServices />
                </Avatar>
                <Box>
                  <Typography variant="h4" color="success.main">
                    {patients.filter(p => p.status === 'active').length}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Active Patients
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Avatar sx={{ bgcolor: 'error.main', mr: 2 }}>
                  <MonitorHeart />
                </Avatar>
                <Box>
                  <Typography variant="h4" color="error.main">
                    {patients.filter(p => p.status === 'critical').length}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Critical Patients
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Avatar sx={{ bgcolor: 'warning.main', mr: 2 }}>
                  <MonitorHeart />
                </Avatar>
                <Box>
                  <Typography variant="h4" color="warning.main">
                    {patients.reduce((acc, p) => acc + p.assigned_devices.length, 0)}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Assigned Devices
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              placeholder="Search patients..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
              }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              select
              label="Status Filter"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              SelectProps={{ native: true }}
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="critical">Critical</option>
              <option value="discharged">Discharged</option>
            </TextField>
          </Grid>
          <Grid item xs={12} md={3}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<FilterList />}
              onClick={() => {
                setSearchTerm('');
                setStatusFilter('all');
              }}
            >
              Clear Filters
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Patient Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Patient</TableCell>
              <TableCell>Age</TableCell>
              <TableCell>Room</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Devices</TableCell>
              <TableCell>Admission Date</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredPatients
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((patient) => (
                <TableRow key={patient.patient_id} hover>
                  <TableCell>
                    <Box>
                      <Typography variant="subtitle2" fontWeight="bold">
                        {patient.full_name}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        MR: {patient.medical_record_number}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>{patient.age}</TableCell>
                  <TableCell>{patient.room_number}</TableCell>
                  <TableCell>
                    <Chip
                      label={patient.status.toUpperCase()}
                      color={getStatusColor(patient.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Box display="flex" flexWrap="wrap" gap={0.5}>
                      {patient.assigned_devices.map((device) => (
                        <Chip
                          key={device.device_id}
                          label={device.device_name}
                          color={getDeviceStatusColor(device.status) as any}
                          size="small"
                          variant="outlined"
                        />
                      ))}
                    </Box>
                  </TableCell>
                  <TableCell>
                    {new Date(patient.admission_date).toLocaleDateString()}
                  </TableCell>
                      <TableCell align="center">
                        <Box display="flex" gap={1}>
                          <Tooltip title="View Details">
                            <IconButton size="small" color="primary">
                              <Visibility />
                            </IconButton>
                          </Tooltip>
                          {canManagePatients && (
                            <>
                              <Tooltip title="Edit Patient">
                                <IconButton
                                  size="small"
                                  color="primary"
                                  onClick={() => handleOpenDialog(patient)}
                                >
                                  <Edit />
                                </IconButton>
                              </Tooltip>
                              {user?.role === 'super_admin' && (
                                <Tooltip title="Delete Patient">
                                  <IconButton
                                    size="small"
                                    color="error"
                                    onClick={() => handleDeletePatient(patient.patient_id)}
                                  >
                                    <Delete />
                                  </IconButton>
                                </Tooltip>
                              )}
                            </>
                          )}
                        </Box>
                      </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={filteredPatients.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </TableContainer>

      {/* Add/Edit Patient Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingPatient ? 'Edit Patient' : 'Add New Patient'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Full Name"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Age"
                type="number"
                value={formData.age}
                onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                select
                label="Gender"
                value={formData.gender}
                onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                SelectProps={{ native: true }}
                required
              >
                <option value="">Select Gender</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </TextField>
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Room Number"
                value={formData.room_number}
                onChange={(e) => setFormData({ ...formData, room_number: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Medical Record Number"
                value={formData.medical_record_number}
                onChange={(e) => setFormData({ ...formData, medical_record_number: e.target.value })}
                required
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSavePatient} variant="contained">
            {editingPatient ? 'Update' : 'Add'} Patient
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PatientList;
