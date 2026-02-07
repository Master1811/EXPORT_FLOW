import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import {
  TrendingUp, TrendingDown, Package, CreditCard, Calculator,
  AlertTriangle, ArrowUpRight, RefreshCw, Ship, DollarSign,
  FileCheck, Percent, Sparkles, Target, Zap, Clock, ChevronRight,
  BarChart3, PieChart as PieChartIcon, Activity, Eye, Calendar
} from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell, AreaChart, Area, BarChart, Bar
} from 'recharts';
import EmptyState from '../components/EmptyState';
import QuickStartTutorial from '../components/QuickStartTutorial';

const CHART_COLORS = {
  primary: '#8B5CF6',
  success: '#10B981',
  warning: '#F59E0B',
  danger: '#EF4444',
  info: '#3B82F6',
  secondary: '#6366F1'
};

const formatCurrency = (value, currency = 'INR') => {
  if (currency === 'INR') {
    if (value >= 10000000) return `₹${(value / 10000000).toFixed(2)}Cr`;
    if (value >= 100000) return `₹${(value / 100000).toFixed(2)}L`;
    return `₹${value.toLocaleString('en-IN')}`;
  }
  return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(value);
};

const GlowCard = ({ children, className = '', glowColor = 'violet', ...props }) => (
  <Card 
    className={`relative overflow-hidden bg-zinc-900/50 border-zinc-800 hover:border-zinc-700 transition-all duration-300 ${className}`}
    {...props}
  >
    <div className={`absolute inset-0 bg-gradient-to-br from-${glowColor}-500/5 to-transparent pointer-events-none`} />
    {children}
  </Card>
);

