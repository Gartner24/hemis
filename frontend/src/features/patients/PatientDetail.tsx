import React from 'react';
import { Typography, Box, Paper } from '@mui/material';

const PatientDetail: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Patient Details
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography variant="body1">
          Patient detail component will be implemented here.
        </Typography>
      </Paper>
    </Box>
  );
};

export default PatientDetail;
