import React, { useEffect, useRef, useState, useMemo, lazy, Suspense } from 'react';
import { motion, useInView, useScroll, useTransform } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { 
  Factory, Ship, Landmark, ArrowRight, Shield, Eye, Lock, 
  Database, FileCheck, TrendingUp, Clock, AlertTriangle, 
  IndianRupee, CheckCircle, Sparkles, ChevronDown, Users,
  Target, Mail, Building, MessageSquare, Send, Loader2
} from 'lucide-react';
import { toast } from 'sonner';

// Error Boundary Component
class AnimationErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Animation Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <div className="animate-none">{this.props.children}</div>;
    }
    return this.props.children;
  }
}

// Loading Spinner Component
const LoadingSpinner = () => (
  <div className="flex items-center justify-center min-h-[400px]" role="status" aria-live="polite">
    <div className="w-12 h-12 border-4 border-violet-600/30 border-t-violet-600 rounded-full animate-spin" aria-hidden="true" />
    <span className="sr-only">Loading content...</span>
  </div>
);

// Animation variants - memoized for performance
const fadeInUp = {
  hidden: { opacity: 0, y: 40 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: [0.25, 0.1, 0.25, 1] } }
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.2, delayChildren: 0.1 } }
};

const scaleIn = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: { opacity: 1, scale: 1, transition: { duration: 0.6, ease: [0.25, 0.1, 0.25, 1] } }
};

