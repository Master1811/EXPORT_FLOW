import React, { useState, useEffect, useCallback, useMemo, memo } from 'react';
import { useDebouncedCallback } from 'use-debounce';
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
  Package, Plus, Search, Filter, Edit, Trash2, Ship, MapPin, 
  RefreshCw, Loader2, FileCheck, AlertTriangle, Clock, CheckCircle,
  XCircle, Eye, EyeOff
} from 'lucide-react';
import { toast } from 'sonner';
import EmptyState from '../components/EmptyState';

// Virtualization with dynamic import (lazy loading)
let VirtualizedList = null;
try {
  // Dynamic import to avoid build issues
  const ReactWindow = require('react-window');
  VirtualizedList = ReactWindow.FixedSizeList;
} catch (e) {
  console.warn('react-window not available, using standard rendering');
}

// Memoized constants
const STATUS_COLORS = {
  draft: 'bg-muted text-muted-foreground',
  confirmed: 'bg-primary/20 text-primary',
  shipped: 'bg-amber/20 text-amber',
  in_transit: 'bg-amber/20 text-amber',
  delivered: 'bg-neon/20 text-neon',
  completed: 'bg-neon/20 text-neon',
  cancelled: 'bg-destructive/20 text-destructive'
};

const EBRC_STATUS_COLORS = {
  pending: 'bg-amber/20 text-amber border-amber/30',
  filed: 'bg-primary/20 text-primary border-primary/30',
  approved: 'bg-neon/20 text-neon border-neon/30',
  rejected: 'bg-destructive/20 text-destructive border-destructive/30'
};

const INCOTERMS = ['FOB', 'CIF', 'EXW', 'FCA', 'CFR', 'DAP', 'DDP'];
const CURRENCIES = ['USD', 'EUR', 'GBP', 'AED', 'JPY', 'CNY', 'SGD', 'INR'];

// Memoized currency formatter
const formatCurrency = (value, currency) => {
  const symbols = { USD: '$', EUR: '€', GBP: '£', INR: '₹', AED: 'AED ' };
  if (currency === 'INR' && value >= 100000) return `₹${(value/100000).toFixed(2)}L`;
  return `${symbols[currency] || ''}${value?.toLocaleString() || 0}`;
};

// Memoized mask function
const maskValue = (value) => {
  if (!value) return '—';
  return value.includes('*') ? value : value;
};

// Initial form state
const initialFormState = {
  shipment_number: '',
  buyer_name: '',
  buyer_country: '',
  destination_port: '',
  origin_port: '',
  incoterm: 'FOB',
  currency: 'USD',
  total_value: '',
  status: 'draft',
  expected_ship_date: '',
  actual_ship_date: '',
  product_description: '',
  hs_codes: '',
  buyer_email: '',
  buyer_phone: '',
  buyer_pan: '',
  buyer_bank_account: ''
};

