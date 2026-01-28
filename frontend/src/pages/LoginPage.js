import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Ship, TrendingUp, Shield, ArrowRight, Loader2, Eye, EyeOff } from 'lucide-react';
import { toast } from 'sonner';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email, password);
      toast.success('Welcome back!');
      navigate('/dashboard');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex" data-testid="login-page">
      {/* Left Panel - Branding */}
      <div 
        className="hidden lg:flex lg:w-1/2 relative bg-cover bg-center"
        style={{
          backgroundImage: `linear-gradient(to right, rgba(9,9,11,0.95), rgba(9,9,11,0.7)), url('https://images.unsplash.com/photo-1761307234324-0c9eadb951de?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NTYxODl8MHwxfHNlYXJjaHwxfHxzaGlwcGluZyUyMGNvbnRhaW5lciUyMHRlcm1pbmFsJTIwbmlnaHQlMjBhZXJpYWx8ZW58MHx8fHwxNzY5NjMyNDk2fDA&ixlib=rb-4.1.0&q=85')`
        }}
      >
        <div className="flex flex-col justify-between p-12">
          <div>
            <div className="flex items-center gap-3 mb-8">
              <div className="w-12 h-12 rounded-md bg-primary flex items-center justify-center">
                <Ship className="w-7 h-7 text-white" strokeWidth={1.5} />
              </div>
              <span className="font-heading text-3xl text-white tracking-tight">ExportFlow</span>
            </div>
            <h1 className="font-heading text-5xl text-white leading-tight mb-6">
              Export Finance<br />
              <span className="text-primary">Simplified</span>
            </h1>
            <p className="text-muted-foreground text-lg max-w-md">
              Manage shipments, track receivables, optimize incentives, and stay compliant — all in one platform.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-6">
            <div className="p-4 rounded-md bg-surface/50 border border-border">
              <TrendingUp className="w-8 h-8 text-neon mb-3" strokeWidth={1.5} />
              <h3 className="font-heading text-lg text-white mb-1">RoDTEP Optimizer</h3>
              <p className="text-sm text-muted-foreground">Never miss an export incentive</p>
            </div>
            <div className="p-4 rounded-md bg-surface/50 border border-border">
              <Shield className="w-8 h-8 text-amber mb-3" strokeWidth={1.5} />
              <h3 className="font-heading text-lg text-white mb-1">GST Compliance</h3>
              <p className="text-sm text-muted-foreground">Automate refund tracking</p>
            </div>
          </div>
        </div>
      </div>

      {/* Right Panel - Login Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-background">
        <div className="w-full max-w-md">
          {/* Mobile Logo */}
          <div className="lg:hidden flex items-center gap-3 mb-8 justify-center">
            <div className="w-10 h-10 rounded-md bg-primary flex items-center justify-center">
              <Ship className="w-6 h-6 text-white" strokeWidth={1.5} />
            </div>
            <span className="font-heading text-2xl text-white">ExportFlow</span>
          </div>

          <Card className="border-border bg-card/50 backdrop-blur-sm">
            <CardHeader className="space-y-1">
              <CardTitle className="font-heading text-2xl">Sign in</CardTitle>
              <CardDescription>Enter your credentials to access your dashboard</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="name@company.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    data-testid="login-email-input"
                    className="bg-background"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <div className="relative">
                    <Input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      placeholder="Enter your password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      data-testid="login-password-input"
                      className="bg-background pr-10"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>
                <Button 
                  type="submit" 
                  className="w-full mt-6 bg-primary hover:bg-primary/90"
                  disabled={loading}
                  data-testid="login-submit-btn"
                >
                  {loading ? (
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  ) : (
                    <ArrowRight className="w-4 h-4 mr-2" />
                  )}
                  Sign In
                </Button>
              </form>

              <div className="mt-6 text-center">
                <p className="text-sm text-muted-foreground">
                  Don't have an account?{' '}
                  <Link to="/register" className="text-primary hover:underline" data-testid="register-link">
                    Create account
                  </Link>
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
