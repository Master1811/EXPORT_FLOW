import React, { useState, useRef, useEffect } from 'react';
import { api } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { ScrollArea } from '../components/ui/scroll-area';
import {
  Brain, Send, Loader2, Sparkles, RefreshCw, TrendingUp,
  AlertTriangle, Calculator, MessageSquare, Bot, User
} from 'lucide-react';
import { toast } from 'sonner';

export default function AIPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [forecasts, setForecasts] = useState(null);
  const [riskAlerts, setRiskAlerts] = useState([]);
  const [optimizer, setOptimizer] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchAIData();
    // Add welcome message
    setMessages([{
      role: 'assistant',
      content: "Hello! I'm your AI Export Finance Assistant. I can help you with GST regulations, RoDTEP/RoSCTL incentives, forex management, customs procedures, and trade documentation. How can I assist you today?"
    }]);
  }, []);

  const fetchAIData = async () => {
    try {
      const [refundRes, cashflowRes, alertsRes, optimizerRes] = await Promise.all([
        api.get('/ai/refund-forecast'),
        api.get('/ai/cashflow-forecast'),
        api.get('/ai/risk-alerts'),
        api.get('/ai/incentive-optimizer')
      ]);
      setForecasts({
        refund: refundRes.data,
        cashflow: cashflowRes.data
      });
      setRiskAlerts(alertsRes.data.alerts);
      setOptimizer(optimizerRes.data);
    } catch (error) {
      console.error('Failed to fetch AI data:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await api.post('/ai/query', { query: input });
      const assistantMessage = { role: 'assistant', content: response.data.response };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      toast.error('Failed to get AI response');
      const errorMessage = { 
        role: 'assistant', 
        content: "I apologize, but I'm having trouble processing your request. Please try again later."
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const quickQuestions = [
    "What is RoDTEP and how do I claim it?",
    "How to calculate GST refund for exports?",
    "What documents are needed for zero-rated exports?",
    "Explain LUT requirements for exporters"
  ];

  const handleQuickQuestion = (question) => {
    setInput(question);
  };

  const formatCurrency = (value) => {
    if (value >= 100000) return `₹${(value / 100000).toFixed(2)}L`;
    return `₹${value?.toLocaleString('en-IN') || 0}`;
  };

  return (
    <div className="space-y-6 animate-fade-in" data-testid="ai-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="font-heading text-4xl text-foreground">AI Assistant</h1>
          <p className="text-muted-foreground mt-1">Get AI-powered insights and answers</p>
        </div>
        <Button variant="outline" onClick={fetchAIData} data-testid="refresh-ai-btn">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh Insights
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chat Interface */}
        <Card className="lg:col-span-2 bg-card border-border flex flex-col h-[600px]" data-testid="ai-chat">
          <CardHeader className="border-b border-border flex-shrink-0">
            <CardTitle className="font-heading text-lg flex items-center gap-2">
              <Brain className="w-5 h-5 text-primary" />
              Export Finance AI
              <span className="text-xs text-neon bg-neon/10 px-2 py-1 rounded-full ml-2">Powered by Gemini</span>
            </CardTitle>
          </CardHeader>
          
          {/* Messages */}
          <ScrollArea className="flex-1 p-4">
            <div className="space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  data-testid={`message-${index}`}
                >
                  {message.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-md bg-primary/20 flex items-center justify-center flex-shrink-0">
                      <Bot className="w-4 h-4 text-primary" />
                    </div>
                  )}
                  <div
                    className={`max-w-[80%] p-3 rounded-md ${
                      message.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-surface-highlight border border-border'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  </div>
                  {message.role === 'user' && (
                    <div className="w-8 h-8 rounded-md bg-neon/20 flex items-center justify-center flex-shrink-0">
                      <User className="w-4 h-4 text-neon" />
                    </div>
                  )}
                </div>
              ))}
              {loading && (
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-md bg-primary/20 flex items-center justify-center">
                    <Bot className="w-4 h-4 text-primary" />
                  </div>
                  <div className="bg-surface-highlight border border-border p-3 rounded-md">
                    <Loader2 className="w-4 h-4 animate-spin text-primary" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>

          {/* Quick Questions */}
          <div className="px-4 py-2 border-t border-border flex-shrink-0">
            <p className="text-xs text-muted-foreground mb-2">Quick questions:</p>
            <div className="flex flex-wrap gap-2">
              {quickQuestions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickQuestion(question)}
                  className="text-xs px-3 py-1.5 rounded-full bg-surface-highlight border border-border hover:border-primary/50 transition-colors"
                  data-testid={`quick-question-${index}`}
                >
                  {question}
                </button>
              ))}
            </div>
          </div>

          {/* Input */}
          <form onSubmit={handleSubmit} className="p-4 border-t border-border flex-shrink-0">
            <div className="flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about exports, GST, incentives..."
                className="bg-background"
                disabled={loading}
                data-testid="ai-input"
              />
              <Button type="submit" disabled={loading || !input.trim()} data-testid="ai-submit-btn">
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </Button>
            </div>
          </form>
        </Card>

        {/* AI Insights Sidebar */}
        <div className="space-y-4">
          {/* Refund Forecast */}
          <Card className="bg-card border-border" data-testid="refund-forecast-card">
            <CardHeader className="pb-3">
              <CardTitle className="font-heading text-sm flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-neon" />
                Refund Forecast
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {forecasts?.refund?.forecast?.map((item, index) => (
                <div key={index} className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">{item.month}</span>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-neon">{formatCurrency(item.expected_refund)}</span>
                    <span className="text-xs text-muted-foreground">({Math.round(item.confidence * 100)}%)</span>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Optimizer Recommendations */}
          <Card className="bg-card border-border" data-testid="optimizer-card">
            <CardHeader className="pb-3">
              <CardTitle className="font-heading text-sm flex items-center gap-2">
                <Calculator className="w-4 h-4 text-primary" />
                Incentive Optimizer
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {optimizer?.recommendations?.map((rec, index) => (
                <div 
                  key={index} 
                  className="p-3 rounded-md bg-surface-highlight/50 border border-border"
                  data-testid={`optimizer-rec-${index}`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium">{rec.action}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      rec.priority === 'high' ? 'bg-destructive/20 text-destructive' : 'bg-amber/20 text-amber'
                    }`}>
                      {rec.priority}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>{rec.shipments_affected} shipments</span>
                    <span className="text-neon font-mono">{formatCurrency(rec.potential_benefit)}</span>
                  </div>
                </div>
              ))}
              <div className="pt-2 border-t border-border">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Total Opportunity</span>
                  <span className="font-mono text-neon font-bold">{formatCurrency(optimizer?.total_opportunity)}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Risk Alerts */}
          <Card className="bg-card border-border" data-testid="risk-alerts-sidebar">
            <CardHeader className="pb-3">
              <CardTitle className="font-heading text-sm flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber" />
                Risk Alerts
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {riskAlerts.slice(0, 3).map((alert, index) => (
                <div 
                  key={index}
                  className={`p-2 rounded-md text-xs border ${
                    alert.severity === 'high' 
                      ? 'bg-destructive/5 border-destructive/20' 
                      : alert.severity === 'medium'
                      ? 'bg-amber/5 border-amber/20'
                      : 'bg-primary/5 border-primary/20'
                  }`}
                  data-testid={`risk-alert-${index}`}
                >
                  <p className={`font-medium ${
                    alert.severity === 'high' ? 'text-destructive' : 
                    alert.severity === 'medium' ? 'text-amber' : 'text-primary'
                  }`}>
                    {alert.message}
                  </p>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Cashflow Forecast */}
          <Card className="bg-card border-border" data-testid="cashflow-card">
            <CardHeader className="pb-3">
              <CardTitle className="font-heading text-sm flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-primary" />
                Cashflow Forecast
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {forecasts?.cashflow?.forecast?.map((item, index) => (
                <div key={index} className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">{item.month}</span>
                  <span className={`font-mono ${item.net >= 0 ? 'text-neon' : 'text-destructive'}`}>
                    {item.net >= 0 ? '+' : ''}{formatCurrency(item.net)}
                  </span>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
