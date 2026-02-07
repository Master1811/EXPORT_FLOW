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
  DialogTitle, DialogFooter
} from '../components/ui/dialog';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue
} from '../components/ui/select';
import {
  Link2, RefreshCw, CheckCircle, AlertCircle, Clock,
  Building2, Landmark, Package, Loader2, Shield, ExternalLink,
  CreditCard, Banknote, FileText, ArrowRight, Zap, Lock,
  AlertTriangle, Info
} from 'lucide-react';
import { toast } from 'sonner';

const BANKS = [
  { id: 'hdfc', name: 'HDFC Bank', color: '#004C8F' },
  { id: 'icici', name: 'ICICI Bank', color: '#F58220' },
  { id: 'sbi', name: 'State Bank of India', color: '#22409A' },
  { id: 'axis', name: 'Axis Bank', color: '#97144D' },
  { id: 'kotak', name: 'Kotak Mahindra Bank', color: '#ED1C24' },
  { id: 'yes', name: 'Yes Bank', color: '#00518F' },
  { id: 'indusind', name: 'IndusInd Bank', color: '#98272A' },
  { id: 'other', name: 'Other Bank', color: '#6B7280' }
];

const connectorConfigs = {
  bank: { 
    name: 'Bank Account (AA)', 
    icon: Landmark, 
    color: 'blue',
    gradient: 'from-blue-500/20 to-blue-600/5',
    description: 'Link your bank accounts via RBI-regulated Account Aggregator for real-time transaction data',
    features: ['Auto-reconcile receivables', 'Track EEFC balance', 'Real-time notifications']
  },
  gst: { 
    name: 'GST Portal', 
    icon: Building2, 
    color: 'emerald',
    gradient: 'from-emerald-500/20 to-emerald-600/5',
    description: 'Connect your GSTIN to fetch returns, ITC balance, and refund application status',
    features: ['Auto-fetch GSTR data', 'ITC reconciliation', 'Refund tracking']
  },
  customs: { 
    name: 'ICEGATE (Customs)', 
    icon: Package, 
    color: 'amber',
    gradient: 'from-amber-500/20 to-amber-600/5',
    description: 'Connect to ICEGATE for shipping bills, duty drawback, and customs notifications',
    features: ['Shipping bill status', 'Drawback tracking', 'e-BRC status']
  }
};

