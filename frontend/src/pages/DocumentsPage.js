import React, { useState, useEffect } from 'react';
import { api } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue
} from '../components/ui/select';
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow
} from '../components/ui/table';
import {
  FileText, Upload, Download, Search, Filter, RefreshCw,
  File, FileSpreadsheet, FileCheck, Loader2, Eye, Trash2
} from 'lucide-react';
import { toast } from 'sonner';

const DOC_TYPE_ICONS = {
  invoice: FileText,
  packing_list: FileSpreadsheet,
  shipping_bill: FileCheck,
  default: File
};

const DOC_TYPE_COLORS = {
  invoice: 'bg-primary/20 text-primary',
  packing_list: 'bg-neon/20 text-neon',
  shipping_bill: 'bg-amber/20 text-amber',
  default: 'bg-muted text-muted-foreground'
};

export default function DocumentsPage() {
  const [documents, setDocuments] = useState([]);
  const [shipments, setShipments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedShipment, setSelectedShipment] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const shipmentsRes = await api.get('/shipments');
      setShipments(shipmentsRes.data);
      
      // Fetch documents for each shipment
      const allDocs = [];
      for (const shipment of shipmentsRes.data.slice(0, 20)) {
        try {
          const docsRes = await api.get(`/shipments/${shipment.id}/documents`);
          allDocs.push(...docsRes.data.map(d => ({ ...d, shipment_number: shipment.shipment_number })));
        } catch (e) {}
      }
      setDocuments(allDocs);
    } catch (error) {
      toast.error('Failed to fetch documents');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      await api.post('/files/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      toast.success('File uploaded successfully');
      fetchData();
    } catch (error) {
      toast.error('Failed to upload file');
    } finally {
      setUploading(false);
    }
  };

  const handleOCRExtract = async () => {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.pdf,.png,.jpg,.jpeg';
    fileInput.onchange = async (e) => {
      const file = e.target.files[0];
      if (!file) return;
      
      const formData = new FormData();
      formData.append('file', file);
      
      try {
        const response = await api.post('/documents/ocr/extract', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        toast.success(`OCR job started: ${response.data.job_id}`);
      } catch (error) {
        toast.error('Failed to start OCR extraction');
      }
    };
    fileInput.click();
  };

  const filteredDocuments = documents.filter(doc => {
    const matchesShipment = selectedShipment === 'all' || doc.shipment_id === selectedShipment;
    const matchesSearch = doc.document_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.shipment_number?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesShipment && matchesSearch;
  });

  const getDocIcon = (type) => {
    const Icon = DOC_TYPE_ICONS[type] || DOC_TYPE_ICONS.default;
    return Icon;
  };

  return (
    <div className="space-y-6 animate-fade-in" data-testid="documents-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="font-heading text-4xl text-foreground">Trade Documents</h1>
          <p className="text-muted-foreground mt-1">Manage invoices, packing lists, and shipping bills</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleOCRExtract} data-testid="ocr-extract-btn">
            <FileText className="w-4 h-4 mr-2" />
            OCR Extract
          </Button>
          <div className="relative">
            <input
              type="file"
              onChange={handleFileUpload}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              disabled={uploading}
              data-testid="file-upload-input"
            />
            <Button disabled={uploading} data-testid="upload-btn">
              {uploading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Upload className="w-4 h-4 mr-2" />}
              Upload Document
            </Button>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-card border-border" data-testid="total-docs-card">
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Documents</p>
                <p className="text-2xl font-heading font-bold mt-1">{documents.length}</p>
              </div>
              <div className="w-12 h-12 rounded-md bg-primary/10 flex items-center justify-center">
                <FileText className="w-6 h-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border" data-testid="invoices-card">
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Invoices</p>
                <p className="text-2xl font-heading font-bold mt-1">
                  {documents.filter(d => d.document_type === 'invoice').length}
                </p>
              </div>
              <div className="w-12 h-12 rounded-md bg-primary/10 flex items-center justify-center">
                <FileText className="w-6 h-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border" data-testid="packing-lists-card">
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Packing Lists</p>
                <p className="text-2xl font-heading font-bold mt-1">
                  {documents.filter(d => d.document_type === 'packing_list').length}
                </p>
              </div>
              <div className="w-12 h-12 rounded-md bg-neon/10 flex items-center justify-center">
                <FileSpreadsheet className="w-6 h-6 text-neon" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border" data-testid="shipping-bills-card">
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Shipping Bills</p>
                <p className="text-2xl font-heading font-bold mt-1">
                  {documents.filter(d => d.document_type === 'shipping_bill').length}
                </p>
              </div>
              <div className="w-12 h-12 rounded-md bg-amber/10 flex items-center justify-center">
                <FileCheck className="w-6 h-6 text-amber" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card className="bg-card border-border">
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search documents..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 bg-background"
                data-testid="search-documents-input"
              />
            </div>
            <Select value={selectedShipment} onValueChange={setSelectedShipment}>
              <SelectTrigger className="w-[200px] bg-background" data-testid="shipment-filter-select">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Filter by shipment" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Shipments</SelectItem>
                {shipments.map(s => (
                  <SelectItem key={s.id} value={s.id}>{s.shipment_number}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Documents Table */}
      <Card className="bg-card border-border" data-testid="documents-table">
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="w-6 h-6 animate-spin text-primary" />
            </div>
          ) : filteredDocuments.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">No documents found</p>
              <p className="text-sm text-muted-foreground mt-1">
                Create shipments and add documents to see them here
              </p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="border-border hover:bg-transparent">
                  <TableHead className="text-muted-foreground">Document</TableHead>
                  <TableHead className="text-muted-foreground">Type</TableHead>
                  <TableHead className="text-muted-foreground">Shipment</TableHead>
                  <TableHead className="text-muted-foreground">Created</TableHead>
                  <TableHead className="text-muted-foreground text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredDocuments.map((doc) => {
                  const Icon = getDocIcon(doc.document_type);
                  return (
                    <TableRow 
                      key={doc.id} 
                      className="border-border hover:bg-surface-highlight/50"
                      data-testid={`doc-row-${doc.id}`}
                    >
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <div className={`w-10 h-10 rounded-md flex items-center justify-center ${DOC_TYPE_COLORS[doc.document_type] || DOC_TYPE_COLORS.default}`}>
                            <Icon className="w-5 h-5" />
                          </div>
                          <span className="font-mono text-sm">{doc.document_number}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={DOC_TYPE_COLORS[doc.document_type] || DOC_TYPE_COLORS.default}>
                          {doc.document_type?.replace('_', ' ')}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-mono text-sm">{doc.shipment_number}</TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {new Date(doc.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button variant="ghost" size="sm" data-testid={`view-doc-${doc.id}`}>
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm" data-testid={`download-doc-${doc.id}`}>
                            <Download className="w-4 h-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
