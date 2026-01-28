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
  Calculator, TrendingUp, AlertCircle, CheckCircle, RefreshCw,
  Loader2, DollarSign, Percent, Gift, Search
} from 'lucide-react';
import { toast } from 'sonner';
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip
} from 'recharts';

const CHART_COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

export default function IncentivesPage() {
  const [eligibility, setEligibility] = useState(null);
  const [summary, setSummary] = useState(null);
  const [lostMoney, setLostMoney] = useState(null);
  const [shipments, setShipments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [hsCode, setHsCode] = useState('');
  const [checkingEligibility, setCheckingEligibility] = useState(false);
  const [calculateDialogOpen, setCalculateDialogOpen] = useState(false);
  const [calcFormData, setCalcFormData] = useState({
    shipment_id: '',
    hs_codes: '',
    fob_value: '',
    currency: 'INR'
  });
  const [calculating, setCalculating] = useState(false);
  const [calculatedResult, setCalculatedResult] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [summaryRes, lostRes, shipmentsRes] = await Promise.all([
        api.get('/incentives/summary'),
        api.get('/incentives/lost-money'),
        api.get('/shipments')
      ]);
      setSummary(summaryRes.data);
      setLostMoney(lostRes.data);
      setShipments(shipmentsRes.data);
    } catch (error) {
      console.error('Failed to fetch incentives data:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkEligibility = async () => {
    if (!hsCode) return;
    setCheckingEligibility(true);
    try {
      const response = await api.get('/incentives/rodtep-eligibility', { params: { hs_code: hsCode } });
      setEligibility(response.data);
    } catch (error) {
      toast.error('Failed to check eligibility');
    } finally {
      setCheckingEligibility(false);
    }
  };

  const calculateIncentive = async (e) => {
    e.preventDefault();
    setCalculating(true);
    try {
      const response = await api.post('/incentives/calculate', {
        shipment_id: calcFormData.shipment_id,
        hs_codes: calcFormData.hs_codes.split(',').map(s => s.trim()),
        fob_value: parseFloat(calcFormData.fob_value),
        currency: calcFormData.currency
      });
      setCalculatedResult(response.data);
      toast.success('Incentive calculated!');
      fetchData();
    } catch (error) {
      toast.error('Failed to calculate incentive');
    } finally {
      setCalculating(false);
    }
  };

  const formatCurrency = (value) => {
    if (!value) return '₹0';
    if (value >= 100000) return `₹${(value / 100000).toFixed(2)}L`;
    return `₹${value.toLocaleString('en-IN')}`;
  };

  const schemeData = summary ? [
    { name: 'RoDTEP', value: summary.by_scheme?.RoDTEP || 0 },
    { name: 'RoSCTL', value: summary.by_scheme?.RoSCTL || 0 }
  ] : [];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <RefreshCw className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in" data-testid="incentives-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="font-heading text-4xl text-foreground">Export Incentives</h1>
          <p className="text-muted-foreground mt-1">RoDTEP, RoSCTL eligibility and calculations</p>
        </div>
        <Dialog open={calculateDialogOpen} onOpenChange={setCalculateDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-primary hover:bg-primary/90" data-testid="calculate-incentive-btn">
              <Calculator className="w-4 h-4 mr-2" />
              Calculate Incentive
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-card border-border max-w-md">
            <DialogHeader>
              <DialogTitle className="font-heading">Calculate Incentive</DialogTitle>
              <DialogDescription>Enter shipment details</DialogDescription>
            </DialogHeader>
            <form onSubmit={calculateIncentive} className="space-y-4">
              <div className="space-y-2">
                <Label>Shipment</Label>
                <Select value={calcFormData.shipment_id} onValueChange={(v) => setCalcFormData({ ...calcFormData, shipment_id: v })}>
                  <SelectTrigger className="bg-background" data-testid="calc-shipment-select">
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
              <div className="space-y-2">
                <Label>HS Codes (comma separated)</Label>
                <Input
                  value={calcFormData.hs_codes}
                  onChange={(e) => setCalcFormData({ ...calcFormData, hs_codes: e.target.value })}
                  placeholder="8471, 8542"
                  required
                  className="bg-background"
                  data-testid="calc-hs-codes-input"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>FOB Value</Label>
                  <Input
                    type="number"
                    value={calcFormData.fob_value}
                    onChange={(e) => setCalcFormData({ ...calcFormData, fob_value: e.target.value })}
                    required
                    className="bg-background"
                    data-testid="calc-fob-value-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Currency</Label>
                  <Select value={calcFormData.currency} onValueChange={(v) => setCalcFormData({ ...calcFormData, currency: v })}>
                    <SelectTrigger className="bg-background" data-testid="calc-currency-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="INR">INR</SelectItem>
                      <SelectItem value="USD">USD</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {calculatedResult && (
                <div className="p-4 rounded-md bg-neon/5 border border-neon/20" data-testid="calc-result">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="w-5 h-5 text-neon" />
                    <span className="font-medium text-neon">Incentive Calculated</span>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Rate</p>
                      <p className="font-mono">{calculatedResult.rate_percent}%</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Amount</p>
                      <p className="font-mono text-neon">{formatCurrency(calculatedResult.incentive_amount)}</p>
                    </div>
                  </div>
                </div>
              )}

              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setCalculateDialogOpen(false)}>Cancel</Button>
                <Button type="submit" disabled={calculating} data-testid="submit-calc-btn">
                  {calculating && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                  Calculate
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-card border-border" data-testid="total-incentives-card">
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Incentives</p>
                <p className="text-2xl font-heading font-bold mt-1 text-neon">
                  {formatCurrency(summary?.total_incentives || 0)}
                </p>
              </div>
              <div className="w-12 h-12 rounded-md bg-neon/10 flex items-center justify-center">
                <Gift className="w-6 h-6 text-neon" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border" data-testid="claimed-card">
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Claimed</p>
                <p className="text-2xl font-heading font-bold mt-1">
                  {formatCurrency(summary?.claimed || 0)}
                </p>
              </div>
              <div className="w-12 h-12 rounded-md bg-primary/10 flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border" data-testid="pending-card">
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Pending</p>
                <p className="text-2xl font-heading font-bold mt-1 text-amber">
                  {formatCurrency(summary?.pending || 0)}
                </p>
              </div>
              <div className="w-12 h-12 rounded-md bg-amber/10 flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-amber" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border bg-destructive/5" data-testid="lost-money-card">
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Potential Loss</p>
                <p className="text-2xl font-heading font-bold mt-1 text-destructive">
                  {formatCurrency(lostMoney?.potential_incentive_loss || 0)}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {lostMoney?.unclaimed_shipments || 0} unclaimed shipments
                </p>
              </div>
              <div className="w-12 h-12 rounded-md bg-destructive/10 flex items-center justify-center">
                <AlertCircle className="w-6 h-6 text-destructive" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* HS Code Checker and Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* HS Code Eligibility Checker */}
        <Card className="bg-card border-border" data-testid="eligibility-checker">
          <CardHeader>
            <CardTitle className="font-heading text-lg flex items-center gap-2">
              <Search className="w-5 h-5 text-primary" />
              RoDTEP Eligibility Checker
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <Input
                value={hsCode}
                onChange={(e) => setHsCode(e.target.value)}
                placeholder="Enter HS Code (e.g., 8471)"
                className="bg-background"
                data-testid="hs-code-input"
              />
              <Button onClick={checkEligibility} disabled={checkingEligibility} data-testid="check-eligibility-btn">
                {checkingEligibility ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Check'}
              </Button>
            </div>

            {eligibility && (
              <div 
                className={`p-4 rounded-md border ${
                  eligibility.eligible ? 'bg-neon/5 border-neon/20' : 'bg-destructive/5 border-destructive/20'
                }`}
                data-testid="eligibility-result"
              >
                <div className="flex items-center gap-2 mb-3">
                  {eligibility.eligible ? (
                    <CheckCircle className="w-5 h-5 text-neon" />
                  ) : (
                    <AlertCircle className="w-5 h-5 text-destructive" />
                  )}
                  <span className={`font-medium ${eligibility.eligible ? 'text-neon' : 'text-destructive'}`}>
                    {eligibility.eligible ? 'Eligible for RoDTEP' : 'Not Eligible'}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">HS Code</p>
                    <p className="font-mono">{eligibility.hs_code}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Chapter</p>
                    <p className="font-mono">{eligibility.chapter}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Rate</p>
                    <p className="font-mono text-neon">{eligibility.rate_percent}%</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Scheme</p>
                    <p className="font-mono">{eligibility.scheme}</p>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground mt-3">{eligibility.notes}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Incentives by Scheme */}
        <Card className="bg-card border-border" data-testid="scheme-breakdown">
          <CardHeader>
            <CardTitle className="font-heading text-lg flex items-center gap-2">
              <Percent className="w-5 h-5 text-neon" />
              Incentives by Scheme
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={schemeData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {schemeData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#18181B',
                      border: '1px solid #27272A',
                      borderRadius: '6px'
                    }}
                    formatter={(value) => [formatCurrency(value), 'Amount']}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center gap-6 mt-4">
              {schemeData.map((item, i) => (
                <div key={item.name} className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: CHART_COLORS[i] }} />
                  <span className="text-sm text-muted-foreground">{item.name}</span>
                  <span className="text-sm font-mono">{formatCurrency(item.value)}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recommendation Card */}
      {lostMoney?.unclaimed_shipments > 0 && (
        <Card className="bg-amber/5 border-amber/20" data-testid="recommendation-card">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-md bg-amber/10 flex items-center justify-center flex-shrink-0">
                <AlertCircle className="w-6 h-6 text-amber" />
              </div>
              <div>
                <h3 className="font-heading text-lg text-amber mb-1">Action Required</h3>
                <p className="text-muted-foreground">{lostMoney.recommendation}</p>
                <Button variant="outline" className="mt-4 border-amber text-amber hover:bg-amber/10">
                  Claim Incentives Now
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* RoDTEP Rate Table */}
      <Card className="bg-card border-border" data-testid="rodtep-rates-table">
        <CardHeader>
          <CardTitle className="font-heading text-lg">RoDTEP Rates by Chapter</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow className="border-border hover:bg-transparent">
                <TableHead className="text-muted-foreground">Chapter</TableHead>
                <TableHead className="text-muted-foreground">Description</TableHead>
                <TableHead className="text-muted-foreground">Rate</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {[
                { chapter: '61-63', desc: 'Textiles & Apparel', rate: '4.0%' },
                { chapter: '84-85', desc: 'Machinery & Electronics', rate: '2.5%' },
                { chapter: '87', desc: 'Vehicles & Parts', rate: '3.0%' },
                { chapter: '90', desc: 'Instruments & Apparatus', rate: '2.0%' },
                { chapter: '94', desc: 'Furniture', rate: '3.5%' }
              ].map((item, index) => (
                <TableRow key={index} className="border-border hover:bg-surface-highlight/50">
                  <TableCell className="font-mono">{item.chapter}</TableCell>
                  <TableCell>{item.desc}</TableCell>
                  <TableCell className="font-mono text-neon">{item.rate}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
