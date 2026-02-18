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
  TrendingUp, TrendingDown, RefreshCw, Plus, DollarSign,
  ArrowRightLeft, Loader2
} from 'lucide-react';
import { toast } from 'sonner';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer
} from 'recharts';

const CURRENCIES = [
  { code: 'USD', name: 'US Dollar', symbol: '$' },
  { code: 'EUR', name: 'Euro', symbol: '€' },
  { code: 'GBP', name: 'British Pound', symbol: '£' },
  { code: 'AED', name: 'UAE Dirham', symbol: 'AED' },
  { code: 'JPY', name: 'Japanese Yen', symbol: '¥' },
  { code: 'CNY', name: 'Chinese Yuan', symbol: '¥' },
  { code: 'SGD', name: 'Singapore Dollar', symbol: 'S$' }
];

export default function ForexPage() {
  const [rates, setRates] = useState({});
  const [loading, setLoading] = useState(true);
  const [convertFrom, setConvertFrom] = useState('USD');
  const [convertTo, setConvertTo] = useState('INR');
  const [convertAmount, setConvertAmount] = useState('');
  const [convertResult, setConvertResult] = useState(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    currency: 'USD',
    rate: '',
    source: 'manual'
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchRates();
  }, []);

  const fetchRates = async () => {
    try {
      const response = await api.get('/forex/latest');
      setRates(response.data.rates);
    } catch (error) {
      toast.error('Failed to fetch forex rates');
    } finally {
      setLoading(false);
    }
  };

  // Helper to get rate value (handles both object and number formats)
  const getRateValue = (currency) => {
    const rateData = rates[currency];
    if (!rateData) return 1;
    // Handle object format: { rate: 83.5, source: "default", ... }
    if (typeof rateData === 'object' && rateData.rate !== undefined) {
      return rateData.rate;
    }
    // Handle direct number format
    return typeof rateData === 'number' ? rateData : 1;
  };

  const handleConvert = () => {
    if (!convertAmount) return;
    const amount = parseFloat(convertAmount);
    let result;
    
    if (convertTo === 'INR') {
      result = amount * getRateValue(convertFrom);
    } else if (convertFrom === 'INR') {
      result = amount / getRateValue(convertTo);
    } else {
      // Cross rate: Convert to INR first, then to target currency
      const inrAmount = amount * getRateValue(convertFrom);
      result = inrAmount / getRateValue(convertTo);
    }
    
    setConvertResult(result);
  };

  const handleAddRate = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.post('/forex/rate', {
        currency: formData.currency,
        rate: parseFloat(formData.rate),
        source: formData.source
      });
      toast.success('Forex rate added');
      setCreateDialogOpen(false);
      setFormData({ currency: 'USD', rate: '', source: 'manual' });
      fetchRates();
    } catch (error) {
      toast.error('Failed to add rate');
    } finally {
      setSubmitting(false);
    }
  };

  // Mock historical data for chart
  const historyData = [
    { date: 'Nov 1', USD: 83.2, EUR: 90.5 },
    { date: 'Nov 8', USD: 83.4, EUR: 90.8 },
    { date: 'Nov 15', USD: 83.3, EUR: 91.0 },
    { date: 'Nov 22', USD: 83.5, EUR: 91.2 },
    { date: 'Nov 29', USD: 83.4, EUR: 91.1 },
    { date: 'Dec 6', USD: 83.5, EUR: 91.2 }
  ];

  const getRateChange = (currency) => {
    // Mock change calculation
    const changes = { USD: 0.12, EUR: -0.08, GBP: 0.25, AED: 0.05, JPY: -0.15, CNY: 0.1, SGD: 0.08 };
    return changes[currency] || 0;
  };

  return (
    <div className="space-y-6 animate-fade-in" data-testid="forex-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="font-heading text-4xl text-foreground">Forex Rates</h1>
          <p className="text-muted-foreground mt-1">Track currency rates and convert amounts</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={fetchRates} data-testid="refresh-rates-btn">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button className="bg-primary hover:bg-primary/90" data-testid="add-rate-btn">
                <Plus className="w-4 h-4 mr-2" />
                Add Rate
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-md bg-card border-border">
              <DialogHeader>
                <DialogTitle className="font-heading text-xl">Add Forex Rate</DialogTitle>
                <DialogDescription>Manually enter a forex rate</DialogDescription>
              </DialogHeader>
              <form onSubmit={handleAddRate} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="currency">Currency</Label>
                  <Select value={formData.currency} onValueChange={(v) => setFormData({ ...formData, currency: v })}>
                    <SelectTrigger className="bg-background" data-testid="rate-currency-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {CURRENCIES.map(c => (
                        <SelectItem key={c.code} value={c.code}>{c.code} - {c.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="rate">Rate (vs INR)</Label>
                  <Input
                    id="rate"
                    type="number"
                    step="0.01"
                    value={formData.rate}
                    onChange={(e) => setFormData({ ...formData, rate: e.target.value })}
                    placeholder="83.50"
                    required
                    className="bg-background"
                    data-testid="rate-input"
                  />
                </div>
                <DialogFooter>
                  <Button type="button" variant="outline" onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
                  <Button type="submit" disabled={submitting} data-testid="submit-rate-btn">
                    {submitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                    Add Rate
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Currency Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
        {loading ? (
          <div className="col-span-full flex items-center justify-center py-12">
            <RefreshCw className="w-6 h-6 animate-spin text-primary" />
          </div>
        ) : (
          CURRENCIES.map(currency => {
            const rateValue = getRateValue(currency.code);
            const change = getRateChange(currency.code);
            const isUp = change > 0;
            
            return (
              <Card 
                key={currency.code} 
                className="bg-card border-border hover:border-primary/50 transition-colors"
                data-testid={`rate-card-${currency.code}`}
              >
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-muted-foreground">{currency.code}</span>
                    <div className={`flex items-center ${isUp ? 'text-neon' : 'text-destructive'}`}>
                      {isUp ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                      <span className="text-xs ml-1">{change > 0 ? '+' : ''}{change}%</span>
                    </div>
                  </div>
                  <p className="text-xl font-heading font-bold">₹{rateValue?.toFixed(2) || 'N/A'}</p>
                  <p className="text-xs text-muted-foreground mt-1">{currency.name}</p>
                </CardContent>
              </Card>
            );
          })
        )}
      </div>

      {/* Converter and Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Currency Converter */}
        <Card className="bg-card border-border" data-testid="currency-converter">
          <CardHeader>
            <CardTitle className="font-heading text-lg flex items-center gap-2">
              <ArrowRightLeft className="w-5 h-5 text-primary" />
              Currency Converter
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Amount</Label>
              <Input
                type="number"
                value={convertAmount}
                onChange={(e) => setConvertAmount(e.target.value)}
                placeholder="Enter amount"
                className="bg-background"
                data-testid="convert-amount-input"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>From</Label>
                <Select value={convertFrom} onValueChange={setConvertFrom}>
                  <SelectTrigger className="bg-background" data-testid="convert-from-select">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="INR">INR</SelectItem>
                    {CURRENCIES.map(c => (
                      <SelectItem key={c.code} value={c.code}>{c.code}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>To</Label>
                <Select value={convertTo} onValueChange={setConvertTo}>
                  <SelectTrigger className="bg-background" data-testid="convert-to-select">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="INR">INR</SelectItem>
                    {CURRENCIES.map(c => (
                      <SelectItem key={c.code} value={c.code}>{c.code}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <Button onClick={handleConvert} className="w-full" data-testid="convert-btn">
              Convert
            </Button>
            {convertResult !== null && (
              <div className="p-4 rounded-md bg-surface-highlight/50 border border-border" data-testid="convert-result">
                <p className="text-sm text-muted-foreground">Result</p>
                <p className="text-2xl font-heading font-bold">
                  {convertTo === 'INR' ? '₹' : CURRENCIES.find(c => c.code === convertTo)?.symbol || ''}
                  {convertResult.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Rate Chart */}
        <Card className="lg:col-span-2 bg-card border-border" data-testid="forex-chart">
          <CardHeader>
            <CardTitle className="font-heading text-lg flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-neon" />
              Rate Trend (USD & EUR vs INR)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[280px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={historyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                  <XAxis dataKey="date" stroke="#71717A" fontSize={12} />
                  <YAxis stroke="#71717A" fontSize={12} domain={['auto', 'auto']} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#18181B',
                      border: '1px solid #27272A',
                      borderRadius: '6px'
                    }}
                  />
                  <Line type="monotone" dataKey="USD" stroke="#3B82F6" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="EUR" stroke="#10B981" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center gap-6 mt-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-primary" />
                <span className="text-sm text-muted-foreground">USD</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-neon" />
                <span className="text-sm text-muted-foreground">EUR</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Forex Tips */}
      <Card className="bg-card border-border" data-testid="forex-tips">
        <CardHeader>
          <CardTitle className="font-heading text-lg">Forex Management Tips</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-md bg-surface-highlight/50 border border-border">
              <DollarSign className="w-8 h-8 text-primary mb-3" />
              <h3 className="font-medium mb-1">Forward Contracts</h3>
              <p className="text-sm text-muted-foreground">Lock in rates for future payments to hedge against volatility</p>
            </div>
            <div className="p-4 rounded-md bg-surface-highlight/50 border border-border">
              <ArrowRightLeft className="w-8 h-8 text-neon mb-3" />
              <h3 className="font-medium mb-1">EEFC Account</h3>
              <p className="text-sm text-muted-foreground">Maintain an EEFC account to hold forex and convert at favorable rates</p>
            </div>
            <div className="p-4 rounded-md bg-surface-highlight/50 border border-border">
              <TrendingUp className="w-8 h-8 text-amber mb-3" />
              <h3 className="font-medium mb-1">Rate Monitoring</h3>
              <p className="text-sm text-muted-foreground">Set alerts for favorable rate movements to optimize conversions</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
