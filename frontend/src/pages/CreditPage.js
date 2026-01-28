import React, { useState, useEffect } from 'react';
import { api } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow
} from '../components/ui/table';
import {
  Users, TrendingUp, TrendingDown, AlertTriangle, CheckCircle,
  RefreshCw, Search, Shield, DollarSign, Clock
} from 'lucide-react';
import { toast } from 'sonner';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer
} from 'recharts';

export default function CreditPage() {
  const [companyScore, setCompanyScore] = useState(null);
  const [paymentBehavior, setPaymentBehavior] = useState(null);
  const [buyerScore, setBuyerScore] = useState(null);
  const [searchBuyer, setSearchBuyer] = useState('');
  const [loading, setLoading] = useState(true);
  const [searchLoading, setSearchLoading] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [scoreRes, behaviorRes] = await Promise.all([
        api.get('/credit/company-score'),
        api.get('/credit/payment-behavior')
      ]);
      setCompanyScore(scoreRes.data);
      setPaymentBehavior(behaviorRes.data);
    } catch (error) {
      console.error('Failed to fetch credit data:', error);
    } finally {
      setLoading(false);
    }
  };

  const searchBuyerScore = async () => {
    if (!searchBuyer.trim()) return;
    setSearchLoading(true);
    try {
      const response = await api.get(`/credit/buyer-score/${searchBuyer}`);
      setBuyerScore(response.data);
    } catch (error) {
      toast.error('Failed to fetch buyer score');
    } finally {
      setSearchLoading(false);
    }
  };

  const formatCurrency = (value) => {
    if (value >= 100000) return `₹${(value / 100000).toFixed(2)}L`;
    return `₹${value?.toLocaleString('en-IN') || 0}`;
  };

  const getScoreColor = (score) => {
    if (score >= 700) return 'text-neon';
    if (score >= 500) return 'text-amber';
    return 'text-destructive';
  };

  const getRiskBadgeColor = (risk) => {
    if (risk === 'low') return 'bg-neon/20 text-neon';
    if (risk === 'medium') return 'bg-amber/20 text-amber';
    return 'bg-destructive/20 text-destructive';
  };

  const regionData = paymentBehavior?.by_region ? Object.entries(paymentBehavior.by_region).map(([region, data]) => ({
    region,
    days: data.avg_days,
    onTime: data.on_time
  })) : [];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <RefreshCw className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in" data-testid="credit-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="font-heading text-4xl text-foreground">Credit Intelligence</h1>
          <p className="text-muted-foreground mt-1">Analyze credit scores and payment behavior</p>
        </div>
        <Button variant="outline" onClick={fetchData} data-testid="refresh-credit-btn">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Company Score Card */}
      <Card className="bg-card border-border" data-testid="company-score-card">
        <CardHeader>
          <CardTitle className="font-heading text-lg flex items-center gap-2">
            <Shield className="w-5 h-5 text-primary" />
            Your Company Credit Profile
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
            {/* Score Circle */}
            <div className="flex flex-col items-center justify-center">
              <div className="relative w-32 h-32">
                <svg className="w-32 h-32 -rotate-90">
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke="#27272A"
                    strokeWidth="12"
                    fill="none"
                  />
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke="#3B82F6"
                    strokeWidth="12"
                    fill="none"
                    strokeDasharray={`${(companyScore?.company_score / 850) * 352} 352`}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center flex-col">
                  <span className={`text-3xl font-heading font-bold ${getScoreColor(companyScore?.company_score)}`}>
                    {companyScore?.company_score}
                  </span>
                  <span className="text-xs text-muted-foreground">/ 850</span>
                </div>
              </div>
              <p className="text-sm text-muted-foreground mt-2">Credit Score</p>
            </div>

            {/* Score Factors */}
            <div className="md:col-span-4 grid grid-cols-2 md:grid-cols-4 gap-4">
              {companyScore?.factors && Object.entries(companyScore.factors).map(([key, data]) => (
                <div key={key} className="p-4 rounded-md bg-surface-highlight/50 border border-border">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-muted-foreground capitalize">
                      {key.replace('_', ' ')}
                    </span>
                    {data.trend === 'up' ? (
                      <TrendingUp className="w-4 h-4 text-neon" />
                    ) : data.trend === 'down' ? (
                      <TrendingDown className="w-4 h-4 text-destructive" />
                    ) : (
                      <div className="w-4 h-4" />
                    )}
                  </div>
                  <Progress value={data.score} className="h-2 mb-1" />
                  <span className="text-lg font-bold">{data.score}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Credit Limit */}
          <div className="mt-6 p-4 rounded-md bg-primary/5 border border-primary/20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Eligible Credit Limit</p>
                <p className="text-2xl font-heading font-bold text-primary">
                  {formatCurrency(companyScore?.credit_limit_eligible)}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-muted-foreground">Recommendations</p>
                <div className="flex flex-wrap gap-2 mt-1 justify-end">
                  {companyScore?.recommendations?.map((rec, i) => (
                    <Badge key={i} variant="outline" className="text-xs">{rec}</Badge>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Buyer Score Search and Payment Behavior */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Buyer Score Search */}
        <Card className="bg-card border-border" data-testid="buyer-search-card">
          <CardHeader>
            <CardTitle className="font-heading text-lg flex items-center gap-2">
              <Users className="w-5 h-5 text-primary" />
              Buyer Credit Check
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <Input
                value={searchBuyer}
                onChange={(e) => setSearchBuyer(e.target.value)}
                placeholder="Enter buyer ID or name"
                className="bg-background"
                data-testid="buyer-search-input"
              />
              <Button onClick={searchBuyerScore} disabled={searchLoading} data-testid="buyer-search-btn">
                {searchLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
              </Button>
            </div>

            {buyerScore && (
              <div className="p-4 rounded-md bg-surface-highlight/50 border border-border" data-testid="buyer-score-result">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <p className="font-medium">{buyerScore.buyer_name}</p>
                    <p className="text-xs text-muted-foreground">ID: {buyerScore.buyer_id}</p>
                  </div>
                  <Badge className={getRiskBadgeColor(buyerScore.risk_level)}>
                    {buyerScore.risk_level} risk
                  </Badge>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Credit Score</p>
                    <p className={`text-2xl font-heading font-bold ${getScoreColor(buyerScore.credit_score)}`}>
                      {buyerScore.credit_score}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Payment History</p>
                    <p className="text-sm">
                      <span className="text-neon">{buyerScore.payment_history.on_time}</span> on-time / 
                      <span className="text-destructive ml-1">{buyerScore.payment_history.delayed}</span> delayed
                    </p>
                  </div>
                </div>

                <div className="p-3 rounded-md bg-background border border-border">
                  <p className="text-sm font-medium mb-1">Recommendation</p>
                  <p className="text-sm text-muted-foreground">{buyerScore.recommendation}</p>
                </div>
              </div>
            )}

            {!buyerScore && (
              <div className="text-center py-8">
                <Users className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">Search for a buyer to view their credit profile</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Payment Behavior */}
        <Card className="bg-card border-border" data-testid="payment-behavior-card">
          <CardHeader>
            <CardTitle className="font-heading text-lg flex items-center gap-2">
              <Clock className="w-5 h-5 text-neon" />
              Payment Behavior Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="p-4 rounded-md bg-surface-highlight/50 border border-border text-center">
                <p className="text-2xl font-heading font-bold text-primary">
                  {paymentBehavior?.average_collection_days}
                </p>
                <p className="text-xs text-muted-foreground">Avg Collection Days</p>
              </div>
              <div className="p-4 rounded-md bg-surface-highlight/50 border border-border text-center">
                <p className="text-2xl font-heading font-bold text-neon">
                  {paymentBehavior?.on_time_percentage}%
                </p>
                <p className="text-xs text-muted-foreground">On-Time %</p>
              </div>
              <div className="p-4 rounded-md bg-surface-highlight/50 border border-border text-center">
                <div className="flex items-center justify-center gap-1">
                  {paymentBehavior?.trend === 'improving' ? (
                    <TrendingUp className="w-5 h-5 text-neon" />
                  ) : (
                    <TrendingDown className="w-5 h-5 text-destructive" />
                  )}
                  <span className={`text-sm font-medium ${
                    paymentBehavior?.trend === 'improving' ? 'text-neon' : 'text-destructive'
                  }`}>
                    {paymentBehavior?.trend}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground">Trend</p>
              </div>
            </div>

            {/* Region Chart */}
            <div className="h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={regionData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                  <XAxis dataKey="region" stroke="#71717A" fontSize={12} />
                  <YAxis stroke="#71717A" fontSize={12} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#18181B',
                      border: '1px solid #27272A',
                      borderRadius: '6px'
                    }}
                  />
                  <Bar dataKey="days" name="Avg Days" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Region Breakdown Table */}
      <Card className="bg-card border-border" data-testid="region-breakdown">
        <CardHeader>
          <CardTitle className="font-heading text-lg">Payment Behavior by Region</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow className="border-border hover:bg-transparent">
                <TableHead className="text-muted-foreground">Region</TableHead>
                <TableHead className="text-muted-foreground">Avg Collection Days</TableHead>
                <TableHead className="text-muted-foreground">On-Time %</TableHead>
                <TableHead className="text-muted-foreground">Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {paymentBehavior?.by_region && Object.entries(paymentBehavior.by_region).map(([region, data]) => (
                <TableRow key={region} className="border-border hover:bg-surface-highlight/50">
                  <TableCell className="font-medium">{region}</TableCell>
                  <TableCell className="font-mono">{data.avg_days} days</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Progress value={data.on_time} className="w-20 h-2" />
                      <span className="text-sm">{data.on_time}%</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge className={data.on_time >= 75 ? 'bg-neon/20 text-neon' : 'bg-amber/20 text-amber'}>
                      {data.on_time >= 75 ? 'Good' : 'Monitor'}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
