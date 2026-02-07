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
  Loader2, DollarSign, Percent, Gift, Search, TrendingDown,
  ArrowUpRight, Package, IndianRupee, AlertTriangle
} from 'lucide-react';
import { toast } from 'sonner';
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid
} from 'recharts';
import EmptyState from '../components/EmptyState';

const CHART_COLORS = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6'];

export default function IncentivesPage() {
  const [eligibility, setEligibility] = useState(null);
  const [summary, setSummary] = useState(null);
  const [leakageDashboard, setLeakageDashboard] = useState(null);
  const [shipmentAnalysis, setShipmentAnalysis] = useState([]);
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
  const [activeTab, setActiveTab] = useState('dashboard');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [summaryRes, leakageRes, analysisRes, shipmentsRes] = await Promise.all([
        api.get('/incentives/summary'),
        api.get('/incentives/leakage-dashboard'),
        api.get('/incentives/shipment-analysis'),
        api.get('/shipments')
      ]);
      setSummary(summaryRes.data);
      setLeakageDashboard(leakageRes.data);
      setShipmentAnalysis(analysisRes.data);
      setShipments(shipmentsRes.data);
    } catch (error) {
      console.error('Failed to fetch incentives data:', error);
      toast.error('Failed to load incentives data');
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
    if (!value && value !== 0) return '₹0';
    if (value >= 100000) return `₹${(value / 100000).toFixed(2)}L`;
    return `₹${Number(value).toLocaleString('en-IN')}`;
  };

  const schemeData = summary ? [
    { name: 'RoDTEP', value: summary.by_scheme?.rodtep || 0 },
    { name: 'RoSCTL', value: summary.by_scheme?.rosctl || 0 },
    { name: 'Drawback', value: summary.by_scheme?.drawback || 0 }
  ].filter(d => d.value > 0) : [];

  const getPriorityBadge = (priority) => {
    const colors = {
      critical: 'bg-red-500/20 text-red-400 border-red-500/30',
      high: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
      medium: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
      low: 'bg-green-500/20 text-green-400 border-green-500/30'
    };
    return colors[priority] || colors.medium;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <RefreshCw className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in" data-testid="incentives-page">
      {/* Empty State Check */}
      {shipments.length === 0 ? (
        <EmptyState type="incentives" />
      ) : (
        <>
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="font-heading text-4xl text-foreground">Incentives Optimizer</h1>
          <p className="text-muted-foreground mt-1">RoDTEP, RoSCTL, Drawback - Never leave money on the table</p>
        </div>
        <div className="flex gap-2">
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
                <DialogDescription>Enter shipment details for incentive calculation</DialogDescription>
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
                    placeholder="7419, 7418, 9405"
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
      </div>

      {/* Money Left on Table - Hero Section */}
      {leakageDashboard && (
        <Card className="bg-gradient-to-r from-red-900/20 via-red-800/10 to-card border-red-500/30" data-testid="money-left-hero">
          <CardContent className="p-6">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
              <div className="flex items-start gap-4">
                <div className="w-16 h-16 rounded-xl bg-red-500/20 flex items-center justify-center flex-shrink-0">
                  <TrendingDown className="w-8 h-8 text-red-400" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground uppercase tracking-wider">Money Left on Table</p>
                  <p className="text-4xl font-heading font-bold text-red-400 mt-1">
                    {leakageDashboard.money_left_on_table?.formatted || formatCurrency(leakageDashboard.summary?.total_leakage)}
                  </p>
                  <p className="text-muted-foreground mt-2">
                    {leakageDashboard.shipment_stats?.unclaimed || 0} unclaimed shipments out of {leakageDashboard.shipment_stats?.total || 0} total
                  </p>
                </div>
              </div>
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="text-center px-6 py-3 rounded-lg bg-card/50 border border-border">
                  <p className="text-xs text-muted-foreground uppercase">Recovery Rate</p>
                  <p className="text-2xl font-heading font-bold text-primary">{leakageDashboard.summary?.recovery_rate || 0}%</p>
                </div>
                <div className="text-center px-6 py-3 rounded-lg bg-card/50 border border-border">
                  <p className="text-xs text-muted-foreground uppercase">Priority</p>
                  <Badge className={`mt-1 ${getPriorityBadge(leakageDashboard.money_left_on_table?.priority)}`}>
                    {leakageDashboard.money_left_on_table?.priority?.toUpperCase() || 'MEDIUM'}
                  </Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Summary Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-card border-border" data-testid="total-incentives-card">
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Potential</p>
                <p className="text-2xl font-heading font-bold mt-1 text-foreground">
                  {formatCurrency(leakageDashboard?.summary?.total_potential_incentives || summary?.total_incentives || 0)}
                </p>
              </div>
              <div className="w-12 h-12 rounded-md bg-primary/10 flex items-center justify-center">
                <IndianRupee className="w-6 h-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border" data-testid="claimed-card">
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Claimed</p>
                <p className="text-2xl font-heading font-bold mt-1 text-neon">
                  {formatCurrency(leakageDashboard?.summary?.total_claimed || summary?.claimed || 0)}
                </p>
              </div>
              <div className="w-12 h-12 rounded-md bg-neon/10 flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-neon" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border" data-testid="pending-card">
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Exports</p>
                <p className="text-2xl font-heading font-bold mt-1 text-foreground">
                  {formatCurrency(leakageDashboard?.summary?.total_exports || 0)}
                </p>
              </div>
              <div className="w-12 h-12 rounded-md bg-amber/10 flex items-center justify-center">
                <Package className="w-6 h-6 text-amber" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border" data-testid="claim-rate-card">
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Claim Rate</p>
                <p className="text-2xl font-heading font-bold mt-1 text-primary">
                  {leakageDashboard?.shipment_stats?.claim_rate || 0}%
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {leakageDashboard?.shipment_stats?.claimed || 0}/{leakageDashboard?.shipment_stats?.total || 0} shipments
                </p>
              </div>
              <div className="w-12 h-12 rounded-md bg-primary/10 flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 border-b border-border pb-2">
        <Button
          variant={activeTab === 'dashboard' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('dashboard')}
          data-testid="tab-dashboard"
        >
          Dashboard
        </Button>
        <Button
          variant={activeTab === 'analysis' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('analysis')}
          data-testid="tab-analysis"
        >
          Shipment Analysis
        </Button>
        <Button
          variant={activeTab === 'calculator' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('calculator')}
          data-testid="tab-calculator"
        >
          HS Code Checker
        </Button>
      </div>

      {/* Dashboard Tab */}
      {activeTab === 'dashboard' && (
        <div className="space-y-6">
          {/* Top Leaking Shipments & Scheme Breakdown */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Top Leaking Shipments */}
            <Card className="bg-card border-border" data-testid="top-leaking">
              <CardHeader>
                <CardTitle className="font-heading text-lg flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-amber" />
                  Top Shipments Needing Action
                </CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <Table>
                  <TableHeader>
                    <TableRow className="border-border hover:bg-transparent">
                      <TableHead className="text-muted-foreground">Shipment</TableHead>
                      <TableHead className="text-muted-foreground">FOB Value</TableHead>
                      <TableHead className="text-muted-foreground text-right">Potential</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {(leakageDashboard?.top_leaking_shipments || []).slice(0, 5).map((item, index) => (
                      <TableRow key={index} className="border-border hover:bg-surface-highlight/50">
                        <TableCell>
                          <div>
                            <p className="font-medium">{item.shipment_number}</p>
                            <p className="text-xs text-muted-foreground">{item.buyer_name}</p>
                          </div>
                        </TableCell>
                        <TableCell className="font-mono">{formatCurrency(item.fob_value)}</TableCell>
                        <TableCell className="text-right">
                          <span className="font-mono text-red-400">{formatCurrency(item.leakage)}</span>
                        </TableCell>
                      </TableRow>
                    ))}
                    {(!leakageDashboard?.top_leaking_shipments || leakageDashboard.top_leaking_shipments.length === 0) && (
                      <TableRow>
                        <TableCell colSpan={3} className="text-center text-muted-foreground py-8">
                          No unclaimed shipments found
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
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
                {schemeData.length > 0 ? (
                  <>
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
                  </>
                ) : (
                  <div className="h-[200px] flex items-center justify-center text-muted-foreground">
                    No incentive data available yet
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Moradabad Handicrafts HS Codes Reference */}
          <Card className="bg-card border-border" data-testid="hs-codes-reference">
            <CardHeader>
              <CardTitle className="font-heading text-lg">Handicrafts & Metal Products - HS Code Reference</CardTitle>
              <p className="text-sm text-muted-foreground">Quick reference for common Moradabad export categories</p>
            </CardHeader>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow className="border-border hover:bg-transparent">
                    <TableHead className="text-muted-foreground">Category</TableHead>
                    <TableHead className="text-muted-foreground">HS Code</TableHead>
                    <TableHead className="text-muted-foreground">Description</TableHead>
                    <TableHead className="text-muted-foreground text-right">RoDTEP Rate</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {[
                    { category: 'Brass Handicrafts', code: '7419.80.30', desc: 'Artware/Handicrafts of Brass', rate: '2.5% - 3%' },
                    { category: 'Copper Utensils', code: '7418.10.22', desc: 'Utensils of Copper (Bottles, Mugs)', rate: '1.5% - 2%' },
                    { category: 'Iron Furniture', code: '9403.20.10', desc: 'Iron/Metal Furniture', rate: '0.8% - 1%' },
                    { category: 'Metal Planters', code: '7326.90.99', desc: 'Iron Handicraft Planters', rate: '1.0% - 1.5%' },
                    { category: 'Stone Decor', code: '6802.21.90', desc: 'Worked Marble/Stone Articles', rate: '1.2% - 2%' },
                    { category: 'Decorative Lamps', code: '9405.50.00', desc: 'Non-Electrical Lamps & Lighting', rate: '1.5% - 2%' }
                  ].map((item, index) => (
                    <TableRow key={index} className="border-border hover:bg-surface-highlight/50">
                      <TableCell className="font-medium">{item.category}</TableCell>
                      <TableCell className="font-mono text-primary">{item.code}</TableCell>
                      <TableCell className="text-muted-foreground">{item.desc}</TableCell>
                      <TableCell className="text-right font-mono text-neon">{item.rate}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Shipment Analysis Tab */}
      {activeTab === 'analysis' && (
        <Card className="bg-card border-border" data-testid="shipment-analysis-table">
          <CardHeader>
            <CardTitle className="font-heading text-lg">Shipment-by-Shipment Incentive Analysis</CardTitle>
            <p className="text-sm text-muted-foreground">Detailed breakdown showing claimed vs potential incentives for each shipment</p>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="border-border hover:bg-transparent">
                    <TableHead className="text-muted-foreground">Shipment</TableHead>
                    <TableHead className="text-muted-foreground">Buyer</TableHead>
                    <TableHead className="text-muted-foreground">FOB Value</TableHead>
                    <TableHead className="text-muted-foreground">HS Codes</TableHead>
                    <TableHead className="text-muted-foreground">Status</TableHead>
                    <TableHead className="text-muted-foreground text-right">Claimed</TableHead>
                    <TableHead className="text-muted-foreground text-right">Potential</TableHead>
                    <TableHead className="text-muted-foreground text-right">Leakage</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {shipmentAnalysis.length > 0 ? shipmentAnalysis.map((item, index) => (
                    <TableRow key={index} className="border-border hover:bg-surface-highlight/50">
                      <TableCell className="font-medium">{item.shipment_number}</TableCell>
                      <TableCell className="text-muted-foreground">{item.buyer_name}</TableCell>
                      <TableCell className="font-mono">{formatCurrency(item.fob_value)}</TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-1">
                          {(item.hs_codes || []).slice(0, 2).map((code, i) => (
                            <Badge key={i} variant="outline" className="text-xs">{code}</Badge>
                          ))}
                          {(item.hs_codes || []).length > 2 && (
                            <Badge variant="outline" className="text-xs">+{item.hs_codes.length - 2}</Badge>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={item.incentive_status === 'claimed' ? 'bg-neon/20 text-neon' : 'bg-amber/20 text-amber'}>
                          {item.incentive_status}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right font-mono text-neon">
                        {formatCurrency(item.claimed_amount)}
                      </TableCell>
                      <TableCell className="text-right font-mono">
                        {formatCurrency(item.potential_incentive)}
                      </TableCell>
                      <TableCell className="text-right">
                        {item.leakage > 0 ? (
                          <span className="font-mono text-red-400">{formatCurrency(item.leakage)}</span>
                        ) : (
                          <span className="font-mono text-neon">₹0</span>
                        )}
                      </TableCell>
                    </TableRow>
                  )) : (
                    <TableRow>
                      <TableCell colSpan={8} className="text-center text-muted-foreground py-12">
                        <Package className="w-12 h-12 mx-auto mb-3 opacity-50" />
                        <p>No shipments found. Create shipments to see incentive analysis.</p>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* HS Code Checker Tab */}
      {activeTab === 'calculator' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* HS Code Eligibility Checker */}
          <Card className="bg-card border-border" data-testid="eligibility-checker">
            <CardHeader>
              <CardTitle className="font-heading text-lg flex items-center gap-2">
                <Search className="w-5 h-5 text-primary" />
                RoDTEP/RoSCTL Eligibility Checker
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Input
                  value={hsCode}
                  onChange={(e) => setHsCode(e.target.value)}
                  placeholder="Enter HS Code (e.g., 7419, 9405)"
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
                    eligibility.eligible ? 'bg-neon/5 border-neon/20' : 'bg-amber/5 border-amber/20'
                  }`}
                  data-testid="eligibility-result"
                >
                  <div className="flex items-center gap-2 mb-3">
                    {eligibility.eligible ? (
                      <CheckCircle className="w-5 h-5 text-neon" />
                    ) : (
                      <AlertCircle className="w-5 h-5 text-amber" />
                    )}
                    <span className={`font-medium ${eligibility.eligible ? 'text-neon' : 'text-amber'}`}>
                      {eligibility.eligible ? 'Eligible for RoDTEP' : 'Limited Eligibility'}
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
                      <p className="text-muted-foreground">RoDTEP Rate</p>
                      <p className="font-mono text-neon">{eligibility.rate_percent}%</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Scheme</p>
                      <p className="font-mono">{eligibility.scheme}</p>
                    </div>
                  </div>
                  {eligibility.all_rates && (
                    <div className="mt-4 pt-4 border-t border-border">
                      <p className="text-xs text-muted-foreground mb-2">All Applicable Schemes</p>
                      <div className="grid grid-cols-3 gap-2 text-sm">
                        <div className="p-2 rounded bg-background">
                          <p className="text-xs text-muted-foreground">RoDTEP</p>
                          <p className="font-mono text-neon">{eligibility.all_rates.rodtep}%</p>
                        </div>
                        <div className="p-2 rounded bg-background">
                          <p className="text-xs text-muted-foreground">RoSCTL</p>
                          <p className="font-mono">{eligibility.all_rates.rosctl}%</p>
                        </div>
                        <div className="p-2 rounded bg-background">
                          <p className="text-xs text-muted-foreground">Drawback</p>
                          <p className="font-mono">{eligibility.all_rates.drawback}%</p>
                        </div>
                      </div>
                      <p className="text-xs text-muted-foreground mt-2">Total: {eligibility.all_rates.total}%</p>
                    </div>
                  )}
                  <p className="text-xs text-muted-foreground mt-3">{eligibility.notes}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Quick Reference */}
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="font-heading text-lg">Popular Export Categories</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {[
                { code: '7419', desc: 'Brass Artware/Handicrafts', rate: '~3%' },
                { code: '7418', desc: 'Copper Utensils', rate: '~2%' },
                { code: '9403', desc: 'Metal Furniture', rate: '~1%' },
                { code: '9405', desc: 'Lamps & Lighting', rate: '~2%' },
                { code: '7326', desc: 'Iron Articles/Planters', rate: '~1.5%' },
                { code: '6802', desc: 'Stone/Marble Articles', rate: '~2%' }
              ].map((item, i) => (
                <button
                  key={i}
                  onClick={() => setHsCode(item.code)}
                  className="w-full flex items-center justify-between p-3 rounded-md bg-background hover:bg-surface-highlight transition-colors text-left"
                >
                  <div>
                    <span className="font-mono text-primary">{item.code}</span>
                    <span className="text-muted-foreground ml-2">{item.desc}</span>
                  </div>
                  <Badge variant="outline" className="text-neon">{item.rate}</Badge>
                </button>
              ))}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Action Required Alert */}
      {leakageDashboard?.action_required?.length > 0 && (
        <Card className="bg-amber/5 border-amber/20" data-testid="action-required-card">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-md bg-amber/10 flex items-center justify-center flex-shrink-0">
                <AlertCircle className="w-6 h-6 text-amber" />
              </div>
              <div className="flex-1">
                <h3 className="font-heading text-lg text-amber mb-1">Action Required</h3>
                <p className="text-muted-foreground mb-4">
                  You have {leakageDashboard.action_required.length} shipments with unclaimed incentives worth approximately {formatCurrency(leakageDashboard.summary?.total_leakage)}
                </p>
                <div className="flex flex-wrap gap-2">
                  {leakageDashboard.action_required.slice(0, 3).map((ship, i) => (
                    <Badge key={i} variant="outline" className="border-amber/30 text-amber">
                      {ship.shipment_number}: {formatCurrency(ship.estimated_incentive)}
                    </Badge>
                  ))}
                  {leakageDashboard.action_required.length > 3 && (
                    <Badge variant="outline" className="border-amber/30 text-amber">
                      +{leakageDashboard.action_required.length - 3} more
                    </Badge>
                  )}
                </div>
                <Button 
                  className="mt-4 bg-amber hover:bg-amber/90 text-black"
                  onClick={() => setCalculateDialogOpen(true)}
                >
                  Claim Incentives Now
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
