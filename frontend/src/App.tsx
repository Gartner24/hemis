import { Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './features/auth/ProtectedRoute';
import LoginPage from './features/auth/LoginPage';
import MedicDashboard from './features/dashboard/MedicDashboard';
import PatientList from './features/patients/PatientList';
import PatientDetail from './features/patients/PatientDetail';
import RealTimeMonitoring from './features/telemetry/RealTimeMonitoring';
import VitalSignsSimulator from './features/telemetry/VitalSignsSimulator';
import Layout from './components/layout/Layout';

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<MedicDashboard />} />
          <Route path="patients" element={<PatientList />} />
          <Route path="patients/:patientId" element={<PatientDetail />} />
          <Route path="telemetry" element={<RealTimeMonitoring />} />
          <Route path="simulator" element={<VitalSignsSimulator />} />
        </Route>
      </Routes>
    </AuthProvider>
  );
}

export default App;
