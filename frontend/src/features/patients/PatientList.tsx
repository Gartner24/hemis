import React from 'react'
import { Typography, Box, Paper } from '@mui/material'

const PatientList: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Patient Management
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography variant="body1">
          Patient list component will be implemented here.
        </Typography>
      </Paper>
    </Box>
  )
}

export default PatientList
