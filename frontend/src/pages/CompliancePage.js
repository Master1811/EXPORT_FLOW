import React, { useState, useEffect } from 'react';
import { api } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import {
  Dialog, DialogContent, DialogDescription, DialogHeader,
  DialogTitle, DialogTrigger, DialogFooter
} from '../components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow
} from '../components/ui/table';
import {
  Calculator, FileCheck, AlertCircle, CheckCircle, Clock,
  RefreshCw, Plus, Loader2, Receipt, ArrowRight, Download
} from 'lucide-react';
import { toast } from 'sonner';

export default function CompliancePage() {
  const [lutStatus, setLutStatus] = useState(null);
  const [refundStatus, setRefundStatus] = useState(null);
  const [gstSummary, setGstSummary] = useState([]);
  const [expectedRefund, setExpectedRefund] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lutDialogOpen, setLutDialogOpen] = useState(false);
  const [creditDialogOpen, setCreditDialogOpen] = useState(false);
  const [lutFormData, setLutFormData] = useState({
    lut_number: '',
    financial_year: '2024-25',
    valid_from: '',
    valid_until: ''
  });
  const [creditFormData, setCreditFormData] = useState({
    invoice_number: '',
    supplier_gstin: '',
    invoice_date: '',
    taxable_value: '',
    igst: '',
    cgst: '',
    sgst: '',
    total_tax: ''
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [lutRes, refundStatusRes, expectedRes, summaryRes] = await Promise.all([
        api.get('/compliance/lut-status'),
        api.get('/gst/refund/status'),
        api.get('/gst/refund/expected'),
        api.get('/gst/summary/monthly', { params: { year: 2024 } })
      ]);
      setLutStatus(lutRes.data);
      setRefundStatus(refundStatusRes.data);
      setExpectedRefund(expectedRes.data);
      setGstSummary(summaryRes.data);
    } catch (error) {
      console.error('Failed to fetch compliance data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLutSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.post('/compliance/lut-link', lutFormData);
      toast.success('LUT linked successfully');
      setLutDialogOpen(false);
      fetchData();
    } catch (error) {
      toast.error('Failed to link LUT');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCreditSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.post('/gst/input-credit', {
        ...creditFormData,
        taxable_value: parseFloat(creditFormData.taxable_value),
        igst: parseFloat(creditFormData.igst || 0),
        cgst: parseFloat(creditFormData.cgst || 0),
        sgst: parseFloat(creditFormData.sgst || 0),
        total_tax: parseFloat(creditFormData.total_tax)
      });
      toast.success('Input credit added');
      setCreditDialogOpen(false);
      setCreditFormData({
        invoice_number: '',
        supplier_gstin: '',
        invoice_date: '',
        taxable_value: '',
        igst: '',
        cgst: '',
        sgst: '',
        total_tax: ''
      });
    } catch (error) {
      toast.error('Failed to add input credit');
    } finally {
      setSubmitting(false);
    }
  };

  const formatCurrency = (value) => {
    if (value >= 100000) return `₹${(value / 100000).toFixed(2)}L`;
    return `₹${value?.toLocaleString('en-IN') || 0}`;
  };

  const getRefundStatusColor = (status) => {
    const colors = {
      processing: 'bg-primary/20 text-primary',
      under_review: 'bg-amber/20 text-amber',
      approved: 'bg-neon/20 text-neon',
      rejected: 'bg-destructive/20 text-destructive'
    };
    return colors[status] || 'bg-muted text-muted-foreground';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <RefreshCw className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in" data-testid="compliance-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="font-heading text-4xl text-foreground">GST & Compliance</h1>
          <p className="text-muted-foreground mt-1">Manage GST, LUT, and compliance requirements</p>
        </div>
        <Button variant="outline" onClick={fetchData} data-testid="refresh-compliance-btn">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-card border-border" data-testid="expected-refund-card">
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Expected Refund</p>
                <p className="text-2xl font-heading font-bold mt-1 text-neon">
                  {formatCurrency(expectedRefund?.refund_expected || 0)}
                </p>
              </div>
              <div className="w-12 h-12 rounded-md bg-neon/10 flex items-center justify-center">
                <Receipt className="w-6 h-6 text-neon" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border" data-testid="pending-refund-card">
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Pending Applications</p>
                <p className="text-2xl font-heading font-bold mt-1">{refundStatus?.pending_applications || 0}</p>
              </div>
              <div className="w-12 h-12 rounded-md bg-amber/10 flex items-center justify-center">
                <Clock className="w-6 h-6 text-amber" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border" data-testid="igst-paid-card">
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground">IGST Paid</p>
                <p className="text-2xl font-heading font-bold mt-1">
                  {formatCurrency(expectedRefund?.igst_paid || 0)}
                </p>
              </div>
              <div className="w-12 h-12 rounded-md bg-primary/10 flex items-center justify-center">
                <Calculator className="w-6 h-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border" data-testid="lut-status-card">
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground">LUT Status</p>
                <Badge className={lutStatus?.status === 'active' ? 'bg-neon/20 text-neon' : 'bg-destructive/20 text-destructive'}>
                  {lutStatus?.status === 'active' ? 'Active' : 'Not Filed'}
                </Badge>
              </div>
              <div className="w-12 h-12 rounded-md bg-primary/10 flex items-center justify-center">
                <FileCheck className="w-6 h-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs for different sections */}
      <Tabs defaultValue="lut" className="space-y-6">
        <TabsList className="bg-surface border border-border">
          <TabsTrigger value="lut" data-testid="lut-tab">LUT Status</TabsTrigger>
          <TabsTrigger value="refunds" data-testid="refunds-tab">GST Refunds</TabsTrigger>
          <TabsTrigger value="input-credit" data-testid="input-credit-tab">Input Credit</TabsTrigger>
          <TabsTrigger value="monthly" data-testid="monthly-tab">Monthly Summary</TabsTrigger>
        </TabsList>

        {/* LUT Tab */}
        <TabsContent value="lut" className="space-y-4">
          <Card className="bg-card border-border" data-testid="lut-details-card">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="font-heading text-lg flex items-center gap-2">
                <FileCheck className="w-5 h-5 text-primary" />
                Letter of Undertaking (LUT)
              </CardTitle>
              <Dialog open={lutDialogOpen} onOpenChange={setLutDialogOpen}>
                <DialogTrigger asChild>
                  <Button size="sm" data-testid="link-lut-btn">
                    <Plus className="w-4 h-4 mr-2" />
                    Link LUT
                  </Button>
                </DialogTrigger>
                <DialogContent className="bg-card border-border">
                  <DialogHeader>
                    <DialogTitle className="font-heading">Link LUT</DialogTitle>
                    <DialogDescription>Enter your LUT details</DialogDescription>
                  </DialogHeader>
                  <form onSubmit={handleLutSubmit} className="space-y-4">
                    <div className="space-y-2">
                      <Label>LUT Number</Label>
                      <Input
                        value={lutFormData.lut_number}
                        onChange={(e) => setLutFormData({ ...lutFormData, lut_number: e.target.value })}
                        placeholder="AD123456789"
                        required
                        className="bg-background"
                        data-testid="lut-number-input"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label>Valid From</Label>
                        <Input
                          type="date"
                          value={lutFormData.valid_from}
                          onChange={(e) => setLutFormData({ ...lutFormData, valid_from: e.target.value })}
                          required
                          className="bg-background"
                          data-testid="lut-valid-from-input"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>Valid Until</Label>
                        <Input
                          type="date"
                          value={lutFormData.valid_until}
                          onChange={(e) => setLutFormData({ ...lutFormData, valid_until: e.target.value })}
                          required
                          className="bg-background"
                          data-testid="lut-valid-until-input"
                        />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button type="button" variant="outline" onClick={() => setLutDialogOpen(false)}>Cancel</Button>
                      <Button type="submit" disabled={submitting} data-testid="submit-lut-btn">
                        {submitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                        Link LUT
                      </Button>
                    </DialogFooter>
                  </form>
                </DialogContent>
              </Dialog>
            </CardHeader>
            <CardContent>
              {lutStatus?.status === 'active' ? (
                <div className="space-y-4">
                  <div className="flex items-center gap-3 p-4 rounded-md bg-neon/5 border border-neon/20">
                    <CheckCircle className="w-6 h-6 text-neon" />
                    <div>
                      <p className="font-medium text-neon">LUT Active</p>
                      <p className="text-sm text-muted-foreground">
                        LUT Number: {lutStatus.lut_number} | FY: {lutStatus.financial_year}
                      </p>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 rounded-md bg-surface-highlight/50 border border-border">
                      <p className="text-sm text-muted-foreground">Valid From</p>
                      <p className="font-medium">{lutStatus.valid_from || 'April 1, 2024'}</p>
                    </div>
                    <div className="p-4 rounded-md bg-surface-highlight/50 border border-border">
                      <p className="text-sm text-muted-foreground">Valid Until</p>
                      <p className="font-medium">{lutStatus.valid_until || 'March 31, 2025'}</p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex items-center gap-3 p-4 rounded-md bg-destructive/5 border border-destructive/20">
                  <AlertCircle className="w-6 h-6 text-destructive" />
                  <div>
                    <p className="font-medium text-destructive">LUT Not Filed</p>
                    <p className="text-sm text-muted-foreground">
                      File LUT to export without paying IGST. Action required for zero-rated exports.
                    </p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* GST Refunds Tab */}
        <TabsContent value="refunds" className="space-y-4">
          <Card className="bg-card border-border" data-testid="refund-applications-card">
            <CardHeader>
              <CardTitle className="font-heading text-lg flex items-center gap-2">
                <Receipt className="w-5 h-5 text-primary" />
                Refund Applications
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow className="border-border hover:bg-transparent">
                    <TableHead className="text-muted-foreground">Reference</TableHead>
                    <TableHead className="text-muted-foreground">Filed Date</TableHead>
                    <TableHead className="text-muted-foreground">Amount</TableHead>
                    <TableHead className="text-muted-foreground">Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {refundStatus?.applications?.map((app, index) => (
                    <TableRow key={index} className="border-border hover:bg-surface-highlight/50">
                      <TableCell className="font-mono text-sm">{app.ref_number}</TableCell>
                      <TableCell>{app.filed_date}</TableCell>
                      <TableCell className="font-mono">{formatCurrency(app.amount)}</TableCell>
                      <TableCell>
                        <Badge className={getRefundStatusColor(app.status)}>
                          {app.status.replace('_', ' ')}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Input Credit Tab */}
        <TabsContent value="input-credit" className="space-y-4">
          <Card className="bg-card border-border" data-testid="input-credit-card">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="font-heading text-lg flex items-center gap-2">
                <Calculator className="w-5 h-5 text-primary" />
                Input Tax Credit
              </CardTitle>
              <Dialog open={creditDialogOpen} onOpenChange={setCreditDialogOpen}>
                <DialogTrigger asChild>
                  <Button size="sm" data-testid="add-credit-btn">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Credit
                  </Button>
                </DialogTrigger>
                <DialogContent className="bg-card border-border max-w-md">
                  <DialogHeader>
                    <DialogTitle className="font-heading">Add Input Credit</DialogTitle>
                    <DialogDescription>Enter invoice details</DialogDescription>
                  </DialogHeader>
                  <form onSubmit={handleCreditSubmit} className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label>Invoice Number</Label>
                        <Input
                          value={creditFormData.invoice_number}
                          onChange={(e) => setCreditFormData({ ...creditFormData, invoice_number: e.target.value })}
                          required
                          className="bg-background"
                          data-testid="credit-invoice-input"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>Invoice Date</Label>
                        <Input
                          type="date"
                          value={creditFormData.invoice_date}
                          onChange={(e) => setCreditFormData({ ...creditFormData, invoice_date: e.target.value })}
                          required
                          className="bg-background"
                          data-testid="credit-date-input"
                        />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label>Supplier GSTIN</Label>
                      <Input
                        value={creditFormData.supplier_gstin}
                        onChange={(e) => setCreditFormData({ ...creditFormData, supplier_gstin: e.target.value })}
                        placeholder="22AAAAA0000A1Z5"
                        required
                        className="bg-background"
                        data-testid="credit-gstin-input"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label>Taxable Value</Label>
                        <Input
                          type="number"
                          value={creditFormData.taxable_value}
                          onChange={(e) => setCreditFormData({ ...creditFormData, taxable_value: e.target.value })}
                          required
                          className="bg-background"
                          data-testid="credit-taxable-input"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>Total Tax</Label>
                        <Input
                          type="number"
                          value={creditFormData.total_tax}
                          onChange={(e) => setCreditFormData({ ...creditFormData, total_tax: e.target.value })}
                          required
                          className="bg-background"
                          data-testid="credit-tax-input"
                        />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button type="button" variant="outline" onClick={() => setCreditDialogOpen(false)}>Cancel</Button>
                      <Button type="submit" disabled={submitting} data-testid="submit-credit-btn">
                        {submitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                        Add Credit
                      </Button>
                    </DialogFooter>
                  </form>
                </DialogContent>
              </Dialog>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <Calculator className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">Add input tax credit entries to track ITC</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Monthly Summary Tab */}
        <TabsContent value="monthly" className="space-y-4">
          <Card className="bg-card border-border" data-testid="monthly-summary-card">
            <CardHeader>
              <CardTitle className="font-heading text-lg">Monthly GST Summary</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow className="border-border hover:bg-transparent">
                    <TableHead className="text-muted-foreground">Month</TableHead>
                    <TableHead className="text-muted-foreground">Export Value</TableHead>
                    <TableHead className="text-muted-foreground">IGST Paid</TableHead>
                    <TableHead className="text-muted-foreground">Refund Claimed</TableHead>
                    <TableHead className="text-muted-foreground">Pending</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {gstSummary.slice(0, 6).map((item, index) => (
                    <TableRow key={index} className="border-border hover:bg-surface-highlight/50">
                      <TableCell>{item.month}</TableCell>
                      <TableCell className="font-mono">{formatCurrency(item.total_export_value)}</TableCell>
                      <TableCell className="font-mono">{formatCurrency(item.total_igst_paid)}</TableCell>
                      <TableCell className="font-mono text-neon">{formatCurrency(item.refund_claimed)}</TableCell>
                      <TableCell className="font-mono text-amber">{formatCurrency(item.refund_pending)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
