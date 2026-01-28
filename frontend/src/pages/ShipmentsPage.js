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
  Package, Plus, Search, Filter, Eye, Edit, Trash2,
  Ship, MapPin, Calendar, DollarSign, RefreshCw, Loader2
} from 'lucide-react';
import { toast } from 'sonner';

const STATUS_COLORS = {
  draft: 'bg-muted text-muted-foreground',
  confirmed: 'bg-primary/20 text-primary',
  shipped: 'bg-amber/20 text-amber',
  delivered: 'bg-neon/20 text-neon',
  completed: 'bg-neon/20 text-neon',
  cancelled: 'bg-destructive/20 text-destructive'
};

const INCOTERMS = ['FOB', 'CIF', 'EXW', 'FCA', 'CFR', 'DAP', 'DDP'];
const CURRENCIES = ['USD', 'EUR', 'GBP', 'AED', 'JPY', 'CNY', 'SGD'];

export default function ShipmentsPage() {
  const [shipments, setShipments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editingShipment, setEditingShipment] = useState(null);
  const [formData, setFormData] = useState({
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
    product_description: '',
    hs_codes: ''
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchShipments();
  }, [statusFilter]);

  const fetchShipments = async () => {
    try {
      const params = statusFilter !== 'all' ? { status: statusFilter } : {};
      const response = await api.get('/shipments', { params });
      setShipments(response.data);
    } catch (error) {
      toast.error('Failed to fetch shipments');
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

  const resetForm = () => {
    setFormData({
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
      product_description: '',
      hs_codes: ''
    });
    setEditingShipment(null);
  };

  const handleSubmit = async (e) => {
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
        toast.success('Shipment updated successfully');
      } else {
        await api.post('/shipments', data);
        toast.success('Shipment created successfully');
      }
      
      setCreateDialogOpen(false);
      resetForm();
      fetchShipments();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Operation failed');
    } finally {
      setSubmitting(false);
    }
  };

  const handleEdit = (shipment) => {
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
      product_description: shipment.product_description || '',
      hs_codes: shipment.hs_codes?.join(', ') || ''
    });
    setCreateDialogOpen(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this shipment?')) return;
    try {
      await api.delete(`/shipments/${id}`);
      toast.success('Shipment deleted');
      fetchShipments();
    } catch (error) {
      toast.error('Failed to delete shipment');
    }
  };

  const filteredShipments = shipments.filter(s =>
    s.shipment_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.buyer_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const formatCurrency = (value, currency) => {
    const symbols = { USD: '$', EUR: '€', GBP: '£', INR: '₹', AED: 'AED ', JPY: '¥', CNY: '¥', SGD: 'S$' };
    return `${symbols[currency] || ''}${value.toLocaleString()}`;
  };

  return (
    <div className="space-y-6 animate-fade-in" data-testid="shipments-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="font-heading text-4xl text-foreground">Shipments</h1>
          <p className="text-muted-foreground mt-1">Manage your export shipments</p>
        </div>
        <Dialog open={createDialogOpen} onOpenChange={(open) => { setCreateDialogOpen(open); if (!open) resetForm(); }}>
          <DialogTrigger asChild>
            <Button className="bg-primary hover:bg-primary/90" data-testid="create-shipment-btn">
              <Plus className="w-4 h-4 mr-2" />
              New Shipment
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto bg-card border-border">
            <DialogHeader>
              <DialogTitle className="font-heading text-xl">
                {editingShipment ? 'Edit Shipment' : 'Create New Shipment'}
              </DialogTitle>
              <DialogDescription>Enter shipment details below</DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="shipment_number">Shipment Number *</Label>
                  <Input
                    id="shipment_number"
                    name="shipment_number"
                    value={formData.shipment_number}
                    onChange={handleInputChange}
                    placeholder="SH-2024-001"
                    required
                    className="bg-background"
                    data-testid="shipment-number-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="buyer_name">Buyer Name *</Label>
                  <Input
                    id="buyer_name"
                    name="buyer_name"
                    value={formData.buyer_name}
                    onChange={handleInputChange}
                    placeholder="ABC Corp"
                    required
                    className="bg-background"
                    data-testid="buyer-name-input"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="buyer_country">Buyer Country *</Label>
                  <Input
                    id="buyer_country"
                    name="buyer_country"
                    value={formData.buyer_country}
                    onChange={handleInputChange}
                    placeholder="USA"
                    required
                    className="bg-background"
                    data-testid="buyer-country-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="origin_port">Origin Port *</Label>
                  <Input
                    id="origin_port"
                    name="origin_port"
                    value={formData.origin_port}
                    onChange={handleInputChange}
                    placeholder="INNSA (Nhava Sheva)"
                    required
                    className="bg-background"
                    data-testid="origin-port-input"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="destination_port">Destination Port *</Label>
                  <Input
                    id="destination_port"
                    name="destination_port"
                    value={formData.destination_port}
                    onChange={handleInputChange}
                    placeholder="USLAX (Los Angeles)"
                    required
                    className="bg-background"
                    data-testid="destination-port-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="incoterm">Incoterm</Label>
                  <Select value={formData.incoterm} onValueChange={(v) => handleSelectChange('incoterm', v)}>
                    <SelectTrigger className="bg-background" data-testid="incoterm-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {INCOTERMS.map(term => (
                        <SelectItem key={term} value={term}>{term}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="currency">Currency</Label>
                  <Select value={formData.currency} onValueChange={(v) => handleSelectChange('currency', v)}>
                    <SelectTrigger className="bg-background" data-testid="currency-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {CURRENCIES.map(curr => (
                        <SelectItem key={curr} value={curr}>{curr}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="total_value">Total Value *</Label>
                  <Input
                    id="total_value"
                    name="total_value"
                    type="number"
                    value={formData.total_value}
                    onChange={handleInputChange}
                    placeholder="50000"
                    required
                    min="0"
                    step="0.01"
                    className="bg-background"
                    data-testid="total-value-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="status">Status</Label>
                  <Select value={formData.status} onValueChange={(v) => handleSelectChange('status', v)}>
                    <SelectTrigger className="bg-background" data-testid="status-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="draft">Draft</SelectItem>
                      <SelectItem value="confirmed">Confirmed</SelectItem>
                      <SelectItem value="shipped">Shipped</SelectItem>
                      <SelectItem value="delivered">Delivered</SelectItem>
                      <SelectItem value="completed">Completed</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="expected_ship_date">Expected Ship Date</Label>
                  <Input
                    id="expected_ship_date"
                    name="expected_ship_date"
                    type="date"
                    value={formData.expected_ship_date}
                    onChange={handleInputChange}
                    className="bg-background"
                    data-testid="ship-date-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="hs_codes">HS Codes (comma separated)</Label>
                  <Input
                    id="hs_codes"
                    name="hs_codes"
                    value={formData.hs_codes}
                    onChange={handleInputChange}
                    placeholder="8471, 8542"
                    className="bg-background"
                    data-testid="hs-codes-input"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="product_description">Product Description</Label>
                <Input
                  id="product_description"
                  name="product_description"
                  value={formData.product_description}
                  onChange={handleInputChange}
                  placeholder="Electronic components and accessories"
                  className="bg-background"
                  data-testid="product-description-input"
                />
              </div>

              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => { setCreateDialogOpen(false); resetForm(); }}>
                  Cancel
                </Button>
                <Button type="submit" disabled={submitting} data-testid="submit-shipment-btn">
                  {submitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                  {editingShipment ? 'Update' : 'Create'} Shipment
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filters */}
      <Card className="bg-card border-border">
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search shipments..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 bg-background"
                data-testid="search-shipments-input"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[180px] bg-background" data-testid="status-filter-select">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Filter by status" />
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
          ) : filteredShipments.length === 0 ? (
            <div className="text-center py-12">
              <Package className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">No shipments found</p>
              <Button 
                variant="outline" 
                className="mt-4"
                onClick={() => setCreateDialogOpen(true)}
              >
                Create your first shipment
              </Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="border-border hover:bg-transparent">
                  <TableHead className="text-muted-foreground">Shipment #</TableHead>
                  <TableHead className="text-muted-foreground">Buyer</TableHead>
                  <TableHead className="text-muted-foreground">Route</TableHead>
                  <TableHead className="text-muted-foreground">Value</TableHead>
                  <TableHead className="text-muted-foreground">Status</TableHead>
                  <TableHead className="text-muted-foreground text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredShipments.map((shipment) => (
                  <TableRow 
                    key={shipment.id} 
                    className="border-border hover:bg-surface-highlight/50 cursor-pointer"
                    data-testid={`shipment-row-${shipment.id}`}
                  >
                    <TableCell className="font-mono text-sm">{shipment.shipment_number}</TableCell>
                    <TableCell>
                      <div>
                        <p className="font-medium">{shipment.buyer_name}</p>
                        <p className="text-xs text-muted-foreground">{shipment.buyer_country}</p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2 text-sm">
                        <MapPin className="w-4 h-4 text-muted-foreground" />
                        <span>{shipment.origin_port}</span>
                        <span className="text-muted-foreground">→</span>
                        <span>{shipment.destination_port}</span>
                      </div>
                    </TableCell>
                    <TableCell className="font-mono">
                      {formatCurrency(shipment.total_value, shipment.currency)}
                    </TableCell>
                    <TableCell>
                      <Badge className={STATUS_COLORS[shipment.status]}>
                        {shipment.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEdit(shipment)}
                          data-testid={`edit-shipment-${shipment.id}`}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(shipment.id)}
                          className="text-destructive hover:text-destructive"
                          data-testid={`delete-shipment-${shipment.id}`}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
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
