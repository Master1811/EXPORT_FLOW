import React, { Suspense, lazy, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { AuthProvider, useAuth } from './context/AuthContext';
import { DashboardLayout } from './components/DashboardLayout';
import { ErrorBoundary, RouteErrorBoundary } from './components/ErrorBoundary';
import { Toaster } from './components/ui/sonner';
import './App.css';

// Loading spinner component
const PageLoader = () => (
  <div className="min-h-screen bg-background flex items-center justify-center">
    <div className="text-center">
      <div className="w-10 h-10 border-3 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
      <p className="text-muted-foreground text-sm">Loading...</p>
    </div>
  </div>
);

// Lazy load all page components for code splitting
const LandingPage = lazy(() => import('./pages/LandingPage'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const RegisterPage = lazy(() => import('./pages/RegisterPage'));
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const ShipmentsPage = lazy(() => import('./pages/ShipmentsPage'));
const DocumentsPage = lazy(() => import('./pages/DocumentsPage'));
const PaymentsPage = lazy(() => import('./pages/PaymentsPage'));
const ForexPage = lazy(() => import('./pages/ForexPage'));
const CompliancePage = lazy(() => import('./pages/CompliancePage'));
const IncentivesPage = lazy(() => import('./pages/IncentivesPage'));
const AIPage = lazy(() => import('./pages/AIPage'));
const CreditPage = lazy(() => import('./pages/CreditPage'));
const ConnectorsPage = lazy(() => import('./pages/ConnectorsPage'));
const NotificationsPage = lazy(() => import('./pages/NotificationsPage'));
const SettingsPage = lazy(() => import('./pages/SettingsPage'));
const AuditLogsPage = lazy(() => import('./pages/AuditLogsPage'));
const RiskClockPage = lazy(() => import('./pages/RiskClockPage'));

// Route configuration for maintainability
const ROUTE_CONFIG = {
  dashboard: { path: '/dashboard', title: 'Dashboard - ExportFlow' },
  shipments: { path: '/shipments', title: 'Shipments - ExportFlow' },
  documents: { path: '/documents', title: 'Documents - ExportFlow' },
  payments: { path: '/payments', title: 'Payments - ExportFlow' },
  forex: { path: '/forex', title: 'Forex - ExportFlow' },
  compliance: { path: '/compliance', title: 'Compliance - ExportFlow' },
  incentives: { path: '/incentives', title: 'Incentives - ExportFlow' },
  ai: { path: '/ai', title: 'AI Assistant - ExportFlow' },
  credit: { path: '/credit', title: 'Credit - ExportFlow' },
  connectors: { path: '/connectors', title: 'Connectors - ExportFlow' },
  notifications: { path: '/notifications', title: 'Notifications - ExportFlow' },
  settings: { path: '/settings', title: 'Settings - ExportFlow' },
  security: { path: '/security', title: 'Security & Audit - ExportFlow' },
  riskClock: { path: '/risk-clock', title: 'RBI Risk Clock - ExportFlow' },
};

// Document title manager
const DocumentTitle = ({ title }) => {
  useEffect(() => {
    const previousTitle = document.title;
    document.title = title || 'ExportFlow - Exporter Finance Platform';
    return () => {
      document.title = previousTitle;
    };
  }, [title]);
  return null;
};

// Enhanced Protected Route with error boundary and document title
const ProtectedRoute = ({ children, title }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <PageLoader />;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return (
    <RouteErrorBoundary>
      <DocumentTitle title={title} />
      <DashboardLayout>{children}</DashboardLayout>
    </RouteErrorBoundary>
  );
};

// Public Route component
const PublicRoute = ({ children, title }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <PageLoader />;
  }
  
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }
  
  return (
    <RouteErrorBoundary>
      <DocumentTitle title={title} />
      {children}
    </RouteErrorBoundary>
  );
};

// Focus management for accessibility
const FocusManager = () => {
  const location = useLocation();
  
  useEffect(() => {
    // Reset focus to top of page on route change
    const mainContent = document.getElementById('main-content');
    if (mainContent) {
      mainContent.focus();
    } else {
      window.scrollTo(0, 0);
    }
  }, [location.pathname]);
  
  return null;
};

// Skip link for accessibility
const SkipLink = () => (
  <a
    href="#main-content"
    className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:bg-primary focus:text-primary-foreground focus:px-4 focus:py-2 focus:rounded"
  >
    Skip to main content
  </a>
);

function AppRoutes() {
  return (
    <>
      <SkipLink />
      <FocusManager />
      <Suspense fallback={<PageLoader />}>
        <Routes>
          {/* Landing Page (Public) */}
          <Route 
            path="/" 
            element={
              <RouteErrorBoundary>
                <DocumentTitle title="ExportFlow - Exporter Finance Platform" />
                <LandingPage />
              </RouteErrorBoundary>
            } 
          />
          
          {/* Auth Routes */}
          <Route 
            path="/login" 
            element={
              <PublicRoute title="Login - ExportFlow">
                <LoginPage />
              </PublicRoute>
            } 
          />
          <Route 
            path="/register" 
            element={
              <PublicRoute title="Register - ExportFlow">
                <RegisterPage />
              </PublicRoute>
            } 
          />
          
          {/* Protected Routes */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute title={ROUTE_CONFIG.dashboard.title}>
                <DashboardPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/shipments" 
            element={
              <ProtectedRoute title={ROUTE_CONFIG.shipments.title}>
                <ShipmentsPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/documents" 
            element={
              <ProtectedRoute title={ROUTE_CONFIG.documents.title}>
                <DocumentsPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/payments" 
            element={
              <ProtectedRoute title={ROUTE_CONFIG.payments.title}>
                <PaymentsPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/forex" 
            element={
              <ProtectedRoute title={ROUTE_CONFIG.forex.title}>
                <ForexPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/compliance" 
            element={
              <ProtectedRoute title={ROUTE_CONFIG.compliance.title}>
                <CompliancePage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/incentives" 
            element={
              <ProtectedRoute title={ROUTE_CONFIG.incentives.title}>
                <IncentivesPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/ai" 
            element={
              <ProtectedRoute title={ROUTE_CONFIG.ai.title}>
                <AIPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/credit" 
            element={
              <ProtectedRoute title={ROUTE_CONFIG.credit.title}>
                <CreditPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/connectors" 
            element={
              <ProtectedRoute title={ROUTE_CONFIG.connectors.title}>
                <ConnectorsPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/notifications" 
            element={
              <ProtectedRoute title={ROUTE_CONFIG.notifications.title}>
                <NotificationsPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/settings" 
            element={
              <ProtectedRoute title={ROUTE_CONFIG.settings.title}>
                <SettingsPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/security" 
            element={
              <ProtectedRoute title={ROUTE_CONFIG.security.title}>
                <AuditLogsPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/audit-logs" 
            element={
              <ProtectedRoute title={ROUTE_CONFIG.security.title}>
                <AuditLogsPage />
              </ProtectedRoute>
            } 
          />
          
          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Suspense>
    </>
  );
}

function App() {
  return (
    <ErrorBoundary message="The application encountered an unexpected error. Please refresh the page.">
      <div className="App noise-overlay" id="main-content" tabIndex={-1}>
        <HelmetProvider>
        <BrowserRouter>
          <AuthProvider>
            <AppRoutes />
            <Toaster position="top-right" richColors />
          </AuthProvider>
        </BrowserRouter>
        </HelmetProvider>
      </div>
    </ErrorBoundary>
  );
}

export default App;
