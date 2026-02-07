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
  Shield, Eye, Edit, Trash2, LogIn, LogOut, Key, RefreshCw,
  AlertTriangle, CheckCircle, XCircle, Clock, Search, Filter,
  Download, Lock, FileText, User, Package, CreditCard, Activity,
  Fingerprint, Globe, Monitor
} from 'lucide-react';
import { toast } from 'sonner';

const ACTION_ICONS = {
  view: Eye,
  edit: Edit,
  create: FileText,
  delete: Trash2,
  export: Download,
  login: LogIn,
  logout: LogOut,
  pii_unmask: Fingerprint,
  decrypt: Lock,
  password_change: Key,
  failed_login: XCircle,
  token_refresh: RefreshCw
};

const ACTION_COLORS = {
  view: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  edit: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  create: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  delete: 'bg-red-500/10 text-red-400 border-red-500/20',
  export: 'bg-violet-500/10 text-violet-400 border-violet-500/20',
  login: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  logout: 'bg-zinc-500/10 text-zinc-400 border-zinc-500/20',
  pii_unmask: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
  decrypt: 'bg-pink-500/10 text-pink-400 border-pink-500/20',
  password_change: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
  failed_login: 'bg-red-500/10 text-red-400 border-red-500/20',
  token_refresh: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20'
};

const RESOURCE_ICONS = {
  shipment: Package,
  payment: CreditCard,
  user: User,
  document: FileText,
  report: Download,
  connector: Globe,
  incentive: Activity
};

