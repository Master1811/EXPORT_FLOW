import React, { useState, useEffect, useCallback } from 'react';
import { api } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import {
  Dialog, DialogContent, DialogDescription, DialogHeader,
  DialogTitle, DialogFooter
} from '../components/ui/dialog';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue
} from '../components/ui/select';
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow
} from '../components/ui/table';
import {
  AlertTriangle, Clock, CheckCircle, Download, FileText,
  RefreshCw, Loader2, DollarSign, AlertCircle, Timer, Shield, Zap
} from 'lucide-react';
import { toast } from 'sonner';

const formatCurrency = (value, currency = 'USD') => {
  if (currency === 'INR' || currency === 'USD') {
    if (value >= 10000000) return `${currency === 'INR' ? '₹' : '$'}${(value / 10000000).toFixed(2)}Cr`;
    if (value >= 100000) return `${currency === 'INR' ? '₹' : '$'}${(value / 100000).toFixed(2)}L`;
  }
  return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(value);
};

const RISK_COLORS = {
  CRITICAL: { bg: 'bg-red-500/10', border: 'border-red-500/30', text: 'text-red-400', progress: 'bg-red-500', badge: 'bg-red-500/20 text-red-400 border-red-500/30' },
  WARNING: { bg: 'bg-orange-500/10', border: 'border-orange-500/30', text: 'text-orange-400', progress: 'bg-orange-500', badge: 'bg-orange-500/20 text-orange-400 border-orange-500/30' },
  MONITOR: { bg: 'bg-yellow-500/10', border: 'border-yellow-500/30', text: 'text-yellow-400', progress: 'bg-yellow-500', badge: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' },
  SAFE: { bg: 'bg-emerald-500/10', border: 'border-emerald-500/30', text: 'text-emerald-400', progress: 'bg-emerald-500', badge: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' }
};

const EXTENSION_REASONS = [
  { value: 'delayed_payment', label: 'Delayed Payment - Buyer cash flow issues' },
  { value: 'dispute', label: 'Commercial Dispute - Quality/specification issues' },
  { value: 'banking_delay', label: 'Banking Delay - Processing delays' },
  { value: 'force_majeure', label: 'Force Majeure - Unforeseen circumstances' },
  { value: 'documentation', label: 'Documentation - Procedural delays' }
];

export default function RiskClockPage() {
  const [riskData, setRiskData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [realizeDialogOpen, setRealizeDialogOpen] = useState(false);
  const [letterDialogOpen, setLetterDialogOpen] = useState(false);
  const [generatedLetterDialogOpen, setGeneratedLetterDialogOpen] = useState(false);
  const [selectedShipment, setSelectedShipment] = useState(null);
  const [generatedLetter, setGeneratedLetter] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [realizeForm, setRealizeForm] = useState({ amount: '', reference_number: '', bank_name: '' });
  const [letterForm, setLetterForm] = useState({ reason: 'delayed_payment', extension_days: 90 });

  const fetchRiskData = useCallback(async () => {
    try {
      const response = await api.get('/risk-clock');
      setRiskData(response.data);
    } catch (error) {
      toast.error('Failed to fetch risk clock data');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => { fetchRiskData(); }, [fetchRiskData]);

  const handleRefresh = () => { setRefreshing(true); fetchRiskData(); };

  const openRealizeDialog = (shipment) => {
    setSelectedShipment(shipment);
    setRealizeForm({ amount: shipment.pending_amount?.toString() || '', reference_number: '', bank_name: '' });
    setRealizeDialogOpen(true);
  };

  const openLetterDialog = (shipment) => {
    setSelectedShipment(shipment);
    setLetterForm({ reason: 'delayed_payment', extension_days: 90 });
    setLetterDialogOpen(true);
  };

  const handleRealize = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.post(`/risk-clock/realize/${selectedShipment.id}`, {
        amount: parseFloat(realizeForm.amount),
        reference_number: realizeForm.reference_number,
        bank_name: realizeForm.bank_name
      });
      toast.success('Payment marked as realized');
      setRealizeDialogOpen(false);
      fetchRiskData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to record payment');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDraftLetter = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const response = await api.post(`/risk-clock/draft-letter/${selectedShipment.id}`, letterForm);
      setGeneratedLetter(response.data);
      setLetterDialogOpen(false);
      setGeneratedLetterDialogOpen(true);
      toast.success('RBI extension letter drafted');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to generate letter');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDownloadDGFT = async () => {
    try {
      const response = await api.get('/dgft/export', { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'DGFT_eBRC_Export.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('DGFT Excel downloaded');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to download DGFT Excel');
    }
  };

  const RiskClockProgress = ({ shipment }) => {
    const ageDays = shipment.age_days || 0;
    const progress = Math.min(100, (ageDays / 270) * 100);
    const colors = RISK_COLORS[shipment.risk_category || 'SAFE'];
    return (
      <div className="space-y-2">
        <div className="flex justify-between items-center text-sm">
          <span className={colors.text}>{ageDays} days</span>
          <span className="text-zinc-500">{shipment.days_remaining || (270 - ageDays)} days left</span>
        </div>
        <div className="h-3 bg-zinc-800 rounded-full overflow-hidden">
          <div className={`h-full ${colors.progress} transition-all duration-500`} style={{ width: `${progress}%` }} />
        </div>
        <div className="flex justify-between text-xs text-zinc-500">
          <span>0</span><span className="text-yellow-500">180</span><span className="text-orange-500">210</span><span className="text-red-500">240</span><span>270</span>
        </div>
      </div>
    );
  };

  const SummaryCard = ({ title, count, value, color, icon: Icon }) => (
    <Card className={`${RISK_COLORS[color].bg} ${RISK_COLORS[color].border} border`} data-testid={`risk-summary-${color.toLowerCase()}`}>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm text-zinc-400">{title}</p>
            <p className={`text-3xl font-bold mt-1 ${RISK_COLORS[color].text}`}>{count}</p>
            <p className="text-xs text-zinc-500 mt-1">{formatCurrency(value, 'USD')}</p>
          </div>
          <div className={`w-12 h-12 rounded-xl ${RISK_COLORS[color].bg} flex items-center justify-center`}>
            <Icon className={`w-6 h-6 ${RISK_COLORS[color].text}`} />
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const ShipmentRow = ({ shipment, category }) => {
    const colors = RISK_COLORS[category];
    return (
      <TableRow className="border-zinc-800 hover:bg-zinc-800/50" data-testid={`risk-shipment-${shipment.id}`}>
        <TableCell>
          <div><p className="font-mono text-sm">{shipment.shipment_number}</p><p className="text-xs text-zinc-500">{shipment.buyer_name}</p></div>
        </TableCell>
        <TableCell className="font-mono">{formatCurrency(shipment.total_value, shipment.currency)}</TableCell>
        <TableCell><div className="w-48"><RiskClockProgress shipment={shipment} /></div></TableCell>
        <TableCell>
          <div className="text-right">
            <p className={`font-mono ${colors.text}`}>{shipment.realization_percentage?.toFixed(1)}%</p>
            <p className="text-xs text-zinc-500">{formatCurrency(shipment.pending_amount, shipment.currency)} pending</p>
          </div>
        </TableCell>
        <TableCell><Badge className={colors.badge}>{category}</Badge></TableCell>
        <TableCell>
          <div className="flex gap-2 justify-end">
            <Button size="sm" variant="outline" className="border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10" onClick={() => openRealizeDialog(shipment)} data-testid={`realize-btn-${shipment.id}`}>
              <DollarSign className="w-4 h-4 mr-1" />Realize
            </Button>
            <Button size="sm" variant="outline" className="border-blue-500/30 text-blue-400 hover:bg-blue-500/10" onClick={() => openLetterDialog(shipment)} data-testid={`draft-letter-btn-${shipment.id}`}>
              <FileText className="w-4 h-4 mr-1" />Draft Letter
            </Button>
          </div>
        </TableCell>
      </TableRow>
    );
  };

  if (loading) return <div className="flex items-center justify-center h-96"><RefreshCw className="w-8 h-8 animate-spin text-violet-400" /></div>;

  const summary = riskData?.summary || {};
  const buckets = riskData?.buckets || {};

  return (
    <div className="space-y-6" data-testid="risk-clock-page">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-white via-zinc-200 to-zinc-400 bg-clip-text text-transparent">RBI Risk Clock</h1>
          <p className="text-zinc-400 mt-1">9-Month EDPMS Monitoring Dashboard</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={handleDownloadDGFT} variant="outline" className="border-violet-500/30 text-violet-400 hover:bg-violet-500/10" data-testid="download-dgft-btn">
            <Download className="w-4 h-4 mr-2" />DGFT Excel
          </Button>
          <Button onClick={handleRefresh} variant="outline" className="border-zinc-700" disabled={refreshing}>
            <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />Refresh
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <SummaryCard title="Critical (>240 days)" count={summary.critical_count || 0} value={summary.critical_value || 0} color="CRITICAL" icon={AlertTriangle} />
        <SummaryCard title="Warning (>210 days)" count={summary.warning_count || 0} value={summary.warning_value || 0} color="WARNING" icon={AlertCircle} />
        <SummaryCard title="Monitor (>180 days)" count={summary.monitor_count || 0} value={summary.monitor_value || 0} color="MONITOR" icon={Timer} />
        <SummaryCard title="Safe (<180 days)" count={summary.safe_count || 0} value={0} color="SAFE" icon={Shield} />
      </div>

      {summary.total_at_risk_value > 0 && (
        <Card className="bg-gradient-to-r from-red-500/10 via-orange-500/10 to-yellow-500/10 border-red-500/30" data-testid="at-risk-banner">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 rounded-2xl bg-red-500/20 flex items-center justify-center"><Zap className="w-8 h-8 text-red-400" /></div>
                <div>
                  <p className="text-sm text-zinc-400">Total Value At Risk</p>
                  <p className="text-3xl font-bold text-white">{formatCurrency(summary.total_at_risk_value, 'USD')}</p>
                  <p className="text-xs text-zinc-500 mt-1">{(summary.critical_count || 0) + (summary.warning_count || 0) + (summary.monitor_count || 0)} shipments require attention</p>
                </div>
              </div>
              <div className="text-right"><p className="text-sm text-zinc-400">RBI Deadline</p><p className="text-2xl font-bold text-white">270 Days</p></div>
            </div>
          </CardContent>
        </Card>
      )}

      {buckets.critical?.length > 0 && (
        <Card className="bg-zinc-900/50 border-red-500/30" data-testid="critical-section">
          <CardHeader><CardTitle className="text-lg flex items-center gap-2 text-red-400"><AlertTriangle className="w-5 h-5" />Critical - Immediate Action Required</CardTitle></CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader><TableRow className="border-zinc-800"><TableHead>Shipment</TableHead><TableHead>Value</TableHead><TableHead>Risk Clock</TableHead><TableHead className="text-right">Realization</TableHead><TableHead>Status</TableHead><TableHead className="text-right">Actions</TableHead></TableRow></TableHeader>
              <TableBody>{buckets.critical.map(s => <ShipmentRow key={s.id} shipment={s} category="CRITICAL" />)}</TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {buckets.warning?.length > 0 && (
        <Card className="bg-zinc-900/50 border-orange-500/30" data-testid="warning-section">
          <CardHeader><CardTitle className="text-lg flex items-center gap-2 text-orange-400"><AlertCircle className="w-5 h-5" />Warning - Action Recommended</CardTitle></CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader><TableRow className="border-zinc-800"><TableHead>Shipment</TableHead><TableHead>Value</TableHead><TableHead>Risk Clock</TableHead><TableHead className="text-right">Realization</TableHead><TableHead>Status</TableHead><TableHead className="text-right">Actions</TableHead></TableRow></TableHeader>
              <TableBody>{buckets.warning.map(s => <ShipmentRow key={s.id} shipment={s} category="WARNING" />)}</TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {buckets.monitor?.length > 0 && (
        <Card className="bg-zinc-900/50 border-yellow-500/30" data-testid="monitor-section">
          <CardHeader><CardTitle className="text-lg flex items-center gap-2 text-yellow-400"><Timer className="w-5 h-5" />Monitor - Keep Track</CardTitle></CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader><TableRow className="border-zinc-800"><TableHead>Shipment</TableHead><TableHead>Value</TableHead><TableHead>Risk Clock</TableHead><TableHead className="text-right">Realization</TableHead><TableHead>Status</TableHead><TableHead className="text-right">Actions</TableHead></TableRow></TableHeader>
              <TableBody>{buckets.monitor.map(s => <ShipmentRow key={s.id} shipment={s} category="MONITOR" />)}</TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {!buckets.critical?.length && !buckets.warning?.length && !buckets.monitor?.length && (
        <Card className="bg-zinc-900/50 border-emerald-500/30">
          <CardContent className="p-12 text-center">
            <CheckCircle className="w-16 h-16 text-emerald-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">All Clear!</h3>
            <p className="text-zinc-400">No shipments at risk. All receivables are within safe limits.</p>
          </CardContent>
        </Card>
      )}

      <Dialog open={realizeDialogOpen} onOpenChange={setRealizeDialogOpen}>
        <DialogContent className="bg-zinc-900 border-zinc-800">
          <DialogHeader><DialogTitle>Mark Payment as Realized</DialogTitle><DialogDescription>Record realization for {selectedShipment?.shipment_number}</DialogDescription></DialogHeader>
          <form onSubmit={handleRealize} className="space-y-4">
            <div className="space-y-2"><Label>Amount ({selectedShipment?.currency})</Label><Input type="number" value={realizeForm.amount} onChange={(e) => setRealizeForm({...realizeForm, amount: e.target.value})} required className="bg-zinc-800 border-zinc-700" data-testid="realize-amount-input" /></div>
            <div className="space-y-2"><Label>Reference Number</Label><Input value={realizeForm.reference_number} onChange={(e) => setRealizeForm({...realizeForm, reference_number: e.target.value})} placeholder="Bank reference/UTR" className="bg-zinc-800 border-zinc-700" /></div>
            <div className="space-y-2"><Label>Bank Name</Label><Input value={realizeForm.bank_name} onChange={(e) => setRealizeForm({...realizeForm, bank_name: e.target.value})} placeholder="Receiving bank" className="bg-zinc-800 border-zinc-700" /></div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setRealizeDialogOpen(false)}>Cancel</Button>
              <Button type="submit" disabled={submitting} className="bg-emerald-600 hover:bg-emerald-700">{submitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}Record Payment</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <Dialog open={letterDialogOpen} onOpenChange={setLetterDialogOpen}>
        <DialogContent className="bg-zinc-900 border-zinc-800">
          <DialogHeader><DialogTitle>Draft RBI Extension Letter</DialogTitle><DialogDescription>Generate AI-powered extension request for {selectedShipment?.shipment_number}</DialogDescription></DialogHeader>
          <form onSubmit={handleDraftLetter} className="space-y-4">
            <div className="space-y-2">
              <Label>Reason for Extension</Label>
              <Select value={letterForm.reason} onValueChange={(v) => setLetterForm({...letterForm, reason: v})}>
                <SelectTrigger className="bg-zinc-800 border-zinc-700" data-testid="letter-reason-select"><SelectValue /></SelectTrigger>
                <SelectContent>{EXTENSION_REASONS.map(r => <SelectItem key={r.value} value={r.value}>{r.label}</SelectItem>)}</SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Extension Period (Days)</Label>
              <Select value={letterForm.extension_days.toString()} onValueChange={(v) => setLetterForm({...letterForm, extension_days: parseInt(v)})}>
                <SelectTrigger className="bg-zinc-800 border-zinc-700"><SelectValue /></SelectTrigger>
                <SelectContent><SelectItem value="30">30 Days</SelectItem><SelectItem value="60">60 Days</SelectItem><SelectItem value="90">90 Days</SelectItem><SelectItem value="180">180 Days</SelectItem></SelectContent>
              </Select>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setLetterDialogOpen(false)}>Cancel</Button>
              <Button type="submit" disabled={submitting} className="bg-blue-600 hover:bg-blue-700">{submitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}Generate with AI</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <Dialog open={generatedLetterDialogOpen} onOpenChange={setGeneratedLetterDialogOpen}>
        <DialogContent className="bg-zinc-900 border-zinc-800 max-w-3xl max-h-[80vh] overflow-y-auto">
          <DialogHeader><DialogTitle className="flex items-center gap-2"><FileText className="w-5 h-5 text-blue-400" />Generated RBI Extension Letter</DialogTitle></DialogHeader>
          <div className="bg-zinc-800 rounded-lg p-4 whitespace-pre-wrap font-mono text-sm text-zinc-300 max-h-96 overflow-y-auto">{generatedLetter?.content}</div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setGeneratedLetterDialogOpen(false)}>Close</Button>
            <Button onClick={() => { navigator.clipboard.writeText(generatedLetter?.content || ''); toast.success('Letter copied to clipboard'); }}>Copy to Clipboard</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
