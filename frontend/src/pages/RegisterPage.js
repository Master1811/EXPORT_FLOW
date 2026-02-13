import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Ship, ArrowRight, Loader2, Eye, EyeOff, CheckCircle, Sparkles } from 'lucide-react';
import { toast } from 'sonner';

// Animation variants
const fadeInUp = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.25, 0.1, 0.25, 1] } }
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
class RegisterErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Register Page Error:', error, errorInfo);
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
    href="#register-form" 
    className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-[100] focus:px-4 focus:py-2 focus:bg-violet-600 focus:text-white focus:rounded-lg"
  >
    Skip to registration form
  </a>
);

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    company_name: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState(0);
  const { register } = useAuth();
  const navigate = useNavigate();

  // Set document title and meta tags
  useEffect(() => {
    document.title = 'Create Account - ExportFlow';
    
    const updateMetaTag = (name, content) => {
      let element = document.querySelector(`meta[name="${name}"]`);
      if (!element) {
        element = document.createElement('meta');
        element.setAttribute('name', name);
        document.head.appendChild(element);
      }
      element.setAttribute('content', content);
    };

    updateMetaTag('description', 'Create your ExportFlow account and start managing your export business efficiently.');
    updateMetaTag('robots', 'noindex, nofollow'); // Auth pages shouldn't be indexed
  }, []);

  // Calculate password strength
  useEffect(() => {
    const password = formData.password;
    let strength = 0;
    
    if (password.length >= 6) strength += 1;
    if (password.length >= 10) strength += 1;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength += 1;
    if (/\d/.test(password)) strength += 1;
    if (/[^a-zA-Z\d]/.test(password)) strength += 1;
    
    setPasswordStrength(Math.min(strength, 3));
  }, [formData.password]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await register(formData.email, formData.password, formData.full_name, formData.company_name);
      toast.success('Account created successfully!');
      navigate('/dashboard');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Registration failed. Please try again.');
      console.error('Registration error:', error);
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

  const getPasswordStrengthColor = () => {
    if (passwordStrength === 0) return 'bg-zinc-700';
    if (passwordStrength === 1) return 'bg-red-500';
    if (passwordStrength === 2) return 'bg-amber-500';
    return 'bg-emerald-500';
  };

  const getPasswordStrengthText = () => {
    if (passwordStrength === 0) return '';
    if (passwordStrength === 1) return 'Weak';
    if (passwordStrength === 2) return 'Medium';
    return 'Strong';
  };

  return (
    <RegisterErrorBoundary>
      <SkipLink />
      
      <div className="min-h-screen flex items-center justify-center p-4 sm:p-8 bg-[#09090B] overflow-hidden relative">
        {/* Gradient Orbs Background */}
        <div className="absolute top-1/4 right-1/4 w-[300px] sm:w-[500px] h-[300px] sm:h-[500px] bg-violet-600/20 rounded-full blur-orb" aria-hidden="true" />
        <div className="absolute bottom-1/4 left-1/4 w-[200px] sm:w-[400px] h-[200px] sm:h-[400px] bg-blue-600/10 rounded-full blur-orb" style={{ animationDelay: '1s' }} aria-hidden="true" />
        
        <motion.div 
          className="w-full max-w-md relative z-10"
          initial="hidden"
          animate="visible"
          variants={staggerContainer}
        >
          {/* Logo Header */}
          <motion.div 
            variants={fadeInUp}
            className="flex items-center gap-3 mb-8 justify-center"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-600 to-violet-800 flex items-center justify-center" aria-hidden="true">
              <Ship className="w-6 h-6 text-white" strokeWidth={1.5} aria-hidden="true" />
            </div>
            <span className="text-2xl font-bold tracking-tight text-white">
              Export<span className="text-violet-400">Flow</span>
            </span>
          </motion.div>

          {/* Main Card */}
          <motion.div variants={fadeInUp}>
            <Card className="border-zinc-800 bg-zinc-900/50 backdrop-blur-sm shadow-2xl shadow-violet-500/10">
              <CardHeader className="space-y-2 pb-6">
                <div className="flex items-center gap-2 mb-2">
                  <Sparkles className="w-5 h-5 text-violet-400" aria-hidden="true" />
                  <span className="text-sm text-violet-400 font-medium">Get Started Free</span>
                </div>
                <CardTitle className="text-2xl sm:text-3xl font-bold text-white">
                  Create Account
                </CardTitle>
                <CardDescription className="text-zinc-400 text-base">
                  Start managing your export business in minutes
                </CardDescription>
              </CardHeader>
              
              <CardContent>
                <form 
                  id="register-form"
                  onSubmit={handleSubmit} 
                  className="space-y-4"
                  noValidate
                  aria-label="Registration form"
                >
                  {/* Full Name Field */}
                  <motion.div variants={fadeInUp} className="space-y-2">
                    <Label 
                      htmlFor="full_name" 
                      className="text-zinc-200 font-medium"
                    >
                      Full Name <span className="text-red-400" aria-label="required">*</span>
                    </Label>
                    <Input
                      id="full_name"
                      name="full_name"
                      type="text"
                      placeholder="John Doe"
                      value={formData.full_name}
                      onChange={handleChange}
                      required
                      autoComplete="name"
                      aria-required="true"
                      aria-invalid={formData.full_name.length > 0 && formData.full_name.length < 2 ? "true" : "false"}
                      data-testid="register-name-input"
                      className="bg-zinc-800/50 border-zinc-700 text-white placeholder:text-zinc-500 focus:border-violet-500 focus:ring-violet-500/20 transition-all"
                    />
                  </motion.div>

                  {/* Company Name Field */}
                  <motion.div variants={fadeInUp} className="space-y-2">
                    <Label 
                      htmlFor="company_name" 
                      className="text-zinc-200 font-medium"
                    >
                      Company Name <span className="text-zinc-500 text-sm font-normal">(Optional)</span>
                    </Label>
                    <Input
                      id="company_name"
                      name="company_name"
                      type="text"
                      placeholder="Export Corp Pvt Ltd"
                      value={formData.company_name}
                      onChange={handleChange}
                      autoComplete="organization"
                      data-testid="register-company-input"
                      className="bg-zinc-800/50 border-zinc-700 text-white placeholder:text-zinc-500 focus:border-violet-500 focus:ring-violet-500/20 transition-all"
                    />
                  </motion.div>

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
                      name="email"
                      type="email"
                      placeholder="name@company.com"
                      value={formData.email}
                      onChange={handleChange}
                      required
                      autoComplete="email"
                      aria-required="true"
                      aria-invalid={formData.email.length > 0 && !formData.email.includes('@') ? "true" : "false"}
                      data-testid="register-email-input"
                      className="bg-zinc-800/50 border-zinc-700 text-white placeholder:text-zinc-500 focus:border-violet-500 focus:ring-violet-500/20 transition-all"
                    />
                  </motion.div>

                  {/* Password Field */}
                  <motion.div variants={fadeInUp} className="space-y-2">
                    <Label 
                      htmlFor="password" 
                      className="text-zinc-200 font-medium"
                    >
                      Password <span className="text-red-400" aria-label="required">*</span>
                    </Label>
                    <div className="relative">
                      <Input
                        id="password"
                        name="password"
                        type={showPassword ? 'text' : 'password'}
                        placeholder="Create a strong password"
                        value={formData.password}
                        onChange={handleChange}
                        required
                        minLength={6}
                        autoComplete="new-password"
                        aria-required="true"
                        aria-invalid={formData.password.length > 0 && formData.password.length < 6 ? "true" : "false"}
                        aria-describedby="password-strength"
                        data-testid="register-password-input"
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
                    
                    {/* Password Strength Indicator */}
                    {formData.password.length > 0 && (
                      <div id="password-strength" className="space-y-2" role="status" aria-live="polite">
                        <div className="flex gap-1">
                          {[1, 2, 3].map((level) => (
                            <div
                              key={level}
                              className={`h-1 flex-1 rounded-full transition-all duration-300 ${
                                level <= passwordStrength ? getPasswordStrengthColor() : 'bg-zinc-700'
                              }`}
                              aria-hidden="true"
                            />
                          ))}
                        </div>
                        {passwordStrength > 0 && (
                          <p className="text-xs text-zinc-400">
                            Password strength: <span className={
                              passwordStrength === 1 ? 'text-red-400' :
                              passwordStrength === 2 ? 'text-amber-400' :
                              'text-emerald-400'
                            }>{getPasswordStrengthText()}</span>
                          </p>
                        )}
                      </div>
                    )}
                  </motion.div>

                  {/* Submit Button */}
                  <motion.div variants={fadeInUp}>
                    <Button 
                      type="submit" 
                      className="w-full mt-6 bg-gradient-to-r from-violet-600 to-violet-700 hover:from-violet-500 hover:to-violet-600 text-white py-6 text-base font-medium shadow-lg shadow-violet-500/25 hover:shadow-violet-500/40 transition-all duration-300 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-500"
                      disabled={loading}
                      aria-disabled={loading}
                      data-testid="register-submit-btn"
                    >
                      {loading ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin mr-2" aria-hidden="true" />
                          <span>Creating Account...</span>
                        </>
                      ) : (
                        <>
                          <span>Create Account</span>
                          <ArrowRight className="w-4 h-4 ml-2" aria-hidden="true" />
                        </>
                      )}
                    </Button>
                  </motion.div>

                  {/* Features List */}
                  <motion.div variants={fadeInUp} className="pt-4 border-t border-zinc-800">
                    <p className="text-sm text-zinc-400 mb-3">What you'll get:</p>
                    <ul className="space-y-2" role="list">
                      {[
                        'Free for first 5 shipments',
                        'GST refund tracking',
                        'Export incentive calculator',
                        'No credit card required'
                      ].map((feature, index) => (
                        <li key={index} className="flex items-center gap-2 text-sm text-zinc-300">
                          <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0" aria-hidden="true" />
                          <span>{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </motion.div>
                </form>

                {/* Sign In Link */}
                <motion.div variants={fadeInUp} className="mt-6 pt-6 border-t border-zinc-800 text-center">
                  <p className="text-sm text-zinc-400">
                    Already have an account?{' '}
                    <Link 
                      to="/login" 
                      className="text-violet-400 hover:text-violet-300 font-medium transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-500 rounded" 
                      data-testid="login-link"
                    >
                      Sign in
                    </Link>
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
            <span className="text-zinc-700">•</span>
            <span>Indian Data Residency</span>
            <span className="text-zinc-700">•</span>
            <span>GDPR Compliant</span>
          </motion.div>
        </motion.div>
      </div>
    </RegisterErrorBoundary>
  );
}