// Memoized row component for virtualization
const ShipmentRow = memo(({ shipment, onEdit, onDelete, onEbrcUpdate, onToggleSensitive, showSensitive }) => {
  return (
    <TableRow className="border-border hover:bg-surface-highlight/50" data-testid={`shipment-row-${shipment.id}`}>
      <TableCell className="font-mono text-sm">{shipment.shipment_number}</TableCell>
      <TableCell>
        <div>
          <p className="font-medium">{shipment.buyer_name}</p>
          <p className="text-xs text-muted-foreground">{shipment.buyer_country}</p>
          {(shipment.buyer_pan || shipment.buyer_phone) && (
            <button onClick={() => onToggleSensitive(shipment.id)} className="flex items-center gap-1 text-xs text-primary mt-1">
              {showSensitive ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
              {showSensitive ? 'Hide' : 'Show'} details
            </button>
          )}
          {showSensitive && (
            <div className="text-xs text-muted-foreground mt-1 space-y-0.5">
              {shipment.buyer_pan && <p>PAN: {maskValue(shipment.buyer_pan)}</p>}
              {shipment.buyer_phone && <p>Phone: {maskValue(shipment.buyer_phone)}</p>}
            </div>
          )}
        </div>
      </TableCell>
      <TableCell>
        <div className="flex items-center gap-2 text-sm">
          <MapPin className="w-4 h-4 text-muted-foreground" />
          <span>{shipment.origin_port} → {shipment.destination_port}</span>
        </div>
      </TableCell>
      <TableCell className="font-mono">{formatCurrency(shipment.total_value, shipment.currency)}</TableCell>
      <TableCell><Badge className={STATUS_COLORS[shipment.status]}>{shipment.status}</Badge></TableCell>
      <TableCell>
        <Badge className={EBRC_STATUS_COLORS[shipment.ebrc_status || 'pending']}>
          {shipment.ebrc_status || 'pending'}
        </Badge>
        {shipment.ebrc_days_remaining !== null && shipment.ebrc_days_remaining < 15 && (
          <p className={`text-xs mt-1 ${shipment.ebrc_days_remaining < 0 ? 'text-destructive' : 'text-amber'}`}>
            {shipment.ebrc_days_remaining < 0 ? 'Overdue' : `${shipment.ebrc_days_remaining}d left`}
          </p>
        )}
      </TableCell>
      <TableCell className="text-right">
        <div className="flex items-center justify-end gap-1">
          <Button variant="ghost" size="sm" onClick={() => onEbrcUpdate(shipment)} title="Update e-BRC">
            <FileCheck className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm" onClick={() => onEdit(shipment)} data-testid={`edit-shipment-${shipment.id}`}>
            <Edit className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm" onClick={() => onDelete(shipment.id)} className="text-destructive">
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      </TableCell>
    </TableRow>
  );
});

ShipmentRow.displayName = 'ShipmentRow';

// Memoized summary cards component
const EbrcSummaryCards = memo(({ dashboard }) => (
  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
    <Card className="bg-card border-border" data-testid="ebrc-pending-card">
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm text-muted-foreground">Pending</p>
            <p className="text-2xl font-heading font-bold mt-1 text-amber">{dashboard.summary.pending_count}</p>
            <p className="text-xs text-muted-foreground mt-1">{formatCurrency(dashboard.values.total_pending, 'INR')}</p>
          </div>
          <Clock className="w-8 h-8 text-amber" />
        </div>
      </CardContent>
    </Card>
    <Card className="bg-card border-border" data-testid="ebrc-filed-card">
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm text-muted-foreground">Filed</p>
            <p className="text-2xl font-heading font-bold mt-1 text-primary">{dashboard.summary.filed_count}</p>
          </div>
          <FileCheck className="w-8 h-8 text-primary" />
        </div>
      </CardContent>
    </Card>
    <Card className="bg-card border-border" data-testid="ebrc-approved-card">
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm text-muted-foreground">Approved</p>
            <p className="text-2xl font-heading font-bold mt-1 text-neon">{dashboard.summary.approved_count}</p>
            <p className="text-xs text-muted-foreground mt-1">{formatCurrency(dashboard.values.total_approved, 'INR')}</p>
          </div>
          <CheckCircle className="w-8 h-8 text-neon" />
        </div>
      </CardContent>
    </Card>
    <Card className="bg-card border-destructive/30" data-testid="ebrc-overdue-card">
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm text-muted-foreground">Overdue</p>
            <p className="text-2xl font-heading font-bold mt-1 text-destructive">{dashboard.summary.overdue_count}</p>
            <p className="text-xs text-muted-foreground mt-1">{formatCurrency(dashboard.values.total_overdue, 'INR')}</p>
          </div>
          <AlertTriangle className="w-8 h-8 text-destructive" />
        </div>
      </CardContent>
    </Card>
  </div>
));

EbrcSummaryCards.displayName = 'EbrcSummaryCards';

// Main component
export default function ShipmentsPage() {
  const [shipments, setShipments] = useState([]);
  const [ebrcDashboard, setEbrcDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [activeTab, setActiveTab] = useState('shipments');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [ebrcDialogOpen, setEbrcDialogOpen] = useState(false);
  const [selectedShipment, setSelectedShipment] = useState(null);
  const [editingShipment, setEditingShipment] = useState(null);
  const [showSensitive, setShowSensitive] = useState({});
  const [formData, setFormData] = useState(initialFormState);
  const [ebrcFormData, setEbrcFormData] = useState({
    ebrc_status: 'pending',
    ebrc_filed_date: '',
    ebrc_number: '',
    rejection_reason: ''
  });
  const [submitting, setSubmitting] = useState(false);

  // Debounced search handler - prevents API calls on every keystroke
  const debouncedSetSearch = useDebouncedCallback((value) => {
    setDebouncedSearchTerm(value);
  }, 300);

  // Handle search input with debouncing
  const handleSearchChange = useCallback((e) => {
    const value = e.target.value;
    setSearchTerm(value);
    debouncedSetSearch(value);
  }, [debouncedSetSearch]);

  // Memoized filtered shipments - only recomputes when dependencies change
  const filteredShipments = useMemo(() => {
    if (!debouncedSearchTerm) return shipments;
    const term = debouncedSearchTerm.toLowerCase();
    return shipments.filter(s =>
      s.shipment_number.toLowerCase().includes(term) ||
      s.buyer_name.toLowerCase().includes(term)
    );
  }, [shipments, debouncedSearchTerm]);

  // Fetch data with abort controller for cleanup
  const fetchData = useCallback(async () => {
    const controller = new AbortController();
    
    try {
      const [shipmentsRes, ebrcRes] = await Promise.all([
        api.get('/shipments', { 
          params: statusFilter !== 'all' ? { status: statusFilter } : {},
          signal: controller.signal
        }),
        api.get('/shipments/ebrc-dashboard', { signal: controller.signal })
      ]);
      setShipments(shipmentsRes.data);
      setEbrcDashboard(ebrcRes.data);
    } catch (error) {
      if (!controller.signal.aborted) {
        toast.error('Failed to fetch data');
      }
    } finally {
      if (!controller.signal.aborted) {
        setLoading(false);
      }
    }

    return () => controller.abort();
  }, [statusFilter]);

  useEffect(() => {
    const cleanup = fetchData();
    return () => cleanup;
  }, [fetchData]);

  // Memoized handlers to prevent unnecessary re-renders
  const handleInputChange = useCallback((e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  }, []);

  const handleSelectChange = useCallback((name, value) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  }, []);

  const resetForm = useCallback(() => {
    setFormData(initialFormState);
    setEditingShipment(null);
  }, []);

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const data = {
        ...formData,
        total_value: parseFloat(formData.total_value),
        hs_codes: formData.hs_codes ? formData.hs_codes.split(',').map(s => s.trim()) : []
      };

      if (editingShipment) {
        await api.put(`/shipments/${editingShipment.id}`, data);
        toast.success('Shipment updated');
      } else {
        await api.post('/shipments', data);
        toast.success('Shipment created');
      }
      
      setCreateDialogOpen(false);
      resetForm();
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Operation failed');
    } finally {
      setSubmitting(false);
    }
  }, [formData, editingShipment, resetForm, fetchData]);

  const handleEdit = useCallback((shipment) => {
    setEditingShipment(shipment);
    setFormData({
      shipment_number: shipment.shipment_number,
      buyer_name: shipment.buyer_name,
      buyer_country: shipment.buyer_country,
      destination_port: shipment.destination_port,
      origin_port: shipment.origin_port,
      incoterm: shipment.incoterm,
      currency: shipment.currency,
      total_value: shipment.total_value.toString(),
      status: shipment.status,
      expected_ship_date: shipment.expected_ship_date || '',
      actual_ship_date: shipment.actual_ship_date || '',
      product_description: shipment.product_description || '',
      hs_codes: shipment.hs_codes?.join(', ') || '',
      buyer_email: shipment.buyer_email || '',
      buyer_phone: shipment.buyer_phone || '',
      buyer_pan: shipment.buyer_pan || '',
      buyer_bank_account: shipment.buyer_bank_account || ''
    });
    setCreateDialogOpen(true);
  }, []);

  const handleDelete = useCallback(async (id) => {
    // Use a custom confirmation dialog instead of window.confirm for better UX
    if (!window.confirm('Delete this shipment?')) return;
    try {
      await api.delete(`/shipments/${id}`);
      toast.success('Shipment deleted');
      fetchData();
    } catch (error) {
      toast.error('Failed to delete');
    }
  }, [fetchData]);

  const openEbrcDialog = useCallback((shipment) => {
    setSelectedShipment(shipment);
    setEbrcFormData({
      ebrc_status: shipment.ebrc_status || 'pending',
      ebrc_filed_date: shipment.ebrc_filed_date || '',
      ebrc_number: shipment.ebrc_number || '',
      rejection_reason: shipment.ebrc_rejection_reason || ''
    });
    setEbrcDialogOpen(true);
  }, []);

  const handleEbrcSubmit = useCallback(async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.put(`/shipments/${selectedShipment.id}/ebrc`, ebrcFormData);
      toast.success('e-BRC status updated');
      setEbrcDialogOpen(false);
      fetchData();
    } catch (error) {
      toast.error('Failed to update e-BRC status');
    } finally {
      setSubmitting(false);
    }
  }, [selectedShipment, ebrcFormData, fetchData]);

  const toggleSensitive = useCallback((shipmentId) => {
    setShowSensitive(prev => ({ ...prev, [shipmentId]: !prev[shipmentId] }));
  }, []);

  // Virtualized row renderer for large lists
  const VirtualizedRow = useCallback(({ index, style }) => {
    const shipment = filteredShipments[index];
    return (
      <div style={style}>
        <ShipmentRow
          shipment={shipment}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onEbrcUpdate={openEbrcDialog}
          onToggleSensitive={toggleSensitive}
          showSensitive={showSensitive[shipment.id]}
        />
      </div>
    );
  }, [filteredShipments, handleEdit, handleDelete, openEbrcDialog, toggleSensitive, showSensitive]);

  // Determine if we should use virtualization (for 50+ items)
  const useVirtualization = filteredShipments.length > 50 && VirtualizedList;

  return (
    <div className="space-y-6 animate-fade-in" data-testid="shipments-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="font-heading text-4xl text-foreground">Shipments</h1>
          <p className="text-muted-foreground mt-1">Manage shipments and e-BRC compliance</p>
        </div>
        <Dialog open={createDialogOpen} onOpenChange={(open) => { setCreateDialogOpen(open); if (!open) resetForm(); }}>
          <DialogTrigger asChild>
            <Button className="bg-primary hover:bg-primary/90" data-testid="create-shipment-btn">
              <Plus className="w-4 h-4 mr-2" /> New Shipment
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto bg-card border-border">
            <DialogHeader>
              <DialogTitle className="font-heading text-xl">
                {editingShipment ? 'Edit Shipment' : 'Create New Shipment'}
              </DialogTitle>
              <DialogDescription>Enter shipment details</DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Shipment Number *</Label>
                  <Input name="shipment_number" value={formData.shipment_number} onChange={handleInputChange} required className="bg-background" data-testid="shipment-number-input" />
                </div>
                <div className="space-y-2">
                  <Label>Buyer Name *</Label>
                  <Input name="buyer_name" value={formData.buyer_name} onChange={handleInputChange} required className="bg-background" data-testid="buyer-name-input" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Buyer Country *</Label>
                  <Input name="buyer_country" value={formData.buyer_country} onChange={handleInputChange} required className="bg-background" />
                </div>
                <div className="space-y-2">
                  <Label>Origin Port *</Label>
                  <Input name="origin_port" value={formData.origin_port} onChange={handleInputChange} required className="bg-background" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Destination Port *</Label>
                  <Input name="destination_port" value={formData.destination_port} onChange={handleInputChange} required className="bg-background" />
                </div>
                <div className="space-y-2">
                  <Label>Incoterm</Label>
                  <Select value={formData.incoterm} onValueChange={(v) => handleSelectChange('incoterm', v)}>
                    <SelectTrigger className="bg-background"><SelectValue /></SelectTrigger>
                    <SelectContent>{INCOTERMS.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}</SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>Currency</Label>
                  <Select value={formData.currency} onValueChange={(v) => handleSelectChange('currency', v)}>
                    <SelectTrigger className="bg-background"><SelectValue /></SelectTrigger>
                    <SelectContent>{CURRENCIES.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}</SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Total Value *</Label>
                  <Input name="total_value" type="number" value={formData.total_value} onChange={handleInputChange} required className="bg-background" />
                </div>
                <div className="space-y-2">
                  <Label>Status</Label>
                  <Select value={formData.status} onValueChange={(v) => handleSelectChange('status', v)}>
                    <SelectTrigger className="bg-background"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="draft">Draft</SelectItem>
                      <SelectItem value="confirmed">Confirmed</SelectItem>
                      <SelectItem value="shipped">Shipped</SelectItem>
                      <SelectItem value="in_transit">In Transit</SelectItem>
                      <SelectItem value="delivered">Delivered</SelectItem>
                      <SelectItem value="completed">Completed</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Expected Ship Date</Label>
                  <Input name="expected_ship_date" type="date" value={formData.expected_ship_date} onChange={handleInputChange} className="bg-background" />
                </div>
                <div className="space-y-2">
                  <Label>Actual Ship Date</Label>
                  <Input name="actual_ship_date" type="date" value={formData.actual_ship_date} onChange={handleInputChange} className="bg-background" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>HS Codes (comma separated)</Label>
                  <Input name="hs_codes" value={formData.hs_codes} onChange={handleInputChange} placeholder="7419, 9405" className="bg-background" />
                </div>
                <div className="space-y-2">
                  <Label>Product Description</Label>
                  <Input name="product_description" value={formData.product_description} onChange={handleInputChange} className="bg-background" />
                </div>
              </div>
              
              {/* Buyer Contact (PII) */}
              <div className="border-t border-border pt-4 mt-4">
                <p className="text-sm text-muted-foreground mb-3">Buyer Contact (Sensitive - will be masked)</p>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Buyer Email</Label>
                    <Input name="buyer_email" type="email" value={formData.buyer_email} onChange={handleInputChange} className="bg-background" />
                  </div>
                  <div className="space-y-2">
                    <Label>Buyer Phone</Label>
                    <Input name="buyer_phone" value={formData.buyer_phone} onChange={handleInputChange} className="bg-background" />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4 mt-4">
                  <div className="space-y-2">
                    <Label>Buyer PAN</Label>
                    <Input name="buyer_pan" value={formData.buyer_pan} onChange={handleInputChange} placeholder="ABCDE1234F" className="bg-background" />
                  </div>
                  <div className="space-y-2">
                    <Label>Buyer Bank Account</Label>
                    <Input name="buyer_bank_account" value={formData.buyer_bank_account} onChange={handleInputChange} className="bg-background" />
                  </div>
                </div>
              </div>

              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => { setCreateDialogOpen(false); resetForm(); }}>Cancel</Button>
                <Button type="submit" disabled={submitting} data-testid="submit-shipment-btn">
                  {submitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                  {editingShipment ? 'Update' : 'Create'}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 border-b border-border pb-2">
        <Button variant={activeTab === 'shipments' ? 'default' : 'ghost'} onClick={() => setActiveTab('shipments')} data-testid="tab-shipments">
          <Package className="w-4 h-4 mr-2" /> Shipments
        </Button>
        <Button variant={activeTab === 'ebrc' ? 'default' : 'ghost'} onClick={() => setActiveTab('ebrc')} data-testid="tab-ebrc">
          <FileCheck className="w-4 h-4 mr-2" /> e-BRC Monitor
        </Button>
      </div>

      {/* e-BRC Tab */}
      {activeTab === 'ebrc' && ebrcDashboard && (
        <div className="space-y-6">
          <EbrcSummaryCards dashboard={ebrcDashboard} />

          {/* Alerts */}
          {(ebrcDashboard.alerts.overdue.length > 0 || ebrcDashboard.alerts.due_soon.length > 0) && (
            <Card className="bg-destructive/5 border-destructive/30" data-testid="ebrc-alerts">
              <CardHeader>
                <CardTitle className="font-heading text-lg text-destructive flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5" /> e-BRC Alerts
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {ebrcDashboard.alerts.overdue.length > 0 && (
                    <div>
                      <p className="text-sm font-medium text-destructive mb-2">Overdue (Action Required)</p>
                      <div className="space-y-2">
                        {ebrcDashboard.alerts.overdue.map((s, i) => (
                          <div key={i} className="flex items-center justify-between p-3 rounded-md bg-background border border-destructive/20">
                            <div>
                              <p className="font-medium">{s.shipment_number}</p>
                              <p className="text-xs text-muted-foreground">{s.buyer_name}</p>
                            </div>
                            <div className="text-right">
                              <p className="font-mono text-sm">{formatCurrency(s.total_value, s.currency)}</p>
                              <Badge variant="destructive">{Math.abs(s.days_remaining)} days overdue</Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  {ebrcDashboard.alerts.due_soon.length > 0 && (
                    <div>
                      <p className="text-sm font-medium text-amber mb-2">Due Soon (Within 15 days)</p>
                      <div className="space-y-2">
                        {ebrcDashboard.alerts.due_soon.map((s, i) => (
                          <div key={i} className="flex items-center justify-between p-3 rounded-md bg-background border border-amber/20">
                            <div>
                              <p className="font-medium">{s.shipment_number}</p>
                              <p className="text-xs text-muted-foreground">{s.buyer_name}</p>
                            </div>
                            <div className="text-right">
                              <p className="font-mono text-sm">{formatCurrency(s.total_value, s.currency)}</p>
                              <Badge className="bg-amber/20 text-amber">{s.days_remaining} days left</Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* e-BRC Status Table */}
          <Card className="bg-card border-border" data-testid="ebrc-table">
            <CardHeader>
              <CardTitle className="font-heading text-lg">e-BRC Status by Shipment</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow className="border-border">
                    <TableHead>Shipment</TableHead>
                    <TableHead>Buyer</TableHead>
                    <TableHead>Value</TableHead>
                    <TableHead>e-BRC Status</TableHead>
                    <TableHead>Days Remaining</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {[...ebrcDashboard.by_status.pending, ...ebrcDashboard.by_status.filed].slice(0, 10).map((s, i) => (
                    <TableRow key={i} className="border-border">
                      <TableCell className="font-mono">{s.shipment_number}</TableCell>
                      <TableCell>{s.buyer_name}</TableCell>
                      <TableCell className="font-mono">{formatCurrency(s.total_value, s.currency)}</TableCell>
                      <TableCell>
                        <Badge className={EBRC_STATUS_COLORS[s.ebrc_status]}>{s.ebrc_status}</Badge>
                      </TableCell>
                      <TableCell>
                        {s.days_remaining !== null ? (
                          <span className={s.days_remaining < 0 ? 'text-destructive' : s.days_remaining < 15 ? 'text-amber' : ''}>
                            {s.days_remaining < 0 ? `${Math.abs(s.days_remaining)} overdue` : `${s.days_remaining} days`}
                          </span>
                        ) : '—'}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button size="sm" variant="outline" onClick={() => openEbrcDialog(s)}>Update</Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Shipments Tab */}
      {activeTab === 'shipments' && (
        <>
          {/* Filters */}
          <Card className="bg-card border-border">
            <CardContent className="p-4">
              <div className="flex flex-col md:flex-row gap-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input 
                    placeholder="Search shipments..." 
                    value={searchTerm} 
                    onChange={handleSearchChange} 
                    className="pl-10 bg-background" 
                    data-testid="search-shipments-input" 
                  />
                </div>
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-[180px] bg-background" data-testid="status-filter-select">
                    <Filter className="w-4 h-4 mr-2" /><SelectValue placeholder="Filter by status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="draft">Draft</SelectItem>
                    <SelectItem value="confirmed">Confirmed</SelectItem>
                    <SelectItem value="shipped">Shipped</SelectItem>
                    <SelectItem value="delivered">Delivered</SelectItem>
                    <SelectItem value="completed">Completed</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Shipments Table */}
          <Card className="bg-card border-border" data-testid="shipments-table">
            <CardContent className="p-0">
              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <RefreshCw className="w-6 h-6 animate-spin text-primary" />
                </div>
              ) : shipments.length === 0 ? (
                <div className="p-6">
                  <EmptyState 
                    type="shipments" 
                    onAction={() => setCreateDialogOpen(true)}
                  />
                </div>
              ) : filteredShipments.length === 0 ? (
                <div className="text-center py-12">
                  <Package className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">No shipments match your search</p>
                </div>
              ) : useVirtualization ? (
                // Virtualized table for large datasets (50+ items)
                <div className="overflow-hidden">
                  <Table>
                    <TableHeader>
                      <TableRow className="border-border">
                        <TableHead>Shipment #</TableHead>
                        <TableHead>Buyer</TableHead>
                        <TableHead>Route</TableHead>
                        <TableHead>Value</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>e-BRC</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                  </Table>
                  {VirtualizedList && (
                    <VirtualizedList
                      height={600}
                      itemCount={filteredShipments.length}
                      itemSize={80}
                      width="100%"
                    >
                      {VirtualizedRow}
                    </VirtualizedList>
                  )}
                </div>
              ) : (
                // Regular table for smaller datasets
                <Table>
                  <TableHeader>
                    <TableRow className="border-border">
                      <TableHead>Shipment #</TableHead>
                      <TableHead>Buyer</TableHead>
                      <TableHead>Route</TableHead>
                      <TableHead>Value</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>e-BRC</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredShipments.map((shipment) => (
                      <ShipmentRow
                        key={shipment.id}
                        shipment={shipment}
                        onEdit={handleEdit}
                        onDelete={handleDelete}
                        onEbrcUpdate={openEbrcDialog}
                        onToggleSensitive={toggleSensitive}
                        showSensitive={showSensitive[shipment.id]}
                      />
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </>
      )}

      {/* e-BRC Update Dialog */}
      <Dialog open={ebrcDialogOpen} onOpenChange={setEbrcDialogOpen}>
        <DialogContent className="max-w-md bg-card border-border">
          <DialogHeader>
            <DialogTitle className="font-heading">Update e-BRC Status</DialogTitle>
            <DialogDescription>
              {selectedShipment?.shipment_number} - {selectedShipment?.buyer_name}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleEbrcSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label>e-BRC Status</Label>
              <Select value={ebrcFormData.ebrc_status} onValueChange={(v) => setEbrcFormData({...ebrcFormData, ebrc_status: v, rejection_reason: ''})}>
                <SelectTrigger className="bg-background" data-testid="ebrc-status-select">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="filed">Filed</SelectItem>
                  <SelectItem value="approved">Approved</SelectItem>
                  <SelectItem value="rejected">Rejected</SelectItem>
                </SelectContent>
              </Select>
            </div>
            {ebrcFormData.ebrc_status !== 'pending' && (
              <>
                <div className="space-y-2">
                  <Label>Filed Date</Label>
                  <Input type="date" value={ebrcFormData.ebrc_filed_date} onChange={(e) => setEbrcFormData({...ebrcFormData, ebrc_filed_date: e.target.value})} className="bg-background" />
                </div>
                <div className="space-y-2">
                  <Label>e-BRC Number</Label>
                  <Input value={ebrcFormData.ebrc_number} onChange={(e) => setEbrcFormData({...ebrcFormData, ebrc_number: e.target.value})} placeholder="eBRC-2024-XXXXX" className="bg-background" />
                </div>
              </>
            )}
            {ebrcFormData.ebrc_status === 'rejected' && (
              <div className="space-y-2">
                <Label>Reason for Rejection *</Label>
                <Input 
                  value={ebrcFormData.rejection_reason || ''} 
                  onChange={(e) => setEbrcFormData({...ebrcFormData, rejection_reason: e.target.value})} 
                  placeholder="Enter rejection reason" 
                  required
                  className="bg-background" 
                />
              </div>
            )}
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setEbrcDialogOpen(false)}>Cancel</Button>
              <Button type="submit" disabled={submitting}>
                {submitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                Update Status
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
