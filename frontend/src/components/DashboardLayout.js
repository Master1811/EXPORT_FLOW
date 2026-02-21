import React, { useState, useCallback } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth, api } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { 
  Ship, LayoutDashboard, Package, FileText, CreditCard, 
  TrendingUp, Calculator, Brain, Users, Link2, Bell, 
  Settings, LogOut, ChevronLeft, ChevronRight, Menu, X, Shield, Clock
} from 'lucide-react';

const navItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
  { icon: Package, label: 'Shipments', path: '/shipments' },
  { icon: FileText, label: 'Documents', path: '/documents' },
  { icon: CreditCard, label: 'Payments', path: '/payments' },
  { icon: Clock, label: 'RBI Risk Clock', path: '/risk-clock' },
  { icon: TrendingUp, label: 'Forex', path: '/forex' },
  { icon: Calculator, label: 'GST & Compliance', path: '/compliance' },
  { icon: Calculator, label: 'Incentives', path: '/incentives' },
  { icon: Brain, label: 'AI Assistant', path: '/ai' },
  { icon: Users, label: 'Credit', path: '/credit' },
  { icon: Link2, label: 'Connectors', path: '/connectors' },
];

// Prefetch map to avoid redundant prefetches
const prefetchedRoutes = new Set();

// NavLink with prefetch on hover
const NavLink = React.memo(({ item, isActive, collapsed, onNavigate }) => {
  const Icon = item.icon;
  
  const handleMouseEnter = useCallback(() => {
    // Prefetch route chunk on hover (only once)
    if (!prefetchedRoutes.has(item.path)) {
      prefetchedRoutes.add(item.path);
      // The dynamic import triggers webpack to load the chunk
      const routeImports = {
        '/dashboard': () => import('../pages/DashboardPage'),
        '/shipments': () => import('../pages/ShipmentsPage'),
        '/documents': () => import('../pages/DocumentsPage'),
        '/payments': () => import('../pages/PaymentsPage'),
        '/risk-clock': () => import('../pages/RiskClockPage'),
        '/forex': () => import('../pages/ForexPage'),
        '/compliance': () => import('../pages/CompliancePage'),
        '/incentives': () => import('../pages/IncentivesPage'),
        '/ai': () => import('../pages/AIPage'),
        '/credit': () => import('../pages/CreditPage'),
        '/connectors': () => import('../pages/ConnectorsPage'),
      };
      
      const importFn = routeImports[item.path];
      if (importFn) {
        // Use requestIdleCallback for non-blocking prefetch
        if (window.requestIdleCallback) {
          window.requestIdleCallback(() => importFn().catch(() => {}));
        } else {
          setTimeout(() => importFn().catch(() => {}), 100);
        }
      }
    }
  }, [item.path]);

  return (
    <Link
      to={item.path}
      onClick={onNavigate}
      onMouseEnter={handleMouseEnter}
      className={`
        flex items-center gap-3 px-3 py-2.5 rounded-md
        transition-colors duration-200
        ${isActive 
          ? 'bg-primary/10 text-primary border-l-2 border-primary' 
          : 'text-muted-foreground hover:bg-surface-highlight hover:text-foreground'
        }
      `}
      data-testid={`nav-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
    >
      <Icon className="w-5 h-5 flex-shrink-0" strokeWidth={1.5} />
      {!collapsed && <span className="text-sm">{item.label}</span>}
    </Link>
  );
});

NavLink.displayName = 'NavLink';

export const DashboardLayout = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      // Call backend logout to blacklist token
      await api.post('/auth/logout');
    } catch (error) {
      // Continue with logout even if API call fails
      console.error('Logout API error:', error);
    }
    // Navigate first, then clear auth state
    // This prevents ProtectedRoute from redirecting to /login
    navigate('/');
    // Small delay to allow navigation to complete
    setTimeout(() => {
      logout();
    }, 100);
  };

  return (
    <div className="min-h-screen bg-background flex" data-testid="dashboard-layout">
      {/* Mobile Overlay */}
      {mobileOpen && (
        <div 
          className="lg:hidden fixed inset-0 bg-black/50 z-40"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside 
        className={`
          fixed lg:static inset-y-0 left-0 z-50
          ${collapsed ? 'w-20' : 'w-64'}
          ${mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
          bg-surface border-r border-border
          flex flex-col
          transition-all duration-300
        `}
        data-testid="sidebar"
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-border">
          <Link to="/dashboard" className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-md bg-primary flex items-center justify-center flex-shrink-0">
              <Ship className="w-6 h-6 text-white" strokeWidth={1.5} />
            </div>
            {!collapsed && <span className="font-heading text-xl text-white">ExportFlow</span>}
          </Link>
          <button 
            onClick={() => setMobileOpen(false)}
            className="lg:hidden text-muted-foreground hover:text-foreground"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-4 overflow-y-auto">
          <ul className="space-y-1 px-3">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <li key={item.path}>
                  <NavLink
                    item={item}
                    isActive={isActive}
                    collapsed={collapsed}
                    onNavigate={() => setMobileOpen(false)}
                  />
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Bottom Section */}
        <div className="border-t border-border p-3 space-y-1">
          <Link
            to="/security"
            className="flex items-center gap-3 px-3 py-2.5 rounded-md text-muted-foreground hover:bg-surface-highlight hover:text-foreground transition-colors"
            data-testid="nav-security"
          >
            <Shield className="w-5 h-5" strokeWidth={1.5} />
            {!collapsed && <span className="text-sm">Security & Audit</span>}
          </Link>
          <Link
            to="/notifications"
            className="flex items-center gap-3 px-3 py-2.5 rounded-md text-muted-foreground hover:bg-surface-highlight hover:text-foreground transition-colors"
            data-testid="nav-notifications"
          >
            <Bell className="w-5 h-5" strokeWidth={1.5} />
            {!collapsed && <span className="text-sm">Notifications</span>}
          </Link>
          <Link
            to="/settings"
            className="flex items-center gap-3 px-3 py-2.5 rounded-md text-muted-foreground hover:bg-surface-highlight hover:text-foreground transition-colors"
            data-testid="nav-settings"
          >
            <Settings className="w-5 h-5" strokeWidth={1.5} />
            {!collapsed && <span className="text-sm">Settings</span>}
          </Link>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-destructive hover:bg-destructive/10 transition-colors"
            data-testid="logout-btn"
          >
            <LogOut className="w-5 h-5" strokeWidth={1.5} />
            {!collapsed && <span className="text-sm">Logout</span>}
          </button>
        </div>

        {/* Collapse Toggle - Desktop only */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="hidden lg:flex absolute -right-3 top-20 w-6 h-6 rounded-full bg-surface border border-border items-center justify-center hover:bg-surface-highlight transition-colors"
          data-testid="collapse-sidebar-btn"
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Bar */}
        <header className="h-16 border-b border-border bg-surface/50 backdrop-blur-sm flex items-center justify-between px-4 lg:px-8 sticky top-0 z-30">
          <button
            onClick={() => setMobileOpen(true)}
            className="lg:hidden text-muted-foreground hover:text-foreground"
            data-testid="mobile-menu-btn"
          >
            <Menu className="w-6 h-6" />
          </button>

          <div className="flex items-center gap-4 ml-auto">
            <Button variant="ghost" size="sm" className="relative" data-testid="notifications-btn">
              <Bell className="w-5 h-5" strokeWidth={1.5} />
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-destructive rounded-full text-xs flex items-center justify-center">3</span>
            </Button>
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-primary/20 flex items-center justify-center text-primary font-medium">
                {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
              </div>
              <div className="hidden sm:block">
                <p className="text-sm font-medium text-foreground">{user?.full_name || 'User'}</p>
                <p className="text-xs text-muted-foreground">{user?.email}</p>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 p-4 lg:p-8 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
