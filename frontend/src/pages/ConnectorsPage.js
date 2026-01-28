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
  Link2, RefreshCw, CheckCircle, AlertCircle, Clock,
  Building2, Landmark, Package, Plus, Loader2
} from 'lucide-react';
import { toast } from 'sonner';

const connectorTypes = [
  { 
    id: 'bank', 
    name: 'Bank (Account Aggregator)', 
    icon: Landmark, 
    color: 'primary',
    description: 'Connect your bank accounts via Account Aggregator for real-time transaction data'
  },
  { 
    id: 'gst', 
    name: 'GST Portal', 
    icon: Building2, 
    color: 'neon',
    description: 'Link your GSTIN to fetch returns, ITC, and compliance data'
  },
  { 
    id: 'customs', 
    name: 'ICEGATE (Customs)', 
    icon: Package, 
    color: 'amber',
    description: 'Connect to ICEGATE for shipping bills and duty drawback status'
  }
];

export default function ConnectorsPage() {
  const [bankStatus, setBankStatus] = useState(null);
  const [gstStatus, setGstStatus] = useState(null);
  const [customsStatus, setCustomsStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [connectDialogOpen, setConnectDialogOpen] = useState(false);
  const [selectedConnector, setSelectedConnector] = useState(null);
  const [formData, setFormData] = useState({});
  const [connecting, setConnecting] = useState(false);

  useEffect(() => {
    fetchConnectorStatus();
  }, []);

  const fetchConnectorStatus = async () => {
    try {
      const [bankRes, gstRes, customsRes] = await Promise.all([
        api.get('/sync/bank'),
        api.get('/sync/gst'),
        api.get('/sync/customs')
      ]);
      setBankStatus(bankRes.data);
      setGstStatus(gstRes.data);
      setCustomsStatus(customsRes.data);
    } catch (error) {
      console.error('Failed to fetch connector status:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async (e) => {
    e.preventDefault();
    setConnecting(true);
    
    try {
      if (selectedConnector === 'bank') {
        await api.post('/connect/bank/initiate', { connector_type: 'bank', credentials: formData });
        toast.success('Bank connection initiated');
      } else if (selectedConnector === 'gst') {
        await api.post('/connect/gst/link', formData);
        toast.success('GST linked successfully');
      } else if (selectedConnector === 'customs') {
        await api.post('/connect/customs/link', formData);
        toast.success('Customs linked successfully');
      }
      setConnectDialogOpen(false);
      setFormData({});
      fetchConnectorStatus();
    } catch (error) {
      toast.error('Failed to connect');
    } finally {
      setConnecting(false);
    }
  };

  const handleSync = async (type) => {
    try {
      toast.info(`Syncing ${type} data...`);
      if (type === 'bank') await api.get('/sync/bank');
      else if (type === 'gst') await api.get('/sync/gst');
      else if (type === 'customs') await api.get('/sync/customs');
      toast.success(`${type} data synced`);
      fetchConnectorStatus();
    } catch (error) {
      toast.error(`Failed to sync ${type}`);
    }
  };

  const openConnectDialog = (type) => {
    setSelectedConnector(type);
    setFormData({});
    setConnectDialogOpen(true);
  };

  const getConnectorData = (type) => {
    if (type === 'bank') return bankStatus;
    if (type === 'gst') return gstStatus;
    if (type === 'customs') return customsStatus;
    return null;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <RefreshCw className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in" data-testid="connectors-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="font-heading text-4xl text-foreground">Connectors</h1>
          <p className="text-muted-foreground mt-1">Connect to external systems for automated data sync</p>
        </div>
        <Button variant="outline" onClick={fetchConnectorStatus} data-testid="refresh-connectors-btn">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh Status
        </Button>
      </div>

      {/* Connector Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {connectorTypes.map((connector) => {
          const Icon = connector.icon;
          const status = getConnectorData(connector.id);
          const isConnected = status?.status === 'synced' || status?.status === 'linked';
          
          return (
            <Card 
              key={connector.id} 
              className={`bg-card border-border ${isConnected ? 'border-l-4 border-l-neon' : ''}`}
              data-testid={`connector-${connector.id}`}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className={`w-12 h-12 rounded-md bg-${connector.color}/10 flex items-center justify-center`}>
                    <Icon className={`w-6 h-6 text-${connector.color}`} />
                  </div>
                  <Badge className={isConnected ? 'bg-neon/20 text-neon' : 'bg-muted text-muted-foreground'}>
                    {isConnected ? 'Connected' : 'Not Connected'}
                  </Badge>
                </div>
                <CardTitle className="font-heading text-lg mt-4">{connector.name}</CardTitle>
                <p className="text-sm text-muted-foreground">{connector.description}</p>
              </CardHeader>
              <CardContent>
                {isConnected ? (
                  <div className="space-y-4">
                    <div className="p-3 rounded-md bg-surface-highlight/50 border border-border">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
                        <Clock className="w-4 h-4" />
                        Last sync: {new Date(status.last_sync).toLocaleString()}
                      </div>
                      
                      {connector.id === 'bank' && status.accounts && (
                        <div className="space-y-2">
                          {status.accounts.map((acc, i) => (
                            <div key={i} className="flex items-center justify-between text-sm">
                              <span>{acc.bank} ({acc.account_number})</span>
                              <span className="font-mono text-neon">₹{acc.balance.toLocaleString()}</span>
                            </div>
                          ))}
                        </div>
                      )}
                      
                      {connector.id === 'gst' && status.data && (
                        <div className="space-y-2 text-sm">
                          <div className="flex items-center justify-between">
                            <span>GSTR-1 Filed</span>
                            <CheckCircle className="w-4 h-4 text-neon" />
                          </div>
                          <div className="flex items-center justify-between">
                            <span>GSTR-3B Filed</span>
                            <CheckCircle className="w-4 h-4 text-neon" />
                          </div>
                          <div className="flex items-center justify-between">
                            <span>ITC Balance</span>
                            <span className="font-mono text-neon">₹{status.data.input_credit_balance?.toLocaleString()}</span>
                          </div>
                        </div>
                      )}
                      
                      {connector.id === 'customs' && status.data && (
                        <div className="space-y-2 text-sm">
                          <div className="flex items-center justify-between">
                            <span>Shipping Bills</span>
                            <span className="font-mono">{status.data.shipping_bills}</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span>Pending Assessments</span>
                            <span className="font-mono text-amber">{status.data.pending_assessments}</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span>Duty Drawback Pending</span>
                            <span className="font-mono text-neon">₹{status.data.duty_drawback_pending?.toLocaleString()}</span>
                          </div>
                        </div>
                      )}
                    </div>
                    
                    <Button 
                      variant="outline" 
                      className="w-full" 
                      onClick={() => handleSync(connector.id)}
                      data-testid={`sync-${connector.id}-btn`}
                    >
                      <RefreshCw className="w-4 h-4 mr-2" />
                      Sync Now
                    </Button>
                  </div>
                ) : (
                  <Button 
                    className="w-full" 
                    onClick={() => openConnectDialog(connector.id)}
                    data-testid={`connect-${connector.id}-btn`}
                  >
                    <Link2 className="w-4 h-4 mr-2" />
                    Connect
                  </Button>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Connect Dialog */}
      <Dialog open={connectDialogOpen} onOpenChange={setConnectDialogOpen}>
        <DialogContent className="bg-card border-border max-w-md">
          <DialogHeader>
            <DialogTitle className="font-heading">
              Connect {connectorTypes.find(c => c.id === selectedConnector)?.name}
            </DialogTitle>
            <DialogDescription>
              Enter your credentials to connect
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleConnect} className="space-y-4">
            {selectedConnector === 'bank' && (
              <>
                <div className="space-y-2">
                  <Label>Account Aggregator ID</Label>
                  <Input
                    value={formData.aa_id || ''}
                    onChange={(e) => setFormData({ ...formData, aa_id: e.target.value })}
                    placeholder="Enter AA ID"
                    className="bg-background"
                    data-testid="bank-aa-id-input"
                  />
                </div>
                <div className="p-3 rounded-md bg-primary/5 border border-primary/20 text-sm">
                  <p className="text-muted-foreground">
                    You will be redirected to your bank to provide consent for data sharing.
                  </p>
                </div>
              </>
            )}
            
            {selectedConnector === 'gst' && (
              <div className="space-y-2">
                <Label>GSTIN</Label>
                <Input
                  value={formData.gstin || ''}
                  onChange={(e) => setFormData({ ...formData, gstin: e.target.value })}
                  placeholder="22AAAAA0000A1Z5"
                  className="bg-background"
                  data-testid="gst-gstin-input"
                />
              </div>
            )}
            
            {selectedConnector === 'customs' && (
              <div className="space-y-2">
                <Label>IEC Code</Label>
                <Input
                  value={formData.iec_code || ''}
                  onChange={(e) => setFormData({ ...formData, iec_code: e.target.value })}
                  placeholder="0123456789"
                  className="bg-background"
                  data-testid="customs-iec-input"
                />
              </div>
            )}
            
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setConnectDialogOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={connecting} data-testid="submit-connect-btn">
                {connecting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                Connect
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Info Card */}
      <Card className="bg-card border-border" data-testid="connector-info">
        <CardHeader>
          <CardTitle className="font-heading text-lg">About Connectors</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-md bg-surface-highlight/50 border border-border">
            <Landmark className="w-8 h-8 text-primary mb-3" />
            <h3 className="font-medium mb-1">Account Aggregator</h3>
            <p className="text-sm text-muted-foreground">
              Securely fetch bank statements and transactions for receivables reconciliation
            </p>
          </div>
          <div className="p-4 rounded-md bg-surface-highlight/50 border border-border">
            <Building2 className="w-8 h-8 text-neon mb-3" />
            <h3 className="font-medium mb-1">GST Portal</h3>
            <p className="text-sm text-muted-foreground">
              Auto-fetch GSTR data, input credit ledger, and refund application status
            </p>
          </div>
          <div className="p-4 rounded-md bg-surface-highlight/50 border border-border">
            <Package className="w-8 h-8 text-amber mb-3" />
            <h3 className="font-medium mb-1">ICEGATE</h3>
            <p className="text-sm text-muted-foreground">
              Get shipping bill status, duty drawback tracking, and customs notifications
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
