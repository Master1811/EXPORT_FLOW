import React, { useState, useEffect } from 'react';
import { api } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Badge } from '../components/ui/badge';
import {
  Dialog, DialogContent, DialogDescription, DialogHeader,
  DialogTitle, DialogTrigger, DialogFooter
} from '../components/ui/dialog';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue
} from '../components/ui/select';
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow
} from '../components/ui/table';
import {
  CreditCard, Plus, DollarSign, RefreshCw, Loader2,
  TrendingUp, Clock, AlertCircle, CheckCircle, AlertTriangle,
  BarChart3, PieChart as PieChartIcon
} from 'lucide-react';
import { toast } from 'sonner';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell, Legend
} from 'recharts';

const BUCKET_COLORS = {
  '0_30': '#10B981',
  '31_60': '#3B82F6',
  '61_90': '#F59E0B',
  '91_plus': '#EF4444'
};

export default function PaymentsPage() {
  const [payments, setPayments] = useState([]);
  const [receivables, setReceivables] = useState([]);
  const [agingDashboard, setAgingDashboard] = useState(null);
  const [shipments, setShipments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedBucket, setSelectedBucket] = useState(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    shipment_id: '',
    amount: '',
    currency: 'USD',
    payment_date: '',
    payment_mode: 'wire',
    bank_reference: '',
    exchange_rate: '',
    inr_amount: ''
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [receivablesRes, agingRes, shipmentsRes] = await Promise.all([
        api.get('/payments/receivables'),
        api.get('/payments/receivables/aging-dashboard'),
        api.get('/shipments')
      ]);
      setReceivables(receivablesRes.data);
      setAgingDashboard(agingRes.data);
      setShipments(shipmentsRes.data);

      // Fetch payments for shipments
      const allPayments = [];
      for (const shipment of shipmentsRes.data.slice(0, 10)) {
        try {
          const paymentRes = await api.get(`/payments/shipment/${shipment.id}`);
          allPayments.push(...paymentRes.data);
        } catch (e) {}
      }
      setPayments(allPayments);
    } catch (error) {
      toast.error('Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSelectChange = (name, value) => {
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const data = {
        ...formData,
        amount: parseFloat(formData.amount),
        exchange_rate: formData.exchange_rate ? parseFloat(formData.exchange_rate) : null,
        inr_amount: formData.inr_amount ? parseFloat(formData.inr_amount) : null
      };
      await api.post('/payments', data);
      toast.success('Payment recorded');
      setCreateDialogOpen(false);
      setFormData({
        shipment_id: '', amount: '', currency: 'USD', payment_date: '',
        payment_mode: 'wire', bank_reference: '', exchange_rate: '', inr_amount: ''
      });
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to record payment');
    } finally {
      setSubmitting(false);
    }
  };

  const formatCurrency = (value, currency = 'INR') => {
    if (!value && value !== 0) return '₹0';
    const symbols = { USD: '$', EUR: '€', GBP: '£', INR: '₹', AED: 'AED ' };
    if (value >= 100000) return `₹${(value / 100000).toFixed(2)}L`;
    return `${symbols[currency] || '₹'}${Number(value).toLocaleString('en-IN')}`;
  };

  const getBucketColor = (key) => BUCKET_COLORS[key] || '#6B7280';

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <RefreshCw className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in" data-testid="payments-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="font-heading text-4xl text-foreground">Payments & Receivables</h1>
          <p className="text-muted-foreground mt-1">Track payments and aging receivables</p>
        </div>
        <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-primary hover:bg-primary/90" data-testid="record-payment-btn">
              <Plus className="w-4 h-4 mr-2" /> Record Payment
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md bg-card border-border">
            <DialogHeader>
              <DialogTitle className="font-heading text-xl">Record Payment</DialogTitle>
              <DialogDescription>Enter payment details</DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label>Shipment *</Label>
                <Select value={formData.shipment_id} onValueChange={(v) => handleSelectChange('shipment_id', v)}>
                  <SelectTrigger className="bg-background" data-testid="payment-shipment-select">
                    <SelectValue placeholder="Select shipment" />
                  </SelectTrigger>
                  <SelectContent>
                    {shipments.map(s => (
                      <SelectItem key={s.id} value={s.id}>{s.shipment_number} - {s.buyer_name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Amount *</Label>
                  <Input name="amount" type="number" value={formData.amount} onChange={handleInputChange} required className="bg-background" />
                </div>
                <div className="space-y-2">
                  <Label>Currency</Label>
                  <Select value={formData.currency} onValueChange={(v) => handleSelectChange('currency', v)}>
                    <SelectTrigger className="bg-background"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="USD">USD</SelectItem>
                      <SelectItem value="EUR">EUR</SelectItem>
                      <SelectItem value="GBP">GBP</SelectItem>
                      <SelectItem value="AED">AED</SelectItem>
                      <SelectItem value="INR">INR</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Payment Date *</Label>
                  <Input name="payment_date" type="date" value={formData.payment_date} onChange={handleInputChange} required className="bg-background" />
                </div>
                <div className="space-y-2">
                  <Label>Mode</Label>
                  <Select value={formData.payment_mode} onValueChange={(v) => handleSelectChange('payment_mode', v)}>
                    <SelectTrigger className="bg-background"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="wire">Wire Transfer</SelectItem>
                      <SelectItem value="lc">Letter of Credit</SelectItem>
                      <SelectItem value="da">D/A</SelectItem>
                      <SelectItem value="dp">D/P</SelectItem>
                      <SelectItem value="advance">Advance</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="space-y-2">
                <Label>Bank Reference</Label>
                <Input name="bank_reference" value={formData.bank_reference} onChange={handleInputChange} className="bg-background" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Exchange Rate</Label>
                  <Input name="exchange_rate" type="number" step="0.01" value={formData.exchange_rate} onChange={handleInputChange} className="bg-background" />
                </div>
                <div className="space-y-2">
                  <Label>INR Amount</Label>
                  <Input name="inr_amount" type="number" value={formData.inr_amount} onChange={handleInputChange} className="bg-background" />
                </div>
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
                <Button type="submit" disabled={submitting}>
                  {submitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                  Record Payment
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 border-b border-border pb-2">
        <Button variant={activeTab === 'overview' ? 'default' : 'ghost'} onClick={() => setActiveTab('overview')} data-testid="tab-overview">
          <PieChartIcon className="w-4 h-4 mr-2" /> Overview
        </Button>
        <Button variant={activeTab === 'aging' ? 'default' : 'ghost'} onClick={() => setActiveTab('aging')} data-testid="tab-aging">
          <BarChart3 className="w-4 h-4 mr-2" /> Aging Dashboard
        </Button>
        <Button variant={activeTab === 'receivables' ? 'default' : 'ghost'} onClick={() => setActiveTab('receivables')} data-testid="tab-receivables">
          <Clock className="w-4 h-4 mr-2" /> Receivables
        </Button>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && agingDashboard && (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="bg-card border-border" data-testid="total-receivables-card">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Total Receivables</p>
                    <p className="text-2xl font-heading font-bold mt-1">{formatCurrency(agingDashboard.summary.total_receivables)}</p>
                    <p className="text-xs text-muted-foreground mt-1">{agingDashboard.summary.total_shipments_with_outstanding} shipments</p>
                  </div>
                  <DollarSign className="w-8 h-8 text-amber" />
                </div>
              </CardContent>
            </Card>
            <Card className="bg-card border-border" data-testid="overdue-total-card">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Overdue (60+ days)</p>
                    <p className="text-2xl font-heading font-bold mt-1 text-destructive">{formatCurrency(agingDashboard.summary.total_overdue)}</p>
                    <p className="text-xs text-muted-foreground mt-1">{agingDashboard.summary.overdue_percentage}% of total</p>
                  </div>
                  <AlertTriangle className="w-8 h-8 text-destructive" />
                </div>
              </CardContent>
            </Card>
            <Card className="bg-card border-border" data-testid="payments-count-card">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Payments Received</p>
                    <p className="text-2xl font-heading font-bold mt-1 text-neon">{payments.length}</p>
                  </div>
                  <CheckCircle className="w-8 h-8 text-neon" />
                </div>
              </CardContent>
            </Card>
            <Card className="bg-card border-border" data-testid="pending-invoices-card">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Pending Invoices</p>
                    <p className="text-2xl font-heading font-bold mt-1">{receivables.length}</p>
                  </div>
                  <Clock className="w-8 h-8 text-primary" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Aging Bar Chart */}
            <Card className="bg-card border-border" data-testid="aging-bar-chart">
              <CardHeader>
                <CardTitle className="font-heading text-lg flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-primary" />
                  Receivables by Age
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[280px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={agingDashboard.chart_data}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                      <XAxis dataKey="name" stroke="#71717A" fontSize={12} />
                      <YAxis stroke="#71717A" fontSize={12} tickFormatter={(v) => `₹${v/1000}K`} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#18181B', border: '1px solid #27272A', borderRadius: '6px' }}
                        formatter={(value) => [formatCurrency(value), 'Amount']}
                      />
                      <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                        {agingDashboard.chart_data.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* Aging Pie Chart */}
            <Card className="bg-card border-border" data-testid="aging-pie-chart">
              <CardHeader>
                <CardTitle className="font-heading text-lg flex items-center gap-2">
                  <PieChartIcon className="w-5 h-5 text-neon" />
                  Distribution by Age
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[280px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={agingDashboard.chart_data.filter(d => d.value > 0)}
                        cx="50%"
                        cy="50%"
                        innerRadius={50}
                        outerRadius={90}
                        paddingAngle={3}
                        dataKey="value"
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                        labelLine={false}
                      >
                        {agingDashboard.chart_data.filter(d => d.value > 0).map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{ backgroundColor: '#18181B', border: '1px solid #27272A', borderRadius: '6px' }}
                        formatter={(value) => [formatCurrency(value), 'Amount']}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex flex-wrap justify-center gap-4 mt-4">
                  {agingDashboard.chart_data.map((item, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                      <span className="text-sm text-muted-foreground">{item.name}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Payments */}
          <Card className="bg-card border-border" data-testid="recent-payments-card">
            <CardHeader>
              <CardTitle className="font-heading text-lg flex items-center gap-2">
                <CreditCard className="w-5 h-5 text-neon" />
                Recent Payments
              </CardTitle>
            </CardHeader>
            <CardContent>
              {payments.length === 0 ? (
                <div className="text-center py-8">
                  <CreditCard className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">No payments recorded yet</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {payments.slice(0, 5).map((payment, index) => (
                    <div key={payment.id || index} className="flex items-center justify-between p-3 rounded-md bg-surface-highlight/50 border border-border">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-md bg-neon/10 flex items-center justify-center">
                          <CheckCircle className="w-5 h-5 text-neon" />
                        </div>
                        <div>
                          <p className="text-sm font-medium">{payment.payment_mode?.toUpperCase()}</p>
                          <p className="text-xs text-muted-foreground">{payment.payment_date}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-mono font-medium">{formatCurrency(payment.amount, payment.currency)}</p>
                        <Badge variant="outline" className="text-xs">{payment.status}</Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Aging Dashboard Tab */}
      {activeTab === 'aging' && agingDashboard && (
        <div className="space-y-6">
          {/* Aging Buckets */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {Object.entries(agingDashboard.buckets).map(([key, bucket]) => (
              <Card 
                key={key} 
                className={`bg-card border-border cursor-pointer transition-all hover:border-primary ${selectedBucket === key ? 'ring-2 ring-primary' : ''}`}
                onClick={() => setSelectedBucket(selectedBucket === key ? null : key)}
                data-testid={`bucket-${key}`}
              >
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">{bucket.label}</p>
                      <p className="text-2xl font-heading font-bold mt-1" style={{ color: bucket.color }}>
                        {formatCurrency(bucket.amount)}
                      </p>
                      <div className="flex items-center gap-2 mt-2">
                        <Badge variant="outline" className="text-xs">{bucket.count} shipments</Badge>
                        <span className="text-xs text-muted-foreground">{bucket.percentage}%</span>
                      </div>
                    </div>
                    <div className="w-12 h-12 rounded-md flex items-center justify-center" style={{ backgroundColor: `${bucket.color}20` }}>
                      <Clock className="w-6 h-6" style={{ color: bucket.color }} />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Selected Bucket Details */}
          {selectedBucket && agingDashboard.buckets[selectedBucket].shipments.length > 0 && (
            <Card className="bg-card border-border" data-testid="bucket-details">
              <CardHeader>
                <CardTitle className="font-heading text-lg">
                  {agingDashboard.buckets[selectedBucket].label} - Shipment Details
                </CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <Table>
                  <TableHeader>
                    <TableRow className="border-border">
                      <TableHead>Shipment</TableHead>
                      <TableHead>Buyer</TableHead>
                      <TableHead>Total Value</TableHead>
                      <TableHead>Outstanding</TableHead>
                      <TableHead>Days</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {agingDashboard.buckets[selectedBucket].shipments.map((s, i) => (
                      <TableRow key={i} className="border-border">
                        <TableCell className="font-mono">{s.shipment_number}</TableCell>
                        <TableCell>
                          <div>
                            <p>{s.buyer_name}</p>
                            <p className="text-xs text-muted-foreground">{s.buyer_country}</p>
                          </div>
                        </TableCell>
                        <TableCell className="font-mono">{formatCurrency(s.total_value, s.currency)}</TableCell>
                        <TableCell className="font-mono text-amber">{formatCurrency(s.outstanding, s.currency)}</TableCell>
                        <TableCell>
                          <span className={s.days_outstanding > 60 ? 'text-destructive' : s.days_outstanding > 30 ? 'text-amber' : ''}>
                            {s.days_outstanding} days
                          </span>
                        </TableCell>
                        <TableCell><Badge variant="outline">{s.status}</Badge></TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          )}

          {/* Overdue Alerts */}
          {agingDashboard.overdue_alerts.length > 0 && (
            <Card className="bg-destructive/5 border-destructive/30" data-testid="overdue-alerts">
              <CardHeader>
                <CardTitle className="font-heading text-lg text-destructive flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5" /> Overdue Payments (60+ days)
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {agingDashboard.overdue_alerts.map((s, i) => (
                    <div key={i} className="flex items-center justify-between p-4 rounded-md bg-background border border-destructive/20">
                      <div>
                        <p className="font-medium">{s.shipment_number}</p>
                        <p className="text-sm text-muted-foreground">{s.buyer_name} • {s.buyer_country}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-mono font-bold text-destructive">{formatCurrency(s.outstanding, s.currency)}</p>
                        <Badge variant="destructive">{s.days_outstanding} days overdue</Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Receivables Tab */}
      {activeTab === 'receivables' && (
        <Card className="bg-card border-border" data-testid="receivables-table">
          <CardHeader>
            <CardTitle className="font-heading text-lg">Outstanding Receivables</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {receivables.length === 0 ? (
              <div className="text-center py-12">
                <CheckCircle className="w-12 h-12 text-neon mx-auto mb-4" />
                <p className="text-muted-foreground">All receivables collected!</p>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow className="border-border">
                    <TableHead>Shipment</TableHead>
                    <TableHead>Buyer</TableHead>
                    <TableHead>Total Value</TableHead>
                    <TableHead>Paid</TableHead>
                    <TableHead>Outstanding</TableHead>
                    <TableHead>Days</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {receivables.map((item, index) => (
                    <TableRow key={index} className="border-border hover:bg-surface-highlight/50">
                      <TableCell className="font-mono text-sm">{item.shipment_number}</TableCell>
                      <TableCell>
                        <div>
                          <p>{item.buyer_name}</p>
                          <p className="text-xs text-muted-foreground">{item.buyer_country}</p>
                        </div>
                      </TableCell>
                      <TableCell className="font-mono">{formatCurrency(item.total_value, item.currency)}</TableCell>
                      <TableCell className="font-mono text-neon">{formatCurrency(item.paid, item.currency)}</TableCell>
                      <TableCell className="font-mono text-amber">{formatCurrency(item.outstanding, item.currency)}</TableCell>
                      <TableCell>
                        <span className={item.days_outstanding > 60 ? 'text-destructive' : item.days_outstanding > 30 ? 'text-amber' : ''}>
                          {item.days_outstanding || 0} days
                        </span>
                      </TableCell>
                      <TableCell><Badge variant="outline">{item.status}</Badge></TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
