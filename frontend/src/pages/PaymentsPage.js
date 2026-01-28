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
  CreditCard, Plus, DollarSign, Calendar, RefreshCw, Loader2,
  TrendingUp, Clock, AlertCircle, CheckCircle
} from 'lucide-react';
import { toast } from 'sonner';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';

const CHART_COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

export default function PaymentsPage() {
  const [payments, setPayments] = useState([]);
  const [receivables, setReceivables] = useState([]);
  const [aging, setAging] = useState({});
  const [shipments, setShipments] = useState([]);
  const [loading, setLoading] = useState(true);
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
        api.get('/receivables'),
        api.get('/receivables/aging'),
        api.get('/shipments')
      ]);
      setReceivables(receivablesRes.data);
      setAging(agingRes.data);
      setShipments(shipmentsRes.data);

      // Fetch payments for each shipment
      const allPayments = [];
      for (const shipment of shipmentsRes.data.slice(0, 10)) {
        try {
          const paymentRes = await api.get(`/payments/shipment/${shipment.id}`);
          allPayments.push(...paymentRes.data);
        } catch (e) {}
      }
      setPayments(allPayments);
    } catch (error) {
      toast.error('Failed to fetch payment data');
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
      toast.success('Payment recorded successfully');
      setCreateDialogOpen(false);
      setFormData({
        shipment_id: '',
        amount: '',
        currency: 'USD',
        payment_date: '',
        payment_mode: 'wire',
        bank_reference: '',
        exchange_rate: '',
        inr_amount: ''
      });
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to record payment');
    } finally {
      setSubmitting(false);
    }
  };

  const formatCurrency = (value, currency = 'INR') => {
    const symbols = { USD: '$', EUR: '€', GBP: '£', INR: '₹', AED: 'AED ' };
    if (currency === 'INR' && value >= 100000) {
      return `₹${(value / 100000).toFixed(2)}L`;
    }
    return `${symbols[currency] || ''}${value.toLocaleString()}`;
  };

  const agingData = [
    { name: 'Current', value: aging.current || 0, color: '#10B981' },
    { name: '30 Days', value: aging['30_days'] || 0, color: '#3B82F6' },
    { name: '60 Days', value: aging['60_days'] || 0, color: '#F59E0B' },
    { name: '90 Days', value: aging['90_days'] || 0, color: '#EF4444' },
    { name: '90+ Days', value: aging.over_90 || 0, color: '#8B5CF6' }
  ];

  const totalReceivables = receivables.reduce((sum, r) => sum + r.outstanding, 0);

  return (
    <div className="space-y-6 animate-fade-in" data-testid="payments-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="font-heading text-4xl text-foreground">Payments & Receivables</h1>
          <p className="text-muted-foreground mt-1">Track payments and manage receivables</p>
        </div>
        <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-primary hover:bg-primary/90" data-testid="record-payment-btn">
              <Plus className="w-4 h-4 mr-2" />
              Record Payment
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md bg-card border-border">
            <DialogHeader>
              <DialogTitle className="font-heading text-xl">Record Payment</DialogTitle>
              <DialogDescription>Enter payment details</DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="shipment_id">Shipment *</Label>
                <Select value={formData.shipment_id} onValueChange={(v) => handleSelectChange('shipment_id', v)}>
                  <SelectTrigger className="bg-background" data-testid="payment-shipment-select">
                    <SelectValue placeholder="Select shipment" />
                  </SelectTrigger>
                  <SelectContent>
                    {shipments.map(s => (
                      <SelectItem key={s.id} value={s.id}>
                        {s.shipment_number} - {s.buyer_name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="amount">Amount *</Label>
                  <Input
                    id="amount"
                    name="amount"
                    type="number"
                    value={formData.amount}
                    onChange={handleInputChange}
                    required
                    className="bg-background"
                    data-testid="payment-amount-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="currency">Currency</Label>
                  <Select value={formData.currency} onValueChange={(v) => handleSelectChange('currency', v)}>
                    <SelectTrigger className="bg-background" data-testid="payment-currency-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="USD">USD</SelectItem>
                      <SelectItem value="EUR">EUR</SelectItem>
                      <SelectItem value="GBP">GBP</SelectItem>
                      <SelectItem value="AED">AED</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="payment_date">Payment Date *</Label>
                  <Input
                    id="payment_date"
                    name="payment_date"
                    type="date"
                    value={formData.payment_date}
                    onChange={handleInputChange}
                    required
                    className="bg-background"
                    data-testid="payment-date-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="payment_mode">Mode</Label>
                  <Select value={formData.payment_mode} onValueChange={(v) => handleSelectChange('payment_mode', v)}>
                    <SelectTrigger className="bg-background" data-testid="payment-mode-select">
                      <SelectValue />
                    </SelectTrigger>
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
                <Label htmlFor="bank_reference">Bank Reference</Label>
                <Input
                  id="bank_reference"
                  name="bank_reference"
                  value={formData.bank_reference}
                  onChange={handleInputChange}
                  placeholder="Bank transaction reference"
                  className="bg-background"
                  data-testid="bank-reference-input"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="exchange_rate">Exchange Rate</Label>
                  <Input
                    id="exchange_rate"
                    name="exchange_rate"
                    type="number"
                    step="0.01"
                    value={formData.exchange_rate}
                    onChange={handleInputChange}
                    placeholder="83.50"
                    className="bg-background"
                    data-testid="exchange-rate-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="inr_amount">INR Amount</Label>
                  <Input
                    id="inr_amount"
                    name="inr_amount"
                    type="number"
                    value={formData.inr_amount}
                    onChange={handleInputChange}
                    className="bg-background"
                    data-testid="inr-amount-input"
                  />
                </div>
              </div>

              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={submitting} data-testid="submit-payment-btn">
                  {submitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                  Record Payment
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-card border-border" data-testid="total-receivables-card">
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Receivables</p>
                <p className="text-2xl font-heading font-bold mt-1">{formatCurrency(totalReceivables)}</p>
              </div>
              <div className="w-12 h-12 rounded-md bg-amber/10 flex items-center justify-center">
                <DollarSign className="w-6 h-6 text-amber" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border" data-testid="overdue-card">
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Overdue (90+ days)</p>
                <p className="text-2xl font-heading font-bold mt-1 text-destructive">{formatCurrency(aging.over_90 || 0)}</p>
              </div>
              <div className="w-12 h-12 rounded-md bg-destructive/10 flex items-center justify-center">
                <AlertCircle className="w-6 h-6 text-destructive" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border" data-testid="payments-received-card">
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Payments Received</p>
                <p className="text-2xl font-heading font-bold mt-1 text-neon">{payments.length}</p>
              </div>
              <div className="w-12 h-12 rounded-md bg-neon/10 flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-neon" />
              </div>
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
              <div className="w-12 h-12 rounded-md bg-primary/10 flex items-center justify-center">
                <Clock className="w-6 h-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Aging Chart */}
        <Card className="bg-card border-border" data-testid="aging-chart">
          <CardHeader>
            <CardTitle className="font-heading text-lg flex items-center gap-2">
              <Clock className="w-5 h-5 text-primary" />
              Receivables Aging
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[280px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={agingData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                  <XAxis dataKey="name" stroke="#71717A" fontSize={12} />
                  <YAxis stroke="#71717A" fontSize={12} tickFormatter={(v) => `₹${v/1000}K`} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#18181B',
                      border: '1px solid #27272A',
                      borderRadius: '6px'
                    }}
                    formatter={(value) => [formatCurrency(value), 'Amount']}
                  />
                  <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                    {agingData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Recent Payments */}
        <Card className="bg-card border-border" data-testid="recent-payments-card">
          <CardHeader>
            <CardTitle className="font-heading text-lg flex items-center gap-2">
              <CreditCard className="w-5 h-5 text-neon" />
              Recent Payments
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <RefreshCw className="w-6 h-6 animate-spin text-primary" />
              </div>
            ) : payments.length === 0 ? (
              <div className="text-center py-8">
                <CreditCard className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">No payments recorded yet</p>
              </div>
            ) : (
              <div className="space-y-3">
                {payments.slice(0, 5).map((payment, index) => (
                  <div
                    key={payment.id || index}
                    className="flex items-center justify-between p-3 rounded-md bg-surface-highlight/50 border border-border"
                    data-testid={`payment-item-${index}`}
                  >
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
                      <Badge variant="outline" className="text-xs">
                        {payment.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Receivables Table */}
      <Card className="bg-card border-border" data-testid="receivables-table">
        <CardHeader>
          <CardTitle className="font-heading text-lg">Outstanding Receivables</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="w-6 h-6 animate-spin text-primary" />
            </div>
          ) : receivables.length === 0 ? (
            <div className="text-center py-12">
              <CheckCircle className="w-12 h-12 text-neon mx-auto mb-4" />
              <p className="text-muted-foreground">All receivables collected!</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="border-border hover:bg-transparent">
                  <TableHead className="text-muted-foreground">Shipment</TableHead>
                  <TableHead className="text-muted-foreground">Buyer</TableHead>
                  <TableHead className="text-muted-foreground">Total Value</TableHead>
                  <TableHead className="text-muted-foreground">Paid</TableHead>
                  <TableHead className="text-muted-foreground">Outstanding</TableHead>
                  <TableHead className="text-muted-foreground">Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {receivables.map((item, index) => (
                  <TableRow key={index} className="border-border hover:bg-surface-highlight/50">
                    <TableCell className="font-mono text-sm">{item.shipment_number}</TableCell>
                    <TableCell>{item.buyer_name}</TableCell>
                    <TableCell className="font-mono">{formatCurrency(item.total_value, item.currency)}</TableCell>
                    <TableCell className="font-mono text-neon">{formatCurrency(item.paid, item.currency)}</TableCell>
                    <TableCell className="font-mono text-amber">{formatCurrency(item.outstanding, item.currency)}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{item.status}</Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
