import React, { useState, useEffect } from 'react';
import { api } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import {
  TrendingUp, TrendingDown, Package, CreditCard, Calculator,
  AlertTriangle, ArrowUpRight, RefreshCw, Ship, DollarSign,
  FileCheck, Percent
} from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell, AreaChart, Area
} from 'recharts';
import EmptyState from '../components/EmptyState';

const CHART_COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

const formatCurrency = (value, currency = 'INR') => {
  if (currency === 'INR') {
    if (value >= 10000000) return `₹${(value / 10000000).toFixed(2)}Cr`;
    if (value >= 100000) return `₹${(value / 100000).toFixed(2)}L`;
    return `₹${value.toLocaleString('en-IN')}`;
  }
  return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(value);
};

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [exportTrend, setExportTrend] = useState([]);
  const [paymentStatus, setPaymentStatus] = useState([]);
  const [riskAlerts, setRiskAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
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

  const StatCard = ({ title, value, change, icon: Icon, trend, color = 'primary', subtext }) => (
    <Card className="bg-card border-border hover:border-primary/50 transition-colors" data-testid={`stat-${title.toLowerCase().replace(/\s+/g, '-')}`}>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm text-muted-foreground mb-1">{title}</p>
            <p className="text-2xl font-heading font-bold text-foreground">{value}</p>
            {subtext && <p className="text-xs text-muted-foreground mt-1">{subtext}</p>}
          </div>
          <div className={`w-12 h-12 rounded-md bg-${color}/10 flex items-center justify-center`}>
            <Icon className={`w-6 h-6 text-${color}`} strokeWidth={1.5} />
          </div>
        </div>
        {change !== undefined && (
          <div className="flex items-center gap-1 mt-3">
            {trend === 'up' ? (
              <TrendingUp className="w-4 h-4 text-neon" />
            ) : (
              <TrendingDown className="w-4 h-4 text-destructive" />
            )}
            <span className={trend === 'up' ? 'text-neon text-sm' : 'text-destructive text-sm'}>
              {change}%
            </span>
            <span className="text-muted-foreground text-sm ml-1">vs last month</span>
          </div>
        )}
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <RefreshCw className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in" data-testid="dashboard-page">
      {/* Check for empty state - new users with no data */}
      {stats?.total_shipments === 0 ? (
        <>
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="font-heading text-4xl text-foreground">Dashboard</h1>
              <p className="text-muted-foreground mt-1">Overview of your export operations</p>
            </div>
          </div>
          <EmptyState type="dashboard" />
        </>
      ) : (
        <>
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="font-heading text-4xl text-foreground">Dashboard</h1>
          <p className="text-muted-foreground mt-1">Overview of your export operations</p>
        </div>
        <Button onClick={fetchDashboardData} variant="outline" className="w-fit" data-testid="refresh-dashboard-btn">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Export Value"
          value={formatCurrency(stats?.total_export_value || 0)}
          change={12}
          trend="up"
          icon={Ship}
          color="primary"
        />
        <StatCard
          title="Outstanding Receivables"
          value={formatCurrency(stats?.total_receivables || 0)}
          change={-5}
          trend="down"
          icon={CreditCard}
          color="amber"
        />
        <StatCard
          title="Incentives Earned"
          value={formatCurrency(stats?.total_incentives_earned || 0)}
          change={18}
          trend="up"
          icon={Percent}
          color="neon"
        />
        <StatCard
          title="Pending GST Refund"
          value={formatCurrency(stats?.pending_gst_refund || 0)}
          icon={Calculator}
          color="primary"
          subtext="Expected in 45 days"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Export Trend Chart */}
        <Card className="lg:col-span-2 bg-card border-border" data-testid="export-trend-chart">
          <CardHeader className="pb-2">
            <CardTitle className="font-heading text-lg flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-primary" />
              Export Trend
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[280px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={exportTrend}>
                  <defs>
                    <linearGradient id="colorExport" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                  <XAxis dataKey="month" stroke="#71717A" fontSize={12} />
                  <YAxis stroke="#71717A" fontSize={12} tickFormatter={(v) => `₹${v/1000}K`} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#18181B', 
                      border: '1px solid #27272A',
                      borderRadius: '6px'
                    }}
                    formatter={(value) => [formatCurrency(value), 'Export Value']}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="value" 
                    stroke="#3B82F6" 
                    fillOpacity={1} 
                    fill="url(#colorExport)" 
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Payment Status Pie Chart */}
        <Card className="bg-card border-border" data-testid="payment-status-chart">
          <CardHeader className="pb-2">
            <CardTitle className="font-heading text-lg flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-neon" />
              Payment Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[220px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={paymentStatus}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {paymentStatus.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#18181B', 
                      border: '1px solid #27272A',
                      borderRadius: '6px'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center gap-4 mt-2">
              {paymentStatus.map((item, i) => (
                <div key={item.name} className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: CHART_COLORS[i] }} />
                  <span className="text-xs text-muted-foreground">{item.name}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Bottom Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quick Stats */}
        <Card className="bg-card border-border" data-testid="quick-stats-card">
          <CardHeader>
            <CardTitle className="font-heading text-lg flex items-center gap-2">
              <Package className="w-5 h-5 text-primary" />
              Quick Stats
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Active Shipments</span>
              <span className="font-medium text-foreground">{stats?.active_shipments || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Total Shipments</span>
              <span className="font-medium text-foreground">{stats?.total_shipments || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Compliance Score</span>
              <div className="flex items-center gap-2">
                <Progress value={stats?.compliance_score || 0} className="w-24 h-2" />
                <span className="font-medium text-neon">{stats?.compliance_score || 0}%</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Payments Received</span>
              <span className="font-medium text-foreground">{formatCurrency(stats?.total_payments_received || 0)}</span>
            </div>
          </CardContent>
        </Card>

        {/* Risk Alerts */}
        <Card className="bg-card border-border" data-testid="risk-alerts-card">
          <CardHeader>
            <CardTitle className="font-heading text-lg flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-amber" />
              Risk Alerts
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {riskAlerts.map((alert, index) => (
              <div 
                key={index} 
                className="p-3 rounded-md bg-surface-highlight/50 border border-border hover:border-primary/30 transition-colors"
                data-testid={`alert-${index}`}
              >
                <div className="flex items-start gap-3">
                  <Badge 
                    variant={alert.severity === 'high' ? 'destructive' : alert.severity === 'medium' ? 'warning' : 'default'}
                    className={`mt-0.5 ${
                      alert.severity === 'high' ? 'bg-destructive/20 text-destructive' :
                      alert.severity === 'medium' ? 'bg-amber/20 text-amber' :
                      'bg-primary/20 text-primary'
                    }`}
                  >
                    {alert.severity}
                  </Badge>
                  <div className="flex-1">
                    <p className="text-sm text-foreground">{alert.message}</p>
                    <p className="text-xs text-muted-foreground mt-1">{alert.action}</p>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
        </>
      )}
    </div>
  );
}
