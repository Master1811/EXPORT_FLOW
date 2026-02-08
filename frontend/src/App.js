import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { DashboardLayout } from './components/DashboardLayout';
import { Toaster } from './components/ui/sonner';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import ShipmentsPage from './pages/ShipmentsPage';
import DocumentsPage from './pages/DocumentsPage';
import PaymentsPage from './pages/PaymentsPage';
import ForexPage from './pages/ForexPage';
import CompliancePage from './pages/CompliancePage';
import IncentivesPage from './pages/IncentivesPage';
import AIPage from './pages/AIPage';
import CreditPage from './pages/CreditPage';
import ConnectorsPage from './pages/ConnectorsPage';
import NotificationsPage from './pages/NotificationsPage';
import SettingsPage from './pages/SettingsPage';
import './App.css';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <DashboardLayout>{children}</DashboardLayout>;
};

const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }
  
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }
  
  return children;
};

function AppRoutes() {
  return (
    <Routes>
      {/* Landing Page (Public) */}
      <Route path="/" element={<LandingPage />} />
      
      {/* Auth Routes */}
      <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
      <Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />
      
      {/* Protected Routes */}
      <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
      <Route path="/shipments" element={<ProtectedRoute><ShipmentsPage /></ProtectedRoute>} />
      <Route path="/documents" element={<ProtectedRoute><DocumentsPage /></ProtectedRoute>} />
      <Route path="/payments" element={<ProtectedRoute><PaymentsPage /></ProtectedRoute>} />
      <Route path="/forex" element={<ProtectedRoute><ForexPage /></ProtectedRoute>} />
      <Route path="/compliance" element={<ProtectedRoute><CompliancePage /></ProtectedRoute>} />
      <Route path="/incentives" element={<ProtectedRoute><IncentivesPage /></ProtectedRoute>} />
      <Route path="/ai" element={<ProtectedRoute><AIPage /></ProtectedRoute>} />
      <Route path="/credit" element={<ProtectedRoute><CreditPage /></ProtectedRoute>} />
      <Route path="/connectors" element={<ProtectedRoute><ConnectorsPage /></ProtectedRoute>} />
      <Route path="/notifications" element={<ProtectedRoute><NotificationsPage /></ProtectedRoute>} />
      <Route path="/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />
      
      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <div className="App noise-overlay">
      <BrowserRouter>
        <AuthProvider>
          <AppRoutes />
          <Toaster position="top-right" richColors />
        </AuthProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;