export default function DashboardPage() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [exportTrend, setExportTrend] = useState([]);
  const [paymentStatus, setPaymentStatus] = useState([]);
  const [riskAlerts, setRiskAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showTutorial, setShowTutorial] = useState(false);

  useEffect(() => {
    fetchDashboardData();
    // Show tutorial for new users
    const skipped = localStorage.getItem('quickstart_skipped');
    const completed = localStorage.getItem('quickstart_completed');
    if (!skipped && !completed) {
      // Check if user has any shipments
      setTimeout(() => {
        if (stats?.total_shipments === 0) {
          setShowTutorial(true);
        }
      }, 1000);
    }
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, trendRes, statusRes, alertsRes] = await Promise.all([
        api.get('/dashboard/stats'),
        api.get('/dashboard/charts/export-trend'),
        api.get('/dashboard/charts/payment-status'),
        api.get('/ai/risk-alerts')
      ]);

      setStats(statsRes.data);
      setExportTrend(trendRes.data.labels.map((label, i) => ({
        month: label,
        value: trendRes.data.data[i]
      })));
      setPaymentStatus(statusRes.data.labels.map((label, i) => ({
        name: label,
        value: statusRes.data.data[i]
      })));
      setRiskAlerts(alertsRes.data.alerts);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTutorialComplete = () => {
    localStorage.setItem('quickstart_completed', 'true');
    fetchDashboardData();
  };

  // Enhanced Stat Card with gradient and animation
  const StatCard = ({ title, value, change, icon: Icon, trend, color = 'violet', subtext, onClick }) => (
    <GlowCard 
      glowColor={color}
      className="cursor-pointer group hover:scale-[1.02] transition-transform"
      onClick={onClick}
      data-testid={`stat-${title.toLowerCase().replace(/\s+/g, '-')}`}
    >
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <p className="text-sm text-zinc-400 flex items-center gap-1">
              {title}
              {onClick && <ChevronRight className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />}
            </p>
            <p className="text-3xl font-bold bg-gradient-to-r from-white to-zinc-400 bg-clip-text text-transparent">
              {value}
            </p>
            {subtext && <p className="text-xs text-zinc-500">{subtext}</p>}
          </div>
          <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br from-${color}-500/20 to-${color}-600/10 flex items-center justify-center border border-${color}-500/20`}>
            <Icon className={`w-7 h-7 text-${color}-400`} strokeWidth={1.5} />
          </div>
        </div>
        {change !== undefined && (
          <div className="flex items-center gap-2 mt-4 pt-4 border-t border-zinc-800">
            <div className={`flex items-center gap-1 px-2 py-1 rounded-full ${
              trend === 'up' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'
            }`}>
              {trend === 'up' ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
              <span className="text-xs font-medium">{Math.abs(change)}%</span>
            </div>
            <span className="text-xs text-zinc-500">vs last month</span>
          </div>
        )}
      </CardContent>
    </GlowCard>
  );

  // Quick Action Button
  const QuickAction = ({ icon: Icon, label, color, onClick }) => (
    <button
      onClick={onClick}
      className={`flex flex-col items-center gap-2 p-4 rounded-xl bg-zinc-800/50 hover:bg-zinc-800 border border-zinc-700/50 hover:border-${color}-500/30 transition-all group`}
    >
      <div className={`w-10 h-10 rounded-lg bg-${color}-500/10 flex items-center justify-center group-hover:scale-110 transition-transform`}>
        <Icon className={`w-5 h-5 text-${color}-400`} />
      </div>
      <span className="text-xs text-zinc-400 group-hover:text-zinc-300">{label}</span>
    </button>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="text-center">
          <div className="w-16 h-16 rounded-2xl bg-violet-500/10 flex items-center justify-center mx-auto mb-4 animate-pulse">
            <Activity className="w-8 h-8 text-violet-400" />
          </div>
          <p className="text-zinc-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in" data-testid="dashboard-page">
      {/* Quick Start Tutorial */}
      <QuickStartTutorial 
        open={showTutorial} 
        onClose={() => setShowTutorial(false)}
        onComplete={handleTutorialComplete}
      />

      {/* Check for empty state - new users with no data */}
      {stats?.total_shipments === 0 ? (
        <>
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-white via-zinc-200 to-zinc-400 bg-clip-text text-transparent">
                Dashboard
              </h1>
              <p className="text-zinc-400 mt-1">Overview of your export operations</p>
            </div>
            <Button 
              onClick={() => setShowTutorial(true)}
              className="bg-violet-600 hover:bg-violet-700"
            >
              <Sparkles className="w-4 h-4 mr-2" />
              Quick Start Guide
            </Button>
          </div>
          <EmptyState type="dashboard" />
        </>
      ) : (
        <>
          {/* Header with gradient */}
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-white via-zinc-200 to-zinc-400 bg-clip-text text-transparent">
                Dashboard
              </h1>
              <p className="text-zinc-400 mt-1">Overview of your export operations</p>
            </div>
            <div className="flex gap-2">
              <Button 
                onClick={() => setShowTutorial(true)}
                variant="outline" 
                className="border-zinc-700 hover:bg-zinc-800"
              >
                <Sparkles className="w-4 h-4 mr-2" />
                Quick Start
              </Button>
              <Button 
                onClick={fetchDashboardData} 
                variant="outline" 
                className="border-zinc-700 hover:bg-zinc-800"
                data-testid="refresh-dashboard-btn"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>

          {/* Stats Grid - Enhanced */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="Total Export Value"
              value={formatCurrency(stats?.total_export_value || 0)}
              change={12}
              trend="up"
              icon={Ship}
              color="blue"
              onClick={() => navigate('/shipments')}
            />
            <StatCard
              title="Outstanding Receivables"
              value={formatCurrency(stats?.total_receivables || 0)}
              change={-5}
              trend="down"
              icon={CreditCard}
              color="amber"
              onClick={() => navigate('/payments')}
            />
            <StatCard
              title="Incentives Earned"
              value={formatCurrency(stats?.total_incentives_earned || 0)}
              change={18}
              trend="up"
              icon={Percent}
              color="emerald"
              onClick={() => navigate('/incentives')}
            />
            <StatCard
              title="Pending GST Refund"
              value={formatCurrency(stats?.pending_gst_refund || 0)}
              icon={Calculator}
              color="violet"
              subtext="Expected in 45 days"
              onClick={() => navigate('/gst')}
            />
          </div>

          {/* Quick Actions */}
          <GlowCard glowColor="zinc" className="border-zinc-800">
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-zinc-400">Quick Actions</h3>
                <Zap className="w-4 h-4 text-amber-400" />
              </div>
              <div className="grid grid-cols-4 md:grid-cols-8 gap-3">
                <QuickAction icon={Ship} label="New Shipment" color="blue" onClick={() => navigate('/shipments')} />
                <QuickAction icon={CreditCard} label="Record Payment" color="emerald" onClick={() => navigate('/payments')} />
                <QuickAction icon={FileCheck} label="Upload Doc" color="violet" onClick={() => navigate('/documents')} />
                <QuickAction icon={Calculator} label="GST Calculator" color="amber" onClick={() => navigate('/gst')} />
                <QuickAction icon={Target} label="Incentives" color="pink" onClick={() => navigate('/incentives')} />
                <QuickAction icon={BarChart3} label="Reports" color="cyan" onClick={() => navigate('/payments')} />
                <QuickAction icon={Eye} label="AI Insights" color="indigo" onClick={() => navigate('/ai-assistant')} />
                <QuickAction icon={Calendar} label="e-BRC Track" color="orange" onClick={() => navigate('/shipments')} />
              </div>
            </CardContent>
          </GlowCard>

          {/* Charts Row - Enhanced */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Export Trend Chart */}
            <GlowCard glowColor="blue" className="lg:col-span-2" data-testid="export-trend-chart">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg flex items-center gap-2 text-white">
                    <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center">
                      <TrendingUp className="w-4 h-4 text-blue-400" />
                    </div>
                    Export Trend
                  </CardTitle>
                  <Badge className="bg-blue-500/10 text-blue-400 border-blue-500/20">
                    Last 6 months
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={exportTrend}>
                      <defs>
                        <linearGradient id="colorExportNew" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.4}/>
                          <stop offset="50%" stopColor="#3B82F6" stopOpacity={0.1}/>
                          <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#27272A" vertical={false} />
                      <XAxis 
                        dataKey="month" 
                        stroke="#52525B" 
                        fontSize={12} 
                        axisLine={false}
                        tickLine={false}
                      />
                      <YAxis 
                        stroke="#52525B" 
                        fontSize={12} 
                        tickFormatter={(v) => `₹${v/100000}L`}
                        axisLine={false}
                        tickLine={false}
                      />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: '#18181B', 
                          border: '1px solid #3F3F46',
                          borderRadius: '12px',
                          boxShadow: '0 4px 24px rgba(0,0,0,0.4)'
                        }}
                        labelStyle={{ color: '#A1A1AA' }}
                        formatter={(value) => [formatCurrency(value), 'Export Value']}
                      />
                      <Area 
                        type="monotone" 
                        dataKey="value" 
                        stroke="#3B82F6" 
                        fillOpacity={1} 
                        fill="url(#colorExportNew)" 
                        strokeWidth={3}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </GlowCard>

            {/* Payment Status Donut Chart */}
            <GlowCard glowColor="emerald" data-testid="payment-status-chart">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg flex items-center gap-2 text-white">
                    <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                      <PieChartIcon className="w-4 h-4 text-emerald-400" />
                    </div>
                    Payment Status
                  </CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <div className="h-[200px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={paymentStatus}
                        cx="50%"
                        cy="50%"
                        innerRadius={55}
                        outerRadius={80}
                        paddingAngle={4}
                        dataKey="value"
                        strokeWidth={0}
                      >
                        {paymentStatus.map((entry, index) => {
                          const colors = [CHART_COLORS.success, CHART_COLORS.warning, CHART_COLORS.danger];
                          return <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />;
                        })}
                      </Pie>
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: '#18181B', 
                          border: '1px solid #3F3F46',
                          borderRadius: '12px'
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                {/* Legend */}
                <div className="flex flex-wrap justify-center gap-4 mt-4">
                  {paymentStatus.map((item, i) => {
                    const colors = ['#10B981', '#F59E0B', '#EF4444'];
                    return (
                      <div key={item.name} className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: colors[i] }} />
                        <span className="text-xs text-zinc-400">{item.name}</span>
                        <span className="text-xs font-medium text-zinc-300">{item.value}</span>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </GlowCard>
          </div>

          {/* Bottom Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Quick Stats - Enhanced */}
            <GlowCard glowColor="violet" data-testid="quick-stats-card">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2 text-white">
                  <div className="w-8 h-8 rounded-lg bg-violet-500/10 flex items-center justify-center">
                    <Package className="w-4 h-4 text-violet-400" />
                  </div>
                  Performance Overview
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-5">
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-zinc-400">Active Shipments</span>
                    <span className="font-medium text-white">{stats?.active_shipments || 0}</span>
                  </div>
                  <Progress value={(stats?.active_shipments / Math.max(stats?.total_shipments, 1)) * 100} className="h-2 bg-zinc-800" />
                </div>
                
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-zinc-400">Compliance Score</span>
                    <span className={`font-medium ${stats?.compliance_score >= 80 ? 'text-emerald-400' : 'text-amber-400'}`}>
                      {stats?.compliance_score || 0}%
                    </span>
                  </div>
                  <Progress 
                    value={stats?.compliance_score || 0} 
                    className="h-2 bg-zinc-800"
                  />
                </div>

                <div className="pt-4 border-t border-zinc-800 grid grid-cols-2 gap-4">
                  <div className="p-3 rounded-xl bg-zinc-800/50 border border-zinc-700/50">
                    <p className="text-xs text-zinc-500 mb-1">Total Shipments</p>
                    <p className="text-xl font-bold text-white">{stats?.total_shipments || 0}</p>
                  </div>
                  <div className="p-3 rounded-xl bg-zinc-800/50 border border-zinc-700/50">
                    <p className="text-xs text-zinc-500 mb-1">Payments Received</p>
                    <p className="text-xl font-bold text-emerald-400">{formatCurrency(stats?.total_payments_received || 0)}</p>
                  </div>
                </div>
              </CardContent>
            </GlowCard>

            {/* Risk Alerts - Enhanced */}
            <GlowCard glowColor="amber" data-testid="risk-alerts-card">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg flex items-center gap-2 text-white">
                    <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
                      <AlertTriangle className="w-4 h-4 text-amber-400" />
                    </div>
                    Risk Alerts
                  </CardTitle>
                  <Badge className="bg-amber-500/10 text-amber-400 border-amber-500/20">
                    {riskAlerts.length} alerts
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {riskAlerts.slice(0, 4).map((alert, index) => (
                  <div 
                    key={index} 
                    className={`p-4 rounded-xl border transition-all hover:scale-[1.01] cursor-pointer ${
                      alert.severity === 'high' 
                        ? 'bg-red-500/5 border-red-500/20 hover:border-red-500/40' 
                        : alert.severity === 'medium'
                        ? 'bg-amber-500/5 border-amber-500/20 hover:border-amber-500/40'
                        : 'bg-blue-500/5 border-blue-500/20 hover:border-blue-500/40'
                    }`}
                    data-testid={`alert-${index}`}
                  >
                    <div className="flex items-start gap-3">
                      <Badge 
                        className={`text-xs ${
                          alert.severity === 'high' ? 'bg-red-500/20 text-red-400 border-red-500/30' :
                          alert.severity === 'medium' ? 'bg-amber-500/20 text-amber-400 border-amber-500/30' :
                          'bg-blue-500/20 text-blue-400 border-blue-500/30'
                        }`}
                      >
                        {alert.severity}
                      </Badge>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-white truncate">{alert.message}</p>
                        <p className="text-xs text-zinc-500 mt-1 flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {alert.action}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
                {riskAlerts.length > 4 && (
                  <Button 
                    variant="ghost" 
                    className="w-full text-zinc-400 hover:text-white"
                    onClick={() => navigate('/ai-assistant')}
                  >
                    View all {riskAlerts.length} alerts
                    <ArrowUpRight className="w-4 h-4 ml-2" />
                  </Button>
                )}
              </CardContent>
            </GlowCard>
          </div>
        </>
      )}
    </div>
  );
}