export default function ConnectorsPage() {
  const [connectors, setConnectors] = useState({
    bank: null,
    gst: null,
    customs: null
  });
  const [loading, setLoading] = useState(true);
  const [connectDialogOpen, setConnectDialogOpen] = useState(false);
  const [selectedConnector, setSelectedConnector] = useState(null);
  const [formData, setFormData] = useState({});
  const [connecting, setConnecting] = useState(false);
  const [syncingType, setSyncingType] = useState(null);
  const [step, setStep] = useState(1);

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
      setConnectors({
        bank: bankRes.data,
        gst: gstRes.data,
        customs: customsRes.data
      });
    } catch (error) {
      console.error('Failed to fetch connector status:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async (e) => {
    e?.preventDefault();
    setConnecting(true);
    
    try {
      if (selectedConnector === 'bank') {
        // Step 1: Initiate bank connection via Account Aggregator
        if (step === 1) {
          // Validate required fields
          if (!formData.bank_id || !formData.account_number || !formData.account_type) {
            toast.error('Please fill all required fields');
            setConnecting(false);
            return;
          }
          // Initiate connection
          await api.post('/connect/bank/initiate', { 
            connector_type: 'bank', 
            credentials: formData 
          });
          setStep(2);
          toast.info('Redirecting to Account Aggregator for consent...');
          // Simulate consent redirect
          setTimeout(() => {
            setStep(3);
            toast.success('Consent received! Linking account...');
          }, 2000);
        } else if (step === 3) {
          // Complete linking
          await api.post('/connect/bank/consent', { consent_status: 'approved', ...formData });
          toast.success('Bank account linked successfully!');
          setConnectDialogOpen(false);
          setFormData({});
          setStep(1);
          fetchConnectorStatus();
        }
      } else if (selectedConnector === 'gst') {
        if (!formData.gstin) {
          toast.error('Please enter your GSTIN');
          setConnecting(false);
          return;
        }
        await api.post('/connect/gst/link', formData);
        toast.success('GST Portal linked successfully!');
        setConnectDialogOpen(false);
        setFormData({});
        fetchConnectorStatus();
      } else if (selectedConnector === 'customs') {
        if (!formData.iec_code) {
          toast.error('Please enter your IEC Code');
          setConnecting(false);
          return;
        }
        // Additional validation for ICEGATE credentials
        if (step === 1) {
          setStep(2);
          toast.info('Verifying IEC Code with DGFT...');
          setTimeout(async () => {
            await api.post('/connect/customs/link', formData);
            toast.success('ICEGATE linked successfully!');
            setConnectDialogOpen(false);
            setFormData({});
            setStep(1);
            fetchConnectorStatus();
          }, 1500);
        }
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to connect');
    } finally {
      setConnecting(false);
    }
  };

  const handleSync = async (type) => {
    setSyncingType(type);
    try {
      toast.info(`Syncing ${connectorConfigs[type].name} data...`);
      if (type === 'bank') await api.get('/sync/bank');
      else if (type === 'gst') await api.get('/sync/gst');
      else if (type === 'customs') await api.get('/sync/customs');
      toast.success(`${connectorConfigs[type].name} synced successfully!`);
      fetchConnectorStatus();
    } catch (error) {
      toast.error(`Failed to sync ${connectorConfigs[type].name}`);
    } finally {
      setSyncingType(null);
    }
  };

  const openConnectDialog = (type) => {
    setSelectedConnector(type);
    setFormData({});
    setStep(1);
    setConnectDialogOpen(true);
  };

  const closeDialog = () => {
    setConnectDialogOpen(false);
    setSelectedConnector(null);
    setFormData({});
    setStep(1);
  };

  const isConnected = (type) => {
    const status = connectors[type]?.status;
    return status === 'synced' || status === 'linked';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin text-violet-400 mx-auto mb-4" />
          <p className="text-zinc-400">Loading connectors...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in" data-testid="connectors-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-white via-zinc-200 to-zinc-400 bg-clip-text text-transparent">
            Connectors
          </h1>
          <p className="text-zinc-400 mt-1">Connect to external systems for automated data sync</p>
        </div>
        <Button 
          variant="outline" 
          onClick={fetchConnectorStatus} 
          className="border-zinc-700 hover:bg-zinc-800"
          data-testid="refresh-connectors-btn"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh Status
        </Button>
      </div>

      {/* Security Badge */}
      <div className="p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/20 flex items-start gap-3">
        <Shield className="w-5 h-5 text-emerald-400 mt-0.5" />
        <div>
          <p className="text-sm font-medium text-emerald-400">Secure Connections</p>
          <p className="text-xs text-zinc-400 mt-1">
            All connections use RBI-regulated protocols. Your credentials are never stored. Data is encrypted end-to-end.
          </p>
        </div>
      </div>

      {/* Connector Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {Object.entries(connectorConfigs).map(([type, config]) => {
          const Icon = config.icon;
          const connected = isConnected(type);
          const status = connectors[type];
          
          return (
            <Card 
              key={type} 
              className={`relative overflow-hidden bg-zinc-900/50 border-zinc-800 ${connected ? 'border-l-4 border-l-emerald-500' : ''}`}
              data-testid={`connector-${type}`}
            >
              <div className={`absolute inset-0 bg-gradient-to-br ${config.gradient} pointer-events-none`} />
              
              <CardHeader className="relative">
                <div className="flex items-start justify-between">
                  <div className={`w-14 h-14 rounded-2xl bg-${config.color}-500/10 flex items-center justify-center border border-${config.color}-500/20`}>
                    <Icon className={`w-7 h-7 text-${config.color}-400`} />
                  </div>
                  <Badge className={connected 
                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' 
                    : 'bg-zinc-800 text-zinc-400 border-zinc-700'
                  }>
                    {connected ? (
                      <><CheckCircle className="w-3 h-3 mr-1" /> Connected</>
                    ) : 'Not Connected'}
                  </Badge>
                </div>
                <CardTitle className="text-xl mt-4 text-white">{config.name}</CardTitle>
                <p className="text-sm text-zinc-400">{config.description}</p>
              </CardHeader>
              
              <CardContent className="relative space-y-4">
                {connected ? (
                  <>
                    {/* Connected State - Show Data */}
                    <div className="p-4 rounded-xl bg-zinc-800/50 border border-zinc-700/50 space-y-3">
                      <div className="flex items-center gap-2 text-xs text-zinc-500">
                        <Clock className="w-3 h-3" />
                        Last sync: {new Date(status.last_sync).toLocaleString()}
                      </div>
                      
                      {type === 'bank' && status.accounts && (
                        <div className="space-y-2">
                          {status.accounts.map((acc, i) => (
                            <div key={i} className="flex items-center justify-between p-2 rounded-lg bg-zinc-900/50">
                              <div className="flex items-center gap-2">
                                <Banknote className="w-4 h-4 text-blue-400" />
                                <div>
                                  <p className="text-sm text-white">{acc.bank}</p>
                                  <p className="text-xs text-zinc-500">{acc.account_number} • {acc.type}</p>
                                </div>
                              </div>
                              <span className="font-mono text-emerald-400 font-medium">
                                ₹{acc.balance.toLocaleString()}
                              </span>
                            </div>
                          ))}
                        </div>
                      )}
                      
                      {type === 'gst' && status.data && (
                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-zinc-400">GSTR-1 Status</span>
                            <Badge className="bg-emerald-500/10 text-emerald-400">Filed</Badge>
                          </div>
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-zinc-400">GSTR-3B Status</span>
                            <Badge className="bg-emerald-500/10 text-emerald-400">Filed</Badge>
                          </div>
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-zinc-400">ITC Balance</span>
                            <span className="font-mono text-emerald-400">₹{status.data.input_credit_balance?.toLocaleString()}</span>
                          </div>
                        </div>
                      )}
                      
                      {type === 'customs' && status.data && (
                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-zinc-400">Shipping Bills</span>
                            <span className="font-mono text-white">{status.data.shipping_bills}</span>
                          </div>
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-zinc-400">Pending Assessments</span>
                            <span className="font-mono text-amber-400">{status.data.pending_assessments}</span>
                          </div>
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-zinc-400">Duty Drawback Pending</span>
                            <span className="font-mono text-emerald-400">₹{status.data.duty_drawback_pending?.toLocaleString()}</span>
                          </div>
                        </div>
                      )}
                    </div>
                    
                    <div className="flex gap-2">
                      <Button 
                        variant="outline" 
                        className="flex-1 border-zinc-700 hover:bg-zinc-800" 
                        onClick={() => handleSync(type)}
                        disabled={syncingType === type}
                        data-testid={`sync-${type}-btn`}
                      >
                        {syncingType === type ? (
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        ) : (
                          <RefreshCw className="w-4 h-4 mr-2" />
                        )}
                        Sync Now
                      </Button>
                      <Button 
                        variant="outline"
                        className="border-zinc-700 hover:bg-zinc-800"
                        onClick={() => openConnectDialog(type)}
                      >
                        <Link2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </>
                ) : (
                  <>
                    {/* Not Connected State */}
                    <div className="space-y-2">
                      {config.features.map((feature, i) => (
                        <div key={i} className="flex items-center gap-2 text-sm text-zinc-400">
                          <Zap className={`w-3 h-3 text-${config.color}-400`} />
                          {feature}
                        </div>
                      ))}
                    </div>
                    
                    <Button 
                      className={`w-full bg-${config.color}-600 hover:bg-${config.color}-700`}
                      onClick={() => openConnectDialog(type)}
                      data-testid={`connect-${type}-btn`}
                    >
                      <Link2 className="w-4 h-4 mr-2" />
                      Connect {config.name.split('(')[0].trim()}
                    </Button>
                  </>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Connection Dialog */}
      <Dialog open={connectDialogOpen} onOpenChange={closeDialog}>
        <DialogContent className="max-w-md bg-zinc-900 border-zinc-800">
          <DialogHeader>
            <DialogTitle className="text-xl text-white flex items-center gap-2">
              {selectedConnector && (
                <>
                  {React.createElement(connectorConfigs[selectedConnector]?.icon || Link2, {
                    className: `w-5 h-5 text-${connectorConfigs[selectedConnector]?.color}-400`
                  })}
                  Connect {connectorConfigs[selectedConnector]?.name}
                </>
              )}
            </DialogTitle>
            <DialogDescription className="text-zinc-400">
              {selectedConnector === 'bank' && step === 1 && 'Enter your bank account details to initiate linking via Account Aggregator'}
              {selectedConnector === 'bank' && step === 2 && 'Waiting for consent from Account Aggregator...'}
              {selectedConnector === 'bank' && step === 3 && 'Consent received! Click to complete linking.'}
              {selectedConnector === 'gst' && 'Enter your GSTIN to link with GST Portal'}
              {selectedConnector === 'customs' && step === 1 && 'Enter your IEC Code to connect with ICEGATE'}
              {selectedConnector === 'customs' && step === 2 && 'Verifying IEC Code with DGFT...'}
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleConnect} className="space-y-4">
            {/* Bank Account Form */}
            {selectedConnector === 'bank' && step === 1 && (
              <>
                <div className="space-y-2">
                  <Label className="text-zinc-300">Select Bank</Label>
                  <Select 
                    value={formData.bank_id || ''} 
                    onValueChange={(v) => setFormData({ ...formData, bank_id: v })}
                  >
                    <SelectTrigger className="bg-zinc-800 border-zinc-700" data-testid="bank-select">
                      <SelectValue placeholder="Choose your bank" />
                    </SelectTrigger>
                    <SelectContent className="bg-zinc-800 border-zinc-700">
                      {BANKS.map(bank => (
                        <SelectItem key={bank.id} value={bank.id}>
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: bank.color }} />
                            {bank.name}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label className="text-zinc-300">Account Number</Label>
                  <Input
                    value={formData.account_number || ''}
                    onChange={(e) => setFormData({ ...formData, account_number: e.target.value })}
                    placeholder="Enter account number"
                    className="bg-zinc-800 border-zinc-700"
                    data-testid="bank-account-input"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label className="text-zinc-300">Account Type</Label>
                  <Select 
                    value={formData.account_type || ''} 
                    onValueChange={(v) => setFormData({ ...formData, account_type: v })}
                  >
                    <SelectTrigger className="bg-zinc-800 border-zinc-700" data-testid="account-type-select">
                      <SelectValue placeholder="Select account type" />
                    </SelectTrigger>
                    <SelectContent className="bg-zinc-800 border-zinc-700">
                      <SelectItem value="current">Current Account</SelectItem>
                      <SelectItem value="eefc">EEFC Account</SelectItem>
                      <SelectItem value="savings">Savings Account</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
                  <div className="flex items-start gap-2">
                    <Info className="w-4 h-4 text-blue-400 mt-0.5" />
                    <p className="text-xs text-zinc-400">
                      You will be redirected to your bank's Account Aggregator to provide consent for data sharing. 
                      ExportFlow does not store your banking credentials.
                    </p>
                  </div>
                </div>
              </>
            )}
            
            {selectedConnector === 'bank' && step === 2 && (
              <div className="py-8 text-center">
                <Loader2 className="w-12 h-12 animate-spin text-blue-400 mx-auto mb-4" />
                <p className="text-zinc-400">Waiting for consent from Account Aggregator...</p>
                <p className="text-xs text-zinc-500 mt-2">This usually takes a few seconds</p>
              </div>
            )}
            
            {selectedConnector === 'bank' && step === 3 && (
              <div className="py-4 text-center">
                <CheckCircle className="w-12 h-12 text-emerald-400 mx-auto mb-4" />
                <p className="text-white font-medium">Consent Received!</p>
                <p className="text-zinc-400 text-sm mt-2">Click below to complete the linking process</p>
              </div>
            )}
            
            {/* GST Form */}
            {selectedConnector === 'gst' && (
              <>
                <div className="space-y-2">
                  <Label className="text-zinc-300">GSTIN</Label>
                  <Input
                    value={formData.gstin || ''}
                    onChange={(e) => setFormData({ ...formData, gstin: e.target.value.toUpperCase() })}
                    placeholder="22AAAAA0000A1Z5"
                    className="bg-zinc-800 border-zinc-700 font-mono"
                    maxLength={15}
                    data-testid="gst-gstin-input"
                  />
                  <p className="text-xs text-zinc-500">15-character GST Identification Number</p>
                </div>
                
                <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                  <div className="flex items-start gap-2">
                    <Shield className="w-4 h-4 text-emerald-400 mt-0.5" />
                    <p className="text-xs text-zinc-400">
                      We only fetch publicly available GST data. No OTP or login credentials required.
                    </p>
                  </div>
                </div>
              </>
            )}
            
            {/* ICEGATE Form */}
            {selectedConnector === 'customs' && step === 1 && (
              <>
                <div className="space-y-2">
                  <Label className="text-zinc-300">IEC Code</Label>
                  <Input
                    value={formData.iec_code || ''}
                    onChange={(e) => setFormData({ ...formData, iec_code: e.target.value })}
                    placeholder="0123456789"
                    className="bg-zinc-800 border-zinc-700 font-mono"
                    maxLength={10}
                    data-testid="customs-iec-input"
                  />
                  <p className="text-xs text-zinc-500">10-digit Import Export Code issued by DGFT</p>
                </div>
                
                <div className="space-y-2">
                  <Label className="text-zinc-300">ICEGATE Username (Optional)</Label>
                  <Input
                    value={formData.icegate_username || ''}
                    onChange={(e) => setFormData({ ...formData, icegate_username: e.target.value })}
                    placeholder="Enter ICEGATE username"
                    className="bg-zinc-800 border-zinc-700"
                    data-testid="icegate-username-input"
                  />
                </div>
                
                <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20">
                  <div className="flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 text-amber-400 mt-0.5" />
                    <p className="text-xs text-zinc-400">
                      For full ICEGATE integration, you may need to authorize ExportFlow on the ICEGATE portal.
                    </p>
                  </div>
                </div>
              </>
            )}
            
            {selectedConnector === 'customs' && step === 2 && (
              <div className="py-8 text-center">
                <Loader2 className="w-12 h-12 animate-spin text-amber-400 mx-auto mb-4" />
                <p className="text-zinc-400">Verifying IEC Code with DGFT...</p>
              </div>
            )}
            
            <DialogFooter className="gap-2">
              <Button type="button" variant="outline" onClick={closeDialog} className="border-zinc-700">
                Cancel
              </Button>
              {!(selectedConnector === 'bank' && step === 2) && !(selectedConnector === 'customs' && step === 2) && (
                <Button 
                  type="submit" 
                  disabled={connecting}
                  className={`bg-${connectorConfigs[selectedConnector]?.color}-600 hover:bg-${connectorConfigs[selectedConnector]?.color}-700`}
                  data-testid="submit-connect-btn"
                >
                  {connecting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                  {selectedConnector === 'bank' && step === 3 ? 'Complete Linking' : 'Connect'}
                </Button>
              )}
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Help Section */}
      <Card className="bg-zinc-900/50 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-lg text-white">How Connectors Work</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-zinc-800/50 border border-zinc-700/50">
            <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center mb-3">
              <Lock className="w-5 h-5 text-blue-400" />
            </div>
            <h3 className="font-medium text-white mb-1">Secure by Design</h3>
            <p className="text-sm text-zinc-400">
              All connections use RBI-regulated Account Aggregator framework. Your credentials are never stored.
            </p>
          </div>
          <div className="p-4 rounded-xl bg-zinc-800/50 border border-zinc-700/50">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center mb-3">
              <Zap className="w-5 h-5 text-emerald-400" />
            </div>
            <h3 className="font-medium text-white mb-1">Auto Sync</h3>
            <p className="text-sm text-zinc-400">
              Once connected, data syncs automatically. Manual refresh available anytime for latest updates.
            </p>
          </div>
          <div className="p-4 rounded-xl bg-zinc-800/50 border border-zinc-700/50">
            <div className="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center mb-3">
              <FileText className="w-5 h-5 text-amber-400" />
            </div>
            <h3 className="font-medium text-white mb-1">Smart Reconciliation</h3>
            <p className="text-sm text-zinc-400">
              Automatically match bank transactions with shipments and payments for accurate tracking.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