export default function AuditLogsPage() {
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState(null);
  const [piiLogs, setPiiLogs] = useState([]);
  const [securityLogs, setSecurityLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('all');
  
  // Filters
  const [actionFilter, setActionFilter] = useState('');
  const [resourceFilter, setResourceFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    try {
      const [logsRes, statsRes, piiRes, securityRes] = await Promise.all([
        api.get('/security/audit-logs?limit=100'),
        api.get('/security/stats'),
        api.get('/security/pii-access-logs?limit=50'),
        api.get('/security/security-events?limit=50')
      ]);
      
      setLogs(logsRes.data.logs || []);
      setStats(statsRes.data);
      setPiiLogs(piiRes.data.logs || []);
      setSecurityLogs(securityRes.data.logs || []);
    } catch (error) {
      console.error('Failed to fetch audit data:', error);
      toast.error('Failed to load audit logs');
    } finally {
      setLoading(false);
    }
  };

  const fetchFilteredLogs = async () => {
    setLoading(true);
    try {
      let url = '/security/audit-logs?limit=100';
      if (actionFilter) url += `&action=${actionFilter}`;
      if (resourceFilter) url += `&resource_type=${resourceFilter}`;
      
      const res = await api.get(url);
      setLogs(res.data.logs || []);
    } catch (error) {
      toast.error('Failed to apply filters');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const filteredLogs = logs.filter(log => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        log.user_id?.toLowerCase().includes(query) ||
        log.resource_id?.toLowerCase().includes(query) ||
        log.ip_address?.toLowerCase().includes(query)
      );
    }
    return true;
  });

  const StatCard = ({ icon: Icon, title, value, color }) => (
    <Card className={`bg-zinc-900/50 border-zinc-800 hover:border-${color}-500/30 transition-colors`}>
      <CardContent className="p-4">
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-lg bg-${color}-500/10 flex items-center justify-center`}>
            <Icon className={`w-5 h-5 text-${color}-400`} />
          </div>
          <div>
            <p className="text-xs text-zinc-500">{title}</p>
            <p className="text-xl font-bold text-white">{value}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const LogRow = ({ log }) => {
    const ActionIcon = ACTION_ICONS[log.action] || Activity;
    const ResourceIcon = RESOURCE_ICONS[log.resource_type] || FileText;
    
    return (
      <TableRow className="hover:bg-zinc-800/50 transition-colors">
        <TableCell className="w-[180px]">
          <div className="flex items-center gap-2 text-xs text-zinc-400">
            <Clock className="w-3 h-3" />
            {formatDate(log.timestamp)}
          </div>
        </TableCell>
        <TableCell>
          <Badge className={ACTION_COLORS[log.action] || 'bg-zinc-500/10'}>
            <ActionIcon className="w-3 h-3 mr-1" />
            {log.action}
          </Badge>
        </TableCell>
        <TableCell>
          <div className="flex items-center gap-2">
            <ResourceIcon className="w-4 h-4 text-zinc-400" />
            <span className="text-sm text-zinc-300">{log.resource_type}</span>
          </div>
        </TableCell>
        <TableCell>
          <span className="text-xs font-mono text-zinc-400 truncate max-w-[150px] block">
            {log.resource_id || '-'}
          </span>
        </TableCell>
        <TableCell>
          <div className="flex items-center gap-2">
            <User className="w-3 h-3 text-zinc-500" />
            <span className="text-xs font-mono text-zinc-400 truncate max-w-[100px]">
              {log.user_id?.slice(0, 8)}...
            </span>
          </div>
        </TableCell>
        <TableCell>
          {log.ip_address ? (
            <div className="flex items-center gap-1 text-xs text-zinc-500">
              <Globe className="w-3 h-3" />
              {log.ip_address}
            </div>
          ) : '-'}
        </TableCell>
        <TableCell>
          {log.success ? (
            <CheckCircle className="w-4 h-4 text-emerald-400" />
          ) : (
            <XCircle className="w-4 h-4 text-red-400" />
          )}
        </TableCell>
      </TableRow>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin text-violet-400 mx-auto mb-4" />
          <p className="text-zinc-400">Loading audit logs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in" data-testid="audit-logs-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-white via-zinc-200 to-zinc-400 bg-clip-text text-transparent flex items-center gap-3">
            <Shield className="w-10 h-10 text-emerald-400" />
            Security & Audit
          </h1>
          <p className="text-zinc-400 mt-1">
            Every action is logged. Tamper-proof. Immutable.
          </p>
        </div>
        <Button 
          onClick={fetchAllData} 
          variant="outline" 
          className="border-zinc-700 hover:bg-zinc-800"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Security Promise Banner */}
      <Card className="bg-gradient-to-r from-emerald-500/5 to-blue-500/5 border-emerald-500/20">
        <CardContent className="p-4">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center flex-shrink-0">
              <Lock className="w-6 h-6 text-emerald-400" />
            </div>
            <div>
              <h3 className="font-medium text-white mb-1">Zero-Knowledge Security</h3>
              <p className="text-sm text-zinc-400">
                All sensitive data is encrypted with AES-256. Even database administrators cannot read your financials.
                Every access attempt is logged with timestamp, user ID, and IP address. 
                Audit logs are <strong className="text-emerald-400">tamper-proof</strong> - they cannot be deleted or modified.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard 
          icon={Activity} 
          title="Total Actions" 
          value={stats?.total_entries || 0} 
          color="violet" 
        />
        <StatCard 
          icon={Eye} 
          title="View Actions" 
          value={stats?.by_action?.view || 0} 
          color="blue" 
        />
        <StatCard 
          icon={Fingerprint} 
          title="PII Unmask" 
          value={stats?.by_action?.pii_unmask || 0} 
          color="orange" 
        />
        <StatCard 
          icon={LogIn} 
          title="Login Events" 
          value={(stats?.by_action?.login || 0) + (stats?.by_action?.failed_login || 0)} 
          color="emerald" 
        />
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-zinc-800 pb-2">
        {[
          { id: 'all', label: 'All Activity', icon: Activity },
          { id: 'pii', label: 'PII Access', icon: Fingerprint },
          { id: 'security', label: 'Security Events', icon: Shield }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              activeTab === tab.id 
                ? 'bg-violet-500/10 text-violet-400 border border-violet-500/30' 
                : 'text-zinc-400 hover:text-zinc-300 hover:bg-zinc-800/50'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Filters - for All Activity tab */}
      {activeTab === 'all' && (
        <Card className="bg-zinc-900/50 border-zinc-800">
          <CardContent className="p-4">
            <div className="flex flex-wrap items-center gap-4">
              <div className="flex items-center gap-2">
                <Filter className="w-4 h-4 text-zinc-500" />
                <span className="text-sm text-zinc-400">Filters:</span>
              </div>
              
              <Select value={actionFilter} onValueChange={setActionFilter}>
                <SelectTrigger className="w-[150px] bg-zinc-800 border-zinc-700">
                  <SelectValue placeholder="Action Type" />
                </SelectTrigger>
                <SelectContent className="bg-zinc-800 border-zinc-700">
                  <SelectItem value="all">All Actions</SelectItem>
                  <SelectItem value="view">View</SelectItem>
                  <SelectItem value="edit">Edit</SelectItem>
                  <SelectItem value="create">Create</SelectItem>
                  <SelectItem value="delete">Delete</SelectItem>
                  <SelectItem value="export">Export</SelectItem>
                  <SelectItem value="pii_unmask">PII Unmask</SelectItem>
                  <SelectItem value="login">Login</SelectItem>
                  <SelectItem value="logout">Logout</SelectItem>
                </SelectContent>
              </Select>
              
              <Select value={resourceFilter} onValueChange={setResourceFilter}>
                <SelectTrigger className="w-[150px] bg-zinc-800 border-zinc-700">
                  <SelectValue placeholder="Resource Type" />
                </SelectTrigger>
                <SelectContent className="bg-zinc-800 border-zinc-700">
                  <SelectItem value="all">All Resources</SelectItem>
                  <SelectItem value="shipment">Shipment</SelectItem>
                  <SelectItem value="payment">Payment</SelectItem>
                  <SelectItem value="user">User</SelectItem>
                  <SelectItem value="document">Document</SelectItem>
                </SelectContent>
              </Select>
              
              <div className="flex-1 relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
                <Input
                  placeholder="Search by User ID, Resource ID, IP..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 bg-zinc-800 border-zinc-700"
                />
              </div>
              
              <Button onClick={fetchFilteredLogs} variant="outline" className="border-zinc-700">
                Apply
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Logs Table */}
      <Card className="bg-zinc-900/50 border-zinc-800">
        <CardHeader className="border-b border-zinc-800">
          <CardTitle className="text-lg text-white">
            {activeTab === 'all' && 'All Activity Logs'}
            {activeTab === 'pii' && 'PII Access Logs'}
            {activeTab === 'security' && 'Security Events'}
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="border-zinc-800 hover:bg-transparent">
                  <TableHead className="text-zinc-400">Timestamp</TableHead>
                  <TableHead className="text-zinc-400">Action</TableHead>
                  <TableHead className="text-zinc-400">Resource</TableHead>
                  <TableHead className="text-zinc-400">Resource ID</TableHead>
                  <TableHead className="text-zinc-400">User</TableHead>
                  <TableHead className="text-zinc-400">IP Address</TableHead>
                  <TableHead className="text-zinc-400">Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {activeTab === 'all' && filteredLogs.map((log, i) => (
                  <LogRow key={log.id || i} log={log} />
                ))}
                {activeTab === 'pii' && piiLogs.map((log, i) => (
                  <LogRow key={log.id || i} log={log} />
                ))}
                {activeTab === 'security' && securityLogs.map((log, i) => (
                  <LogRow key={log.id || i} log={log} />
                ))}
                {((activeTab === 'all' && filteredLogs.length === 0) ||
                  (activeTab === 'pii' && piiLogs.length === 0) ||
                  (activeTab === 'security' && securityLogs.length === 0)) && (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center py-12 text-zinc-500">
                      No audit logs found
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-zinc-900/50 border-zinc-800">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <Lock className="w-5 h-5 text-violet-400 mt-0.5" />
              <div>
                <h4 className="font-medium text-white text-sm">Field-Level Encryption</h4>
                <p className="text-xs text-zinc-500 mt-1">
                  Buyer names, invoice values, bank details encrypted with AES-256
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-zinc-900/50 border-zinc-800">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <Fingerprint className="w-5 h-5 text-orange-400 mt-0.5" />
              <div>
                <h4 className="font-medium text-white text-sm">On-Demand Decryption</h4>
                <p className="text-xs text-zinc-500 mt-1">
                  Data only unmasked when you explicitly click the View icon
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-zinc-900/50 border-zinc-800">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <Shield className="w-5 h-5 text-emerald-400 mt-0.5" />
              <div>
                <h4 className="font-medium text-white text-sm">Tamper-Proof Logs</h4>
                <p className="text-xs text-zinc-500 mt-1">
                  Hash chain ensures logs cannot be modified or deleted
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