// 3D-style animated journey component
const ExportJourney = React.memo(() => {
  const [activeStep, setActiveStep] = useState(0);
  const steps = useMemo(() => [
    { icon: Factory, label: 'Factory', color: '#7C3AED', desc: 'Invoice created & shipment logged' },
    { icon: Ship, label: 'Port', color: '#3B82F6', desc: 'Documents secured & compliance tracked' },
    { icon: Landmark, label: 'Bank', color: '#10B981', desc: 'Payments reconciled & incentives recovered' }
  ], []);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev + 1) % 3);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleStepClick = (index) => {
    setActiveStep(index);
  };

  const handleKeyDown = (e, index) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      setActiveStep(index);
    }
  };

  return (
    <div className="relative w-full max-w-4xl mx-auto" role="tablist" aria-label="Export journey steps">
      {/* Connection Line */}
      <div className="absolute top-1/2 left-0 right-0 h-1 bg-gradient-to-r from-violet-600/20 via-blue-500/20 to-emerald-500/20 -translate-y-1/2 hidden md:block" aria-hidden="true" />
      
      {/* Progress Line */}
      <motion.div 
        className="absolute top-1/2 left-0 h-1 bg-gradient-to-r from-violet-600 via-blue-500 to-emerald-500 -translate-y-1/2 hidden md:block progress-line"
        initial={{ width: '0%' }}
        animate={{ width: `${(activeStep + 1) * 33.33}%` }}
        transition={{ duration: 0.8, ease: 'easeInOut' }}
        aria-hidden="true"
      />
      
      <div className="flex flex-col md:flex-row justify-between items-center gap-8 md:gap-4">
        {steps.map((step, index) => {
          const Icon = step.icon;
          const isActive = index <= activeStep;
          
          return (
            <motion.div
              key={step.label}
              role="tab"
              aria-selected={index === activeStep}
              aria-controls={`panel-${index}`}
              tabIndex={0}
              className="relative flex flex-col items-center cursor-pointer group focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-violet-500 rounded-2xl"
              onClick={() => handleStepClick(index)}
              onKeyDown={(e) => handleKeyDown(e, index)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {/* Glow Effect */}
              <motion.div
                className="absolute inset-0 rounded-full blur-xl opacity-0 group-hover:opacity-50 transition-opacity glow-effect"
                style={{ backgroundColor: step.color }}
                animate={isActive ? { opacity: 0.3, scale: 1.2 } : { opacity: 0, scale: 1 }}
                aria-hidden="true"
              />
              
              {/* Icon Container */}
              <motion.div
                className={`relative w-24 h-24 md:w-32 md:h-32 rounded-2xl flex items-center justify-center border-2 transition-all duration-500 ${
                  isActive 
                    ? 'bg-gradient-to-br from-violet-600/20 to-transparent border-violet-500/50' 
                    : 'bg-zinc-900/50 border-zinc-800'
                }`}
                animate={isActive ? { 
                  boxShadow: `0 0 40px ${step.color}40`,
                  borderColor: step.color
                } : {}}
              >
                <Icon 
                  className={`w-10 h-10 md:w-14 md:h-14 transition-all duration-500 ${
                    isActive ? 'text-white' : 'text-zinc-500'
                  }`}
                  style={isActive ? { color: step.color } : {}}
                  aria-hidden="true"
                />
                
                {/* Floating coin animation */}
                {index === 2 && isActive && (
                  <motion.div
                    className="absolute -top-2 -right-2"
                    initial={{ scale: 0, rotate: -180 }}
                    animate={{ scale: 1, rotate: 0 }}
                    transition={{ delay: 0.3, type: 'spring', stiffness: 200 }}
                    aria-hidden="true"
                  >
                    <div className="w-8 h-8 rounded-full bg-emerald-500 flex items-center justify-center">
                      <IndianRupee className="w-4 h-4 text-white" aria-hidden="true" />
                    </div>
                  </motion.div>
                )}
              </motion.div>
              
              {/* Label */}
              <motion.p 
                className={`mt-4 font-medium text-lg ${isActive ? 'text-white' : 'text-zinc-400'}`}
                animate={isActive ? { y: 0 } : { y: 5 }}
              >
                {step.label}
              </motion.p>
              
              {/* Description */}
              <motion.p 
                id={`panel-${index}`}
                role="tabpanel"
                className={`text-sm text-center max-w-[180px] mt-2 ${isActive ? 'text-zinc-400' : 'text-zinc-600'}`}
                initial={{ opacity: 0, height: 0 }}
                animate={isActive ? { opacity: 1, height: 'auto' } : { opacity: 0, height: 0 }}
              >
                {step.desc}
              </motion.p>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
});

ExportJourney.displayName = 'ExportJourney';

// Problem Card Component
const ProblemCard = React.memo(({ icon: Icon, title, amount, description, color, delay }) => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });
  
  return (
    <motion.article
      ref={ref}
      initial="hidden"
      animate={isInView ? 'visible' : 'hidden'}
      variants={scaleIn}
      transition={{ delay }}
      className="group relative"
    >
      <div className={`absolute inset-0 bg-gradient-to-br ${color} opacity-0 group-hover:opacity-10 rounded-2xl transition-opacity duration-500`} aria-hidden="true" />
      <div className="relative p-8 rounded-2xl border border-zinc-800 bg-zinc-900/50 backdrop-blur-sm hover:border-zinc-700 transition-all duration-500">
        <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center mb-6`} aria-hidden="true">
          <Icon className="w-7 h-7 text-white" aria-hidden="true" />
        </div>
        <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
        <p className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-orange-400 mb-3">
          {amount}
        </p>
        <p className="text-zinc-300 leading-relaxed">{description}</p>
      </div>
    </motion.article>
  );
});

ProblemCard.displayName = 'ProblemCard';

// Feature Card Component
const FeatureCard = React.memo(({ icon: Icon, title, description, gradient }) => {
  return (
    <motion.article
      whileHover={{ y: -8, scale: 1.02 }}
      transition={{ type: 'spring', stiffness: 300 }}
      className="group relative overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-900/50 p-8 hover:border-violet-500/50 transition-colors duration-500 feature-card"
    >
      {/* Background gradient on hover */}
      <div className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-500`} aria-hidden="true" />
      
      <div className="relative z-10">
        <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center mb-5`} aria-hidden="true">
          <Icon className="w-6 h-6 text-white" aria-hidden="true" />
        </div>
        <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
        <p className="text-zinc-300 text-sm leading-relaxed">{description}</p>
      </div>
    </motion.article>
  );
});

FeatureCard.displayName = 'FeatureCard';

// Trust Badge Component
const TrustBadge = React.memo(({ icon: Icon, text }) => (
  <motion.div 
    whileHover={{ scale: 1.05 }}
    className="flex items-center gap-3 px-5 py-3 rounded-full border border-zinc-800 bg-zinc-900/50 trust-badge"
  >
    <Icon className="w-5 h-5 text-emerald-400" aria-hidden="true" />
    <span className="text-zinc-200 text-sm">{text}</span>
  </motion.div>
));

TrustBadge.displayName = 'TrustBadge';

// Skip Link Component
const SkipLink = () => (
  <a 
    href="#main-content" 
    className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-[100] focus:px-4 focus:py-2 focus:bg-violet-600 focus:text-white focus:rounded-lg"
  >
    Skip to main content
  </a>
);

// Main Landing Page
export default function LandingPage() {
  const navigate = useNavigate();
  const heroRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: heroRef,
    offset: ['start start', 'end start']
  });
  
  const heroOpacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);
  const heroY = useTransform(scrollYProgress, [0, 0.5], [0, -100]);

  // Handle navigation
  const handleNavigation = (path) => {
    navigate(path);
  };

  const handleEmailClick = (e) => {
    e.preventDefault();
    window.open('mailto:sales@exportflow.in', '_blank', 'noopener,noreferrer');
  };

  return (
    <>
      <Helmet>
        <html lang="en" />
        <title>ExportFlow - Track GST Refunds & Export Incentives for Indian Exporters</title>
        <meta name="description" content="Stop losing 3-5% of export margin to manual mistakes. Track receivables, GST refunds, RoDTEP and export incentives without spreadsheets. Built for Indian exporters." />
        <meta name="keywords" content="export management, GST refund, RoDTEP, export incentives, Indian exporters, receivables tracking, working capital" />
        
        {/* Open Graph Tags */}
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://exportflow.in" />
        <meta property="og:title" content="ExportFlow - Export Management for Indian Businesses" />
        <meta property="og:description" content="Track receivables, GST refunds, and export incentives — without spreadsheets or stress." />
        <meta property="og:image" content="https://exportflow.in/og-image.jpg" />
        <meta property="og:site_name" content="ExportFlow" />
        
        {/* Twitter Card Tags */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:url" content="https://exportflow.in" />
        <meta name="twitter:title" content="ExportFlow - Export Management for Indian Businesses" />
        <meta name="twitter:description" content="Track receivables, GST refunds, and export incentives — without spreadsheets or stress." />
        <meta name="twitter:image" content="https://exportflow.in/twitter-image.jpg" />
        
        {/* Additional Meta Tags */}
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <meta name="theme-color" content="#7C3AED" />
        <link rel="canonical" href="https://exportflow.in" />
        
        {/* Structured Data - Organization */}
        <script type="application/ld+json">
          {JSON.stringify({
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "ExportFlow",
            "url": "https://exportflow.in",
            "logo": "https://exportflow.in/logo.png",
            "description": "Export management platform for Indian businesses",
            "contactPoint": {
              "@type": "ContactPoint",
              "email": "sales@exportflow.in",
              "contactType": "Sales"
            },
            "address": {
              "@type": "PostalAddress",
              "addressCountry": "IN"
            }
          })}
        </script>
        
        {/* Structured Data - SoftwareApplication */}
        <script type="application/ld+json">
          {JSON.stringify({
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": "ExportFlow",
            "applicationCategory": "BusinessApplication",
            "operatingSystem": "Web",
            "offers": [
              {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "INR",
                "name": "Starter Plan"
              },
              {
                "@type": "Offer",
                "price": "2999",
                "priceCurrency": "INR",
                "name": "Professional Plan"
              }
            ],
            "description": "Track receivables, GST refunds, and export incentives for Indian exporters"
          })}
        </script>
      </Helmet>

      <SkipLink />

      <div className="min-h-screen bg-[#09090B] text-white overflow-x-hidden">
        {/* Navigation */}
        <nav 
          className="fixed top-0 left-0 right-0 z-50 px-4 sm:px-6 py-4 bg-[#09090B]/80 backdrop-blur-xl border-b border-zinc-800/50 nav-header"
          role="navigation"
          aria-label="Main navigation"
          style={{ paddingTop: 'max(1rem, env(safe-area-inset-top))' }}
        >
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-600 to-violet-800 flex items-center justify-center" aria-hidden="true">
                <Ship className="w-5 h-5 text-white" aria-hidden="true" />
              </div>
              <span className="text-xl font-bold tracking-tight">Export<span className="text-violet-400">Flow</span></span>
            </div>
            
            <div className="flex items-center gap-4">
              <Button 
                variant="ghost" 
                className="text-zinc-300 hover:text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-500"
                onClick={() => handleNavigation('/login')}
                aria-label="Sign in to your account"
              >
                Sign In
              </Button>
              <Button 
                className="bg-violet-600 hover:bg-violet-700 text-white px-6 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-500"
                onClick={() => handleNavigation('/register')}
                aria-label="Get started with ExportFlow"
              >
                Get Started
              </Button>
            </div>
          </div>
        </nav>

        <main id="main-content" role="main">
          <AnimationErrorBoundary>
            {/* Hero Section */}
            <section 
              ref={heroRef} 
              className="relative min-h-screen flex items-center justify-center pt-20 overflow-hidden"
              aria-labelledby="hero-heading"
            >
              {/* Gradient Orbs */}
              <div className="absolute top-1/4 left-1/4 w-[300px] sm:w-[400px] md:w-[600px] h-[300px] sm:h-[400px] md:h-[600px] bg-violet-600/20 rounded-full blur-orb" aria-hidden="true" />
              <div className="absolute bottom-1/4 right-1/4 w-[200px] sm:w-[300px] md:w-[400px] h-[200px] sm:h-[300px] md:h-[400px] bg-blue-600/10 rounded-full blur-orb" style={{ animationDelay: '1s' }} aria-hidden="true" />
              
              <motion.div 
                style={{ opacity: heroOpacity, y: heroY }}
                className="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 text-center"
              >
                {/* Badge */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-violet-500/30 bg-violet-500/10 mb-8"
                  role="status"
                  aria-label="Built for Indian Exporters"
                >
                  <Sparkles className="w-4 h-4 text-violet-400" aria-hidden="true" />
                  <span className="text-sm text-violet-300">Built for Indian Exporters</span>
                </motion.div>
                
                {/* Headline */}
                <motion.h1
                  id="hero-heading"
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3, duration: 0.8 }}
                  className="text-3xl sm:text-4xl md:text-5xl lg:text-7xl font-bold leading-tight tracking-tight mb-6"
                >
                  Stop losing{' '}
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 via-fuchsia-400 to-violet-400">
                    3–5%
                  </span>{' '}
                  of your export margin to manual mistakes.
                </motion.h1>
                
                {/* Subheadline */}
                <motion.p
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5, duration: 0.8 }}
                  className="text-base sm:text-lg md:text-xl text-zinc-300 max-w-2xl mx-auto mb-10 leading-relaxed"
                >
                  Track receivables, GST refunds, and export incentives — without spreadsheets or stress.
                </motion.p>
                
                {/* CTA */}
                <motion.div
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.7 }}
                >
                  <Button
                    size="lg"
                    className="bg-gradient-to-r from-violet-600 to-violet-700 hover:from-violet-500 hover:to-violet-600 text-white px-8 sm:px-10 py-6 sm:py-7 text-base sm:text-lg rounded-xl shadow-lg shadow-violet-500/25 hover:shadow-violet-500/40 transition-all duration-300 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-500"
                    onClick={() => handleNavigation('/register')}
                    aria-label="Start recovering capital - Sign up now"
                  >
                    Start Recovering Capital
                    <ArrowRight className="w-5 h-5 ml-2" aria-hidden="true" />
                  </Button>
                </motion.div>
                
                {/* Trust Line */}
                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 1 }}
                  className="mt-8 text-sm text-zinc-400"
                >
                  No credit card required • Free for first 5 shipments
                </motion.p>
                
                {/* Scroll Indicator */}
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 1.5 }}
                  className="absolute bottom-10 left-1/2 -translate-x-1/2"
                  aria-hidden="true"
                >
                  <motion.div
                    animate={{ y: [0, 10, 0] }}
                    transition={{ repeat: Infinity, duration: 2 }}
                  >
                    <ChevronDown className="w-6 h-6 text-zinc-500" aria-hidden="true" />
                  </motion.div>
                </motion.div>
              </motion.div>
            </section>

            {/* Problem Section */}
            <section className="py-16 sm:py-24 px-4 sm:px-6 relative" aria-labelledby="problem-heading">
              <div className="max-w-6xl mx-auto">
                <motion.div
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true, margin: '-100px' }}
                  variants={fadeInUp}
                  className="text-center mb-12 sm:mb-16"
                >
                  <h2 id="problem-heading" className="text-2xl sm:text-3xl md:text-4xl font-bold mb-4">
                    Where Indian Exporters{' '}
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-orange-400">
                      Lose Money
                    </span>{' '}
                    (Silently)
                  </h2>
                  <p className="text-zinc-300 text-base sm:text-lg max-w-2xl mx-auto">
                    Every delayed refund, every missed incentive, every late payment — it adds up.
                  </p>
                </motion.div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <ProblemCard
                    icon={Clock}
                    title="Blocked Cash"
                    amount="₹2-5 Lakhs"
                    description="GST refunds delayed 30–90 days. Your working capital stuck while you take expensive loans."
                    color="from-red-500 to-orange-500"
                    delay={0}
                  />
                  <ProblemCard
                    icon={AlertTriangle}
                    title="Missed Incentives"
                    amount="₹50K-2L/year"
                    description="RoDTEP & RoSCTL percentages unclear. HS code mistakes mean money lost forever."
                    color="from-amber-500 to-yellow-500"
                    delay={0.1}
                  />
                  <ProblemCard
                    icon={TrendingUp}
                    title="Payment Delays"
                    amount="45-90 days"
                    description="Buyers delay payments. No visibility on who is choking your cashflow."
                    color="from-violet-500 to-purple-500"
                    delay={0.2}
                  />
                </div>
              </div>
            </section>

            {/* How It Works Section */}
            <section 
              className="py-16 sm:py-24 px-4 sm:px-6 relative bg-gradient-to-b from-transparent via-violet-950/10 to-transparent"
              aria-labelledby="how-it-works-heading"
            >
              <div className="max-w-6xl mx-auto">
                <motion.div
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true, margin: '-100px' }}
                  variants={fadeInUp}
                  className="text-center mb-12 sm:mb-16"
                >
                  <h2 id="how-it-works-heading" className="text-2xl sm:text-3xl md:text-4xl font-bold mb-4">
                    From Shipment to Money —{' '}
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-blue-400">
                      Visually
                    </span>
                  </h2>
                  <p className="text-zinc-300 text-base sm:text-lg max-w-2xl mx-auto">
                    See your export journey like never before. Click each step to explore.
                  </p>
                </motion.div>
                
                <motion.div
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true, margin: '-100px' }}
                  variants={scaleIn}
                >
                  <ExportJourney />
                </motion.div>
              </div>
            </section>

            {/* Features Section */}
            <section className="py-16 sm:py-24 px-4 sm:px-6 relative" aria-labelledby="features-heading">
              <div className="max-w-6xl mx-auto">
                <motion.div
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true, margin: '-100px' }}
                  variants={fadeInUp}
                  className="text-center mb-12 sm:mb-16"
                >
                  <h2 id="features-heading" className="text-2xl sm:text-3xl md:text-4xl font-bold mb-4">
                    What ExportFlow Does{' '}
                    <span className="text-zinc-400">(No Noise)</span>
                  </h2>
                  <p className="text-zinc-300 text-base sm:text-lg">
                    No AI hype. No automation promises. Just money visibility.
                  </p>
                </motion.div>
                
                <motion.div
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true, margin: '-100px' }}
                  variants={staggerContainer}
                  className="grid grid-cols-1 md:grid-cols-3 gap-6"
                >
                  <motion.div variants={fadeInUp}>
                    <FeatureCard
                      icon={TrendingUp}
                      title="Receivable Aging Dashboard"
                      description="See who owes you money — today. Know exactly which buyers are delaying and by how many days."
                      gradient="from-emerald-500 to-teal-500"
                    />
                  </motion.div>
                  <motion.div variants={fadeInUp}>
                    <FeatureCard
                      icon={IndianRupee}
                      title="GST Refund Estimator"
                      description="Know how much GST is coming & when. Stop wondering — start planning your cash flow."
                      gradient="from-blue-500 to-cyan-500"
                    />
                  </motion.div>
                  <motion.div variants={fadeInUp}>
                    <FeatureCard
                      icon={AlertTriangle}
                      title="Incentive Loss Tracker"
                      description="Know how much RoDTEP you already lost. Never leave money on the table again."
                      gradient="from-violet-500 to-purple-500"
                    />
                  </motion.div>
                </motion.div>
              </div>
            </section>

            {/* Trust Section */}
            <section className="py-16 sm:py-24 px-4 sm:px-6 relative" aria-labelledby="trust-heading">
              <div className="max-w-4xl mx-auto">
                <motion.div
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true, margin: '-100px' }}
                  variants={fadeInUp}
                  className="text-center mb-12"
                >
                  <h2 id="trust-heading" className="text-2xl sm:text-3xl md:text-4xl font-bold mb-4">
                    Built for{' '}
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-400">
                      Trust
                    </span>
                    , Not Tricks
                  </h2>
                  <p className="text-zinc-300 text-base sm:text-lg">
                    Your data security is our top priority. Always.
                  </p>
                </motion.div>
                
                <motion.div
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true, margin: '-100px' }}
                  variants={staggerContainer}
                  className="flex flex-wrap justify-center gap-4"
                >
                  <motion.div variants={scaleIn}><TrustBadge icon={Lock} text="No bank logins required" /></motion.div>
                  <motion.div variants={scaleIn}><TrustBadge icon={Shield} text="No GST credentials stored" /></motion.div>
                  <motion.div variants={scaleIn}><TrustBadge icon={Eye} text="PII masked by default" /></motion.div>
                  <motion.div variants={scaleIn}><TrustBadge icon={Database} text="Indian data residency" /></motion.div>
                  <motion.div variants={scaleIn}><TrustBadge icon={FileCheck} text="Audit logs for every action" /></motion.div>
                </motion.div>
              </div>
            </section>

            {/* Dashboard Preview Section */}
            <section 
              className="py-16 sm:py-24 px-4 sm:px-6 relative overflow-hidden"
              aria-labelledby="dashboard-preview-heading"
            >
              <div className="absolute inset-0 bg-gradient-to-b from-transparent via-violet-950/5 to-transparent" aria-hidden="true" />
              
              <div className="max-w-6xl mx-auto">
                <motion.div
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true, margin: '-100px' }}
                  variants={fadeInUp}
                  className="text-center mb-12"
                >
                  <h2 id="dashboard-preview-heading" className="text-2xl sm:text-3xl md:text-4xl font-bold mb-4">
                    See ExportFlow{' '}
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-blue-400">
                      in Action
                    </span>
                  </h2>
                  <p className="text-zinc-300 text-base sm:text-lg max-w-2xl mx-auto">
                    A clean, powerful dashboard designed for busy exporters. No clutter, just insights.
                  </p>
                </motion.div>
                
                <motion.div
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true, margin: '-100px' }}
                  variants={scaleIn}
                  className="relative"
                >
                  {/* Dashboard Preview Mock */}
                  <div className="relative rounded-2xl border border-zinc-800 bg-zinc-900/90 backdrop-blur-sm overflow-hidden shadow-2xl shadow-violet-500/10">
                    {/* Browser Chrome */}
                    <div className="flex items-center gap-2 px-4 py-3 bg-zinc-800/50 border-b border-zinc-700" aria-hidden="true">
                      <div className="flex gap-1.5">
                        <div className="w-3 h-3 rounded-full bg-red-500/80" />
                        <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                        <div className="w-3 h-3 rounded-full bg-green-500/80" />
                      </div>
                      <div className="flex-1 mx-4">
                        <div className="bg-zinc-700/50 rounded-md px-3 py-1.5 text-xs text-zinc-400 max-w-xs mx-auto">
                          app.exportflow.in/dashboard
                        </div>
                      </div>
                    </div>
                    
                    {/* Dashboard Content */}
                    <div className="p-3 sm:p-6 space-y-3 sm:space-y-6">
                      {/* Stats Row */}
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-4">
                        {[
                          { label: 'Total Exports', value: '₹45.2L', color: 'text-blue-400' },
                          { label: 'Receivables', value: '₹12.8L', color: 'text-amber-400' },
                          { label: 'Incentives', value: '₹2.1L', color: 'text-emerald-400' },
                          { label: 'GST Refund', value: '₹3.5L', color: 'text-violet-400' }
                        ].map((stat, i) => (
                          <div key={i} className="bg-zinc-800/50 rounded-lg p-3 sm:p-4 border border-zinc-700/50">
                            <p className="text-xs text-zinc-400 mb-1">{stat.label}</p>
                            <p className={`text-lg sm:text-xl font-bold ${stat.color}`}>{stat.value}</p>
                          </div>
                        ))}
                      </div>
                      
                      {/* Charts Row */}
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                        {/* Export Trend Chart */}
                        <div className="bg-zinc-800/50 rounded-lg p-3 sm:p-4 border border-zinc-700/50">
                          <p className="text-sm text-zinc-300 mb-3">Export Trend</p>
                          <div className="flex items-end justify-between h-20 sm:h-24 gap-2" role="img" aria-label="Export trend bar chart">
                            {[40, 55, 45, 70, 60, 80].map((h, i) => (
                              <div 
                                key={i} 
                                className="flex-1 bg-gradient-to-t from-blue-600 to-blue-400 rounded-sm chart-bar"
                                style={{ height: `${h}%` }}
                                aria-hidden="true"
                              />
                            ))}
                          </div>
                          <div className="flex justify-between mt-2 text-xs text-zinc-500">
                            <span>Jul</span><span>Aug</span><span>Sep</span><span>Oct</span><span>Nov</span><span>Dec</span>
                          </div>
                        </div>
                        
                        {/* Payment Status */}
                        <div className="bg-zinc-800/50 rounded-lg p-3 sm:p-4 border border-zinc-700/50">
                          <p className="text-sm text-zinc-300 mb-3">Payment Status</p>
                          <div className="flex items-center justify-center h-20 sm:h-24">
                            <div className="relative w-20 sm:w-24 h-20 sm:h-24" role="img" aria-label="Payment status pie chart showing 65% received">
                              <svg className="w-full h-full" viewBox="0 0 100 100" aria-hidden="true">
                                <circle cx="50" cy="50" r="40" fill="none" stroke="#27272A" strokeWidth="12" />
                                <circle cx="50" cy="50" r="40" fill="none" stroke="#10B981" strokeWidth="12" 
                                  strokeDasharray="163" strokeDashoffset="50" className="transform -rotate-90 origin-center" />
                                <circle cx="50" cy="50" r="40" fill="none" stroke="#F59E0B" strokeWidth="12" 
                                  strokeDasharray="163" strokeDashoffset="130" className="transform -rotate-90 origin-center" />
                              </svg>
                              <div className="absolute inset-0 flex items-center justify-center">
                                <span className="text-base sm:text-lg font-bold text-white">65%</span>
                              </div>
                            </div>
                          </div>
                          <div className="flex justify-center gap-4 mt-2 text-xs">
                            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-emerald-500" aria-hidden="true" /> Received</span>
                            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-amber-500" aria-hidden="true" /> Pending</span>
                          </div>
                        </div>
                      </div>
                      
                      {/* Alerts Row */}
                      <div className="bg-zinc-800/50 rounded-lg p-3 sm:p-4 border border-zinc-700/50">
                        <p className="text-sm text-zinc-300 mb-3">Risk Alerts</p>
                        <div className="space-y-2" role="list" aria-label="Risk alerts">
                          <div className="flex items-center gap-3 p-2 rounded-md bg-amber-500/10 border border-amber-500/20" role="listitem">
                            <span className="px-2 py-0.5 text-xs bg-amber-500/20 text-amber-300 rounded" aria-label="medium priority">medium</span>
                            <span className="text-sm text-zinc-200">e-BRC deadline in 12 days for SHP-2024-0042</span>
                          </div>
                          <div className="flex items-center gap-3 p-2 rounded-md bg-blue-500/10 border border-blue-500/20" role="listitem">
                            <span className="px-2 py-0.5 text-xs bg-blue-500/20 text-blue-300 rounded" aria-label="low priority">low</span>
                            <span className="text-sm text-zinc-200">Payment from ABC Traders is 45 days outstanding</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Decorative gradient */}
                  <div className="absolute -bottom-20 left-1/2 -translate-x-1/2 w-3/4 h-40 bg-violet-600/20 blur-[100px]" aria-hidden="true" />
                </motion.div>
              </div>
            </section>

            {/* Pricing Section */}
            <section className="py-16 sm:py-24 px-4 sm:px-6 relative" id="pricing" aria-labelledby="pricing-heading">
              <div className="max-w-5xl mx-auto">
                <motion.div
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true, margin: '-100px' }}
                  variants={fadeInUp}
                  className="text-center mb-12 sm:mb-16"
                >
                  <h2 id="pricing-heading" className="text-2xl sm:text-3xl md:text-4xl font-bold mb-4">
                    Simple,{' '}
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-400">
                      Transparent
                    </span>{' '}
                    Pricing
                  </h2>
                  <p className="text-zinc-300 text-base sm:text-lg">
                    Start free. Scale as you grow. No hidden fees.
                  </p>
                </motion.div>
                
                <motion.div
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true, margin: '-100px' }}
                  variants={staggerContainer}
                  className="grid grid-cols-1 md:grid-cols-3 gap-6"
                >
                  {/* Free Plan */}
                  <motion.article variants={fadeInUp}>
                    <div className="relative p-6 sm:p-8 rounded-2xl border border-zinc-800 bg-zinc-900/50 hover:border-zinc-700 transition-colors h-full">
                      <div className="mb-6">
                        <h3 className="text-xl font-semibold text-white mb-2">Starter</h3>
                        <p className="text-zinc-300 text-sm">Perfect for small exporters</p>
                      </div>
                      <div className="mb-6">
                        <span className="text-4xl font-bold text-white">Free</span>
                        <span className="text-zinc-400 ml-2">forever</span>
                      </div>
                      <ul className="space-y-3 mb-8" role="list">
                        {['Up to 5 shipments/month', 'Basic receivable tracking', 'GST refund calculator', 'Email support'].map((feature, i) => (
                          <li key={i} className="flex items-center gap-3 text-sm text-zinc-200">
                            <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0" aria-hidden="true" />
                            {feature}
                          </li>
                        ))}
                      </ul>
                      <Button 
                        variant="outline" 
                        className="w-full border-zinc-700 hover:bg-zinc-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-500"
                        onClick={() => handleNavigation('/register')}
                        aria-label="Get started with Starter plan"
                      >
                        Get Started Free
                      </Button>
                    </div>
                  </motion.article>
                  
                  {/* Pro Plan - Highlighted */}
                  <motion.article variants={fadeInUp}>
                    <div className="relative p-6 sm:p-8 rounded-2xl border-2 border-violet-500/50 bg-gradient-to-b from-violet-950/30 to-zinc-900/50 h-full">
                      {/* Popular Badge */}
                      <div className="absolute -top-3 left-1/2 -translate-x-1/2" aria-hidden="true">
                        <span className="px-3 py-1 bg-violet-600 text-white text-xs font-medium rounded-full">
                          Most Popular
                        </span>
                      </div>
                      <div className="mb-6">
                        <h3 className="text-xl font-semibold text-white mb-2">Professional</h3>
                        <p className="text-zinc-300 text-sm">For growing export businesses</p>
                      </div>
                      <div className="mb-6">
                        <span className="text-4xl font-bold text-white">₹2,999</span>
                        <span className="text-zinc-400 ml-2">/month</span>
                      </div>
                      <ul className="space-y-3 mb-8" role="list">
                        {[
                          'Unlimited shipments',
                          'Full incentive optimizer',
                          'e-BRC monitoring & alerts',
                          'Aging dashboard',
                          'AI-powered insights',
                          'Priority support'
                        ].map((feature, i) => (
                          <li key={i} className="flex items-center gap-3 text-sm text-zinc-200">
                            <CheckCircle className="w-4 h-4 text-violet-400 flex-shrink-0" aria-hidden="true" />
                            {feature}
                          </li>
                        ))}
                      </ul>
                      <Button 
                        className="w-full bg-violet-600 hover:bg-violet-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-500"
                        onClick={() => handleNavigation('/register')}
                        aria-label="Start 14-day trial of Professional plan"
                      >
                        Start 14-Day Trial
                      </Button>
                    </div>
                  </motion.article>
                  
                  {/* Enterprise Plan */}
                  <motion.article variants={fadeInUp}>
                    <div className="relative p-6 sm:p-8 rounded-2xl border border-zinc-800 bg-zinc-900/50 hover:border-zinc-700 transition-colors h-full">
                      <div className="mb-6">
                        <h3 className="text-xl font-semibold text-white mb-2">Enterprise</h3>
                        <p className="text-zinc-300 text-sm">For large export houses</p>
                      </div>
                      <div className="mb-6">
                        <span className="text-4xl font-bold text-white">Custom</span>
                      </div>
                      <ul className="space-y-3 mb-8" role="list">
                        {[
                          'Everything in Professional',
                          'Multi-user access',
                          'API integrations',
                          'Custom reports',
                          'Dedicated account manager',
                          'SLA guarantee'
                        ].map((feature, i) => (
                          <li key={i} className="flex items-center gap-3 text-sm text-zinc-200">
                            <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0" aria-hidden="true" />
                            {feature}
                          </li>
                        ))}
                      </ul>
                      <Button 
                        variant="outline" 
                        className="w-full border-zinc-700 hover:bg-zinc-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-500"
                        onClick={handleEmailClick}
                        aria-label="Contact sales for Enterprise plan"
                      >
                        Contact Sales
                      </Button>
                    </div>
                  </motion.article>
                </motion.div>
              </div>
            </section>

            {/* Final CTA Section */}
            <section className="py-24 sm:py-32 px-4 sm:px-6 relative" aria-labelledby="final-cta-heading">
              {/* Background gradient */}
              <div className="absolute inset-0 bg-gradient-to-t from-violet-950/30 via-transparent to-transparent" aria-hidden="true" />
              
              <motion.div
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, margin: '-100px' }}
                variants={fadeInUp}
                className="relative z-10 max-w-3xl mx-auto text-center"
              >
                <h2 id="final-cta-heading" className="text-2xl sm:text-3xl md:text-5xl font-bold mb-6">
                  Ready to see your{' '}
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-fuchsia-400">
                    hidden money
                  </span>
                  ?
                </h2>
                <p className="text-zinc-300 text-base sm:text-lg mb-10">
                  ExportFlow is not accounting software.<br />
                  <span className="text-white">It is a money visibility tool for Indian exporters.</span>
                </p>
                
                <Button
                  size="lg"
                  className="bg-gradient-to-r from-violet-600 to-violet-700 hover:from-violet-500 hover:to-violet-600 text-white px-10 sm:px-12 py-6 sm:py-7 text-base sm:text-lg rounded-xl shadow-lg shadow-violet-500/25 hover:shadow-violet-500/40 transition-all duration-300 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-500"
                  onClick={() => handleNavigation('/register')}
                  aria-label="Start free trial - No credit card needed"
                >
                  Start Free — No Card Needed
                  <ArrowRight className="w-5 h-5 ml-2" aria-hidden="true" />
                </Button>
                
                <p className="mt-6 text-sm text-zinc-400">
                  Join 100+ exporters already recovering capital
                </p>
              </motion.div>
            </section>
          </AnimationErrorBoundary>
        </main>

        {/* Footer */}
        <footer className="py-12 px-4 sm:px-6 border-t border-zinc-800" role="contentinfo">
          <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-600 to-violet-800 flex items-center justify-center" aria-hidden="true">
                <Ship className="w-4 h-4 text-white" aria-hidden="true" />
              </div>
              <span className="font-semibold">ExportFlow</span>
            </div>
            
            <nav className="flex items-center gap-6 text-sm text-zinc-400" aria-label="Footer navigation">
              <a href="/privacy" className="hover:text-white transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-500 rounded">Privacy</a>
              <a href="/terms" className="hover:text-white transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-500 rounded">Terms</a>
              <a href="/support" className="hover:text-white transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-500 rounded">Support</a>
            </nav>
            
            <p className="text-sm text-zinc-400">
              © 2026 ExportFlow. Made in India.
            </p>
          </div>
        </footer>
      </div>
    </>
  );
}