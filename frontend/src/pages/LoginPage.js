import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Ship, TrendingUp, Shield, ArrowRight, Loader2, Eye, EyeOff, IndianRupee, BarChart3, ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';

// Animation variants
const fadeInUp = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.25, 0.1, 0.25, 1] } }
};

const fadeInLeft = {
  hidden: { opacity: 0, x: -30 },
  visible: { opacity: 1, x: 0, transition: { duration: 0.8, ease: [0.25, 0.1, 0.25, 1] } }
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: { 
    opacity: 1, 
    transition: { 
      staggerChildren: 0.1,
      delayChildren: 0.2 
    } 
  }
};

// Error Boundary Component
class LoginErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Login Page Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center p-4 bg-[#09090B]">
          <div className="text-center">
            <h2 className="text-xl font-semibold text-white mb-2">Something went wrong</h2>
            <p className="text-zinc-400 mb-4">Please refresh the page and try again.</p>
            <Button onClick={() => window.location.reload()}>Refresh Page</Button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

// Skip Link Component
const SkipLink = () => (
  <a 
    href="#login-form" 
    className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-[100] focus:px-4 focus:py-2 focus:bg-violet-600 focus:text-white focus:rounded-lg"
  >
    Skip to login form
  </a>
);

// Feature Card Component
const FeatureCard = ({ icon: Icon, title, description, gradient }) => (
  <motion.div 
    variants={fadeInUp}
    whileHover={{ scale: 1.02, y: -4 }}
    transition={{ type: 'spring', stiffness: 300 }}
    className="p-6 rounded-xl bg-zinc-900/50 border border-zinc-800 hover:border-zinc-700 transition-all duration-300"
  >
    <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${gradient} flex items-center justify-center mb-4`} aria-hidden="true">
      <Icon className="w-6 h-6 text-white" strokeWidth={1.5} aria-hidden="true" />
    </div>
    <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
    <p className="text-sm text-zinc-400 leading-relaxed">{description}</p>
  </motion.div>
);

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  // Set document title and meta tags
  useEffect(() => {
    document.title = 'Sign In - ExportFlow';
    
    const updateMetaTag = (name, content) => {
      let element = document.querySelector(`meta[name="${name}"]`);
      if (!element) {
        element = document.createElement('meta');
        element.setAttribute('name', name);
        document.head.appendChild(element);
      }
      element.setAttribute('content', content);
    };

    updateMetaTag('description', 'Sign in to ExportFlow to manage your export business efficiently.');
    updateMetaTag('robots', 'noindex, nofollow'); // Auth pages shouldn't be indexed
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await login(email, password);
      toast.success('Welcome back!');
      navigate('/dashboard');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Login failed. Please check your credentials.');
      console.error('Login error:', error);
    } finally {
      setLoading(false);
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && e.target.type === 'button') {
      e.preventDefault();
      togglePasswordVisibility();
    }
  };

  return (
    <LoginErrorBoundary>
      <SkipLink />
      
      <div className="min-h-screen flex bg-[#09090B]" data-testid="login-page">
        {/* Left Panel - Branding & Features */}
        <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
          {/* Background Image with Overlay */}
          <div 
            className="absolute inset-0 bg-cover bg-center"
            style={{
              backgroundImage: `linear-gradient(to right, rgba(9,9,11,0.95), rgba(9,9,11,0.85)), url('https://images.unsplash.com/photo-1761307234324-0c9eadb951de?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NTYxODl8MHwxfHNlYXJjaHwxfHxzaGlwcGluZyUyMGNvbnRhaW5lciUyMHRlcm1pbmFsJTIwbmlnaHQlMjBhZXJpYWx8ZW58MHx8fHwxNzY5NjMyNDk2fDA&ixlib=rb-4.1.0&q=85')`
            }}
            role="img"
            aria-label="Shipping container terminal at night"
          />
          
          {/* Gradient Orbs */}
          <div className="absolute top-1/3 left-1/3 w-[400px] h-[400px] bg-violet-600/20 rounded-full blur-orb" aria-hidden="true" />
          <div className="absolute bottom-1/3 right-1/3 w-[300px] h-[300px] bg-blue-600/10 rounded-full blur-orb" style={{ animationDelay: '1.5s' }} aria-hidden="true" />
          
          <motion.div 
            className="relative z-10 flex flex-col justify-between p-12"
            initial="hidden"
            animate="visible"
            variants={staggerContainer}
          >
            <div>
              {/* Logo - Clickable to landing page */}
              <motion.div variants={fadeInLeft} className="flex items-center gap-3 mb-12">
                <Link to="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-500 rounded-xl">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-600 to-violet-800 flex items-center justify-center" aria-hidden="true">
                    <Ship className="w-7 h-7 text-white" strokeWidth={1.5} aria-hidden="true" />
                  </div>
                  <span className="text-3xl font-bold tracking-tight text-white">
                    Export<span className="text-violet-400">Flow</span>
                  </span>
                </Link>
              </motion.div>
              
              {/* Headline */}
              <motion.div variants={fadeInLeft}>
                <h1 className="text-5xl font-bold text-white leading-tight mb-6">
                  Export Finance<br />
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-fuchsia-400">
                    Simplified
                  </span>
                </h1>
                <p className="text-zinc-300 text-lg max-w-md leading-relaxed">
                  Manage shipments, track receivables, optimize incentives, and stay compliant — all in one platform built for Indian exporters.
                </p>
              </motion.div>
            </div>

            {/* Feature Cards */}
            <div className="grid grid-cols-2 gap-4">
              <FeatureCard
                icon={TrendingUp}
                title="RoDTEP Optimizer"
                description="Never miss an export incentive opportunity"
                gradient="from-emerald-500 to-teal-500"
              />
              <FeatureCard
                icon={Shield}
                title="GST Compliance"
                description="Automate refund tracking and filing"
                gradient="from-amber-500 to-orange-500"
              />
              <FeatureCard
                icon={IndianRupee}
                title="Cash Flow Insights"
                description="Real-time receivables aging dashboard"
                gradient="from-blue-500 to-cyan-500"
              />
              <FeatureCard
                icon={BarChart3}
                title="Analytics & Reports"
                description="Make data-driven export decisions"
                gradient="from-violet-500 to-purple-500"
              />
            </div>
          </motion.div>
        </div>

        {/* Right Panel - Login Form */}
        <div className="flex-1 flex items-center justify-center p-4 sm:p-8 relative overflow-hidden">
          {/* Gradient Orbs for Mobile */}
          <div className="lg:hidden absolute top-1/4 right-1/4 w-[300px] h-[300px] bg-violet-600/20 rounded-full blur-orb" aria-hidden="true" />
          <div className="lg:hidden absolute bottom-1/4 left-1/4 w-[200px] h-[200px] bg-blue-600/10 rounded-full blur-orb" style={{ animationDelay: '1s' }} aria-hidden="true" />
          
          <motion.div 
            className="w-full max-w-md relative z-10"
            initial="hidden"
            animate="visible"
            variants={staggerContainer}
          >
            {/* Back to Home Link */}
            <motion.div variants={fadeInUp} className="mb-4">
              <Link 
                to="/" 
                className="inline-flex items-center gap-2 text-sm text-zinc-400 hover:text-white transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-500 rounded"
              >
                <ArrowLeft className="w-4 h-4" />
                Back to Home
              </Link>
            </motion.div>

            {/* Mobile Logo - Clickable */}
            <motion.div 
              variants={fadeInUp}
              className="lg:hidden flex items-center gap-3 mb-8 justify-center"
            >
              <Link to="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-600 to-violet-800 flex items-center justify-center" aria-hidden="true">
                  <Ship className="w-6 h-6 text-white" strokeWidth={1.5} aria-hidden="true" />
                </div>
                <span className="text-2xl font-bold tracking-tight text-white">
                  Export<span className="text-violet-400">Flow</span>
                </span>
              </Link>
            </motion.div>

            {/* Login Card */}
            <motion.div variants={fadeInUp}>
              <Card className="border-zinc-800 bg-zinc-900/50 backdrop-blur-sm shadow-2xl shadow-violet-500/10">
                <CardHeader className="space-y-2 pb-6">
                  <CardTitle className="text-2xl sm:text-3xl font-bold text-white">
                    Welcome Back
                  </CardTitle>
                  <CardDescription className="text-zinc-400 text-base">
                    Sign in to access your export dashboard
                  </CardDescription>
                </CardHeader>
                
                <CardContent>
                  <form 
                    id="login-form"
                    onSubmit={handleSubmit} 
                    className="space-y-4"
                    noValidate
                    aria-label="Login form"
                  >
                    {/* Email Field */}
                    <motion.div variants={fadeInUp} className="space-y-2">
                      <Label 
                        htmlFor="email" 
                        className="text-zinc-200 font-medium"
                      >
                        Email <span className="text-red-400" aria-label="required">*</span>
                      </Label>
                      <Input
                        id="email"
                        type="email"
                        placeholder="name@company.com"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        autoComplete="email"
                        aria-required="true"
                        aria-invalid={email.length > 0 && !email.includes('@') ? "true" : "false"}
                        data-testid="login-email-input"
                        className="bg-zinc-800/50 border-zinc-700 text-white placeholder:text-zinc-500 focus:border-violet-500 focus:ring-violet-500/20 transition-all"
                      />
                    </motion.div>

                    {/* Password Field */}
                    <motion.div variants={fadeInUp} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <Label 
                          htmlFor="password" 
                          className="text-zinc-200 font-medium"
                        >
                          Password <span className="text-red-400" aria-label="required">*</span>
                        </Label>
                        <Link 
                          to="/forgot-password" 
                          className="text-sm text-violet-400 hover:text-violet-300 transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-500 rounded"
                          tabIndex={0}
                        >
                          Forgot password?
                        </Link>
                      </div>
                      <div className="relative">
                        <Input
                          id="password"
                          type={showPassword ? 'text' : 'password'}
                          placeholder="Enter your password"
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                          required
                          autoComplete="current-password"
                          aria-required="true"
                          aria-invalid={password.length > 0 && password.length < 6 ? "true" : "false"}
                          data-testid="login-password-input"
                          className="bg-zinc-800/50 border-zinc-700 text-white placeholder:text-zinc-500 focus:border-violet-500 focus:ring-violet-500/20 transition-all pr-10"
                        />
                        <button
                          type="button"
                          onClick={togglePasswordVisibility}
                          onKeyDown={handleKeyDown}
                          aria-label={showPassword ? 'Hide password' : 'Show password'}
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-white transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-500 rounded"
                        >
                          {showPassword ? (
                            <EyeOff className="w-4 h-4" aria-hidden="true" />
                          ) : (
                            <Eye className="w-4 h-4" aria-hidden="true" />
                          )}
                        </button>
                      </div>
                    </motion.div>

                    {/* Submit Button */}
                    <motion.div variants={fadeInUp}>
                      <Button 
                        type="submit" 
                        className="w-full mt-6 bg-gradient-to-r from-violet-600 to-violet-700 hover:from-violet-500 hover:to-violet-600 text-white py-6 text-base font-medium shadow-lg shadow-violet-500/25 hover:shadow-violet-500/40 transition-all duration-300 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-500"
                        disabled={loading}
                        aria-disabled={loading}
                        data-testid="login-submit-btn"
                      >
                        {loading ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin mr-2" aria-hidden="true" />
                            <span>Signing in...</span>
                          </>
                        ) : (
                          <>
                            <span>Sign In</span>
                            <ArrowRight className="w-4 h-4 ml-2" aria-hidden="true" />
                          </>
                        )}
                      </Button>
                    </motion.div>
                  </form>

                  {/* Create Account Link */}
                  <motion.div variants={fadeInUp} className="mt-6 pt-6 border-t border-zinc-800 text-center">
                    <p className="text-sm text-zinc-400">
                      Don't have an account?{' '}
                      <Link 
                        to="/register" 
                        className="text-violet-400 hover:text-violet-300 font-medium transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-500 rounded" 
                        data-testid="register-link"
                      >
                        Create account
                      </Link>
                    </p>
                    <p className="text-xs text-zinc-500 mt-2">
                      Free for first 5 shipments • No credit card required
                    </p>
                  </motion.div>
                </CardContent>
              </Card>
            </motion.div>

            {/* Trust Indicators */}
            <motion.div 
              variants={fadeInUp}
              className="mt-6 flex flex-wrap items-center justify-center gap-4 text-xs text-zinc-500"
            >
              <span className="flex items-center gap-1">
                <svg className="w-4 h-4 text-emerald-400" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                  <path fillRule="evenodd" d="M10 1a4.5 4.5 0 00-4.5 4.5V9H5a2 2 0 00-2 2v6a2 2 0 002 2h10a2 2 0 002-2v-6a2 2 0 00-2-2h-.5V5.5A4.5 4.5 0 0010 1zm3 8V5.5a3 3 0 10-6 0V9h6z" clipRule="evenodd" />
                </svg>
                Secure & Encrypted
              </span>
              <span className="text-zinc-700" aria-hidden="true">•</span>
              <span>Indian Data Residency</span>
              <span className="text-zinc-700" aria-hidden="true">•</span>
              <span>ISO 27001 Certified</span>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </LoginErrorBoundary>
  );
}