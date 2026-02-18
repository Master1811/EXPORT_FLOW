import React, { useState, useEffect, useMemo, lazy, Suspense } from 'react';
import { motion, useInView, AnimatePresence } from 'framer-motion';
import { useNavigate, Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { 
  ArrowRight, Shield, Clock, TrendingUp, 
  CheckCircle, Sparkles, ChevronRight, Users,
  Mail, Building, MessageSquare, Send, Loader2,
  BarChart3, Calculator, Wallet, Bell, FileText,
  CreditCard, PieChart, Target, Zap, Star, Quote
} from 'lucide-react';
import { toast } from 'sonner';
import ScrollSyncHero from '../components/ScrollSyncHero';
import BlockedCapitalCalculator from '../components/BlockedCapitalCalculator';
import { SkeletonCard, PageTransition, FadeSlide } from '../components/Skeleton';

// Animation variants
const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: 'easeOut' } }
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
};

// Navbar Component
const Navbar = () => {
  const navigate = useNavigate();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled ? 'bg-[#09090B]/90 backdrop-blur-lg border-b border-zinc-800' : 'bg-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <div className="w-9 h-9 bg-violet-600 rounded-lg flex items-center justify-center">
              <Wallet className="w-5 h-5 text-white" />
            </div>
            <span className="font-semibold text-white">Export<span className="text-violet-400">Flow</span></span>
          </Link>

          {/* Nav Links - Desktop */}
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-sm text-zinc-400 hover:text-white transition-colors">Features</a>
            <a href="#calculator" className="text-sm text-zinc-400 hover:text-white transition-colors">Calculator</a>
            <a href="#pricing" className="text-sm text-zinc-400 hover:text-white transition-colors">Pricing</a>
            <a href="#about" className="text-sm text-zinc-400 hover:text-white transition-colors">About</a>
          </div>

          {/* Auth Buttons */}
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              onClick={() => navigate('/login')}
              className="text-zinc-300 hover:text-white"
            >
              Sign In
            </Button>
            <Button
              onClick={() => navigate('/register')}
              className="bg-violet-600 hover:bg-violet-500 text-white"
            >
              Get Started
            </Button>
          </div>
        </div>
      </div>
    </motion.nav>
  );
};

// How It Works Section
const HowItWorksSection = () => {
  const steps = [
    {
      number: '01',
      title: 'Add Shipments',
      description: 'Log export invoices, buyers, and shipping details in minutes.',
      icon: FileText,
      color: 'violet',
    },
    {
      number: '02',
      title: 'Track Capital',
      description: 'Monitor payments, GST refunds, and incentives in real-time.',
      icon: BarChart3,
      color: 'blue',
    },
    {
      number: '03',
      title: 'Recover Money',
      description: 'Get alerts on aging receivables and unclaimed benefits.',
      icon: Wallet,
      color: 'emerald',
    },
  ];

  return (
    <section className="py-24 px-4 sm:px-6" id="how-it-works">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeInUp}
          className="text-center mb-16"
        >
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-white mb-4">
            How ExportFlow Works
          </h2>
          <p className="text-zinc-400 max-w-xl mx-auto">
            Three simple steps to visibility over your export finances.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {steps.map((step, index) => (
            <motion.div
              key={step.number}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.15 }}
              className="relative group"
            >
              {/* Connection line */}
              {index < 2 && (
                <div className="hidden md:block absolute top-12 left-full w-full h-[2px] bg-gradient-to-r from-zinc-700 to-transparent z-0" />
              )}
              
              <div className="relative bg-zinc-900/50 border border-zinc-800 rounded-2xl p-8 hover:border-zinc-700 transition-colors">
                <div className={`w-14 h-14 rounded-xl bg-${step.color}-500/10 border border-${step.color}-500/20 flex items-center justify-center mb-6`}>
                  <step.icon className={`w-7 h-7 text-${step.color}-400`} />
                </div>
                <span className="text-xs text-zinc-600 font-mono">{step.number}</span>
                <h3 className="text-xl font-semibold text-white mt-2 mb-3">{step.title}</h3>
                <p className="text-zinc-400 text-sm leading-relaxed">{step.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Features Section
const FeaturesSection = () => {
  const features = [
    {
      title: 'Receivable Aging',
      description: 'Track payment delays by buyer and take action before capital gets blocked.',
      icon: Clock,
      color: 'amber',
    },
    {
      title: 'Incentive Tracker',
      description: 'Never miss RoDTEP, RoSCTL, or duty drawback claims on your exports.',
      icon: Target,
      color: 'emerald',
    },
    {
      title: 'GST Refund Monitor',
      description: 'Track GST refund status and pending IGST claims in one place.',
      icon: CreditCard,
      color: 'blue',
    },
    {
      title: 'Capital Insights',
      description: 'AI-powered alerts on blocked capital and recovery opportunities.',
      icon: Zap,
      color: 'violet',
    },
  ];

  return (
    <section className="py-24 px-4 sm:px-6 bg-gradient-to-b from-transparent via-zinc-900/30 to-transparent" id="features">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeInUp}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-400 text-sm mb-6">
            <Sparkles className="w-4 h-4" />
            Core Features
          </div>
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-white mb-4">
            Export Finance Visibility
          </h2>
          <p className="text-zinc-400 max-w-xl mx-auto">
            Everything you need to track, analyze, and recover your export capital.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className="bg-zinc-900/40 border border-zinc-800 rounded-xl p-6 hover:border-zinc-700 transition-all group"
            >
              <div className={`w-12 h-12 rounded-lg bg-${feature.color}-500/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                <feature.icon className={`w-6 h-6 text-${feature.color}-400`} />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
              <p className="text-sm text-zinc-400 leading-relaxed">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Trust Section
const TrustSection = () => {
  const trustItems = [
    { icon: Shield, label: 'Bank-grade Security', desc: 'AES-256 encryption' },
    { icon: Building, label: 'Indian Data Residency', desc: 'Data stays in India' },
    { icon: CheckCircle, label: 'ISO 27001', desc: 'Certified compliant' },
  ];

  return (
    <section className="py-16 px-4 sm:px-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex flex-wrap justify-center gap-8 md:gap-16">
          {trustItems.map((item, index) => (
            <motion.div
              key={item.label}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className="flex items-center gap-3 text-center"
            >
              <div className="w-10 h-10 rounded-lg bg-zinc-800 flex items-center justify-center">
                <item.icon className="w-5 h-5 text-zinc-400" />
              </div>
              <div className="text-left">
                <p className="text-sm font-medium text-white">{item.label}</p>
                <p className="text-xs text-zinc-500">{item.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Testimonials Section
const TestimonialsSection = () => {
  const testimonials = [
    {
      quote: "ExportFlow helped us recover ₹12L in missed incentives in the first month. Now we track everything.",
      author: "Rajesh Kumar",
      role: "CFO, Brass Exports Ltd",
      avatar: "RK",
    },
    {
      quote: "Finally, visibility into our blocked capital. We reduced receivable aging by 40% in 3 months.",
      author: "Priya Sharma",
      role: "Finance Head, TextileCo",
      avatar: "PS",
    },
    {
      quote: "The GST refund tracking alone saved us hours every week. Highly recommend for any exporter.",
      author: "Amit Patel",
      role: "MD, Handicrafts Hub",
      avatar: "AP",
    },
  ];

  return (
    <section className="py-24 px-4 sm:px-6 bg-gradient-to-b from-transparent via-violet-950/10 to-transparent">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeInUp}
          className="text-center mb-16"
        >
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-white mb-4">
            Trusted by Exporters
          </h2>
          <p className="text-zinc-400">
            See what finance teams say about ExportFlow.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.15 }}
              className="bg-zinc-900/40 border border-zinc-800 rounded-2xl p-6"
            >
              <Quote className="w-8 h-8 text-violet-500/30 mb-4" />
              <p className="text-zinc-300 mb-6 leading-relaxed">"{testimonial.quote}"</p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-violet-600/20 flex items-center justify-center text-violet-400 text-sm font-medium">
                  {testimonial.avatar}
                </div>
                <div>
                  <p className="text-sm font-medium text-white">{testimonial.author}</p>
                  <p className="text-xs text-zinc-500">{testimonial.role}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Pricing Section
const PricingSection = () => {
  const plans = [
    {
      name: 'Starter',
      price: 'Free',
      period: 'forever',
      description: 'For small exporters getting started',
      features: ['Up to 5 shipments/month', 'Basic receivable tracking', 'GST refund calculator', 'Email support'],
      cta: 'Get Started Free',
      popular: false,
    },
    {
      name: 'Professional',
      price: '₹2,999',
      period: '/month',
      description: 'For growing export businesses',
      features: ['Unlimited shipments', 'Full incentive tracker', 'Receivable aging alerts', 'Capital insights AI', 'Priority support'],
      cta: 'Start 14-Day Trial',
      popular: true,
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      period: '',
      description: 'For large export houses',
      features: ['Everything in Pro', 'Multi-user access', 'API integrations', 'Custom reports', 'Dedicated manager', 'SLA guarantee'],
      cta: 'Contact Sales',
      popular: false,
    },
  ];

  const navigate = useNavigate();

  return (
    <section className="py-24 px-4 sm:px-6" id="pricing">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeInUp}
          className="text-center mb-16"
        >
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-white mb-4">
            Simple, <span className="text-violet-400">Transparent</span> Pricing
          </h2>
          <p className="text-zinc-400">
            Start free. Scale as you grow. No hidden fees.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {plans.map((plan, index) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className={`relative bg-zinc-900/40 border rounded-2xl p-6 ${
                plan.popular ? 'border-violet-500/50' : 'border-zinc-800'
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-violet-600 text-white text-xs font-medium rounded-full">
                  Most Popular
                </div>
              )}
              <h3 className="text-xl font-semibold text-white mb-1">{plan.name}</h3>
              <p className="text-sm text-zinc-500 mb-4">{plan.description}</p>
              <div className="mb-6">
                <span className="text-3xl font-bold text-white">{plan.price}</span>
                <span className="text-zinc-400 text-sm">{plan.period}</span>
              </div>
              <ul className="space-y-3 mb-6">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-2 text-sm text-zinc-300">
                    <CheckCircle className="w-4 h-4 text-emerald-500 flex-shrink-0" />
                    {feature}
                  </li>
                ))}
              </ul>
              <Button
                onClick={() => navigate(plan.name === 'Enterprise' ? '#contact' : '/register')}
                className={`w-full ${
                  plan.popular
                    ? 'bg-violet-600 hover:bg-violet-500 text-white'
                    : 'bg-zinc-800 hover:bg-zinc-700 text-white'
                }`}
              >
                {plan.cta}
              </Button>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Final CTA Section
const FinalCTASection = () => {
  const navigate = useNavigate();

  return (
    <section className="py-24 px-4 sm:px-6">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="bg-gradient-to-br from-violet-600/20 to-blue-600/20 border border-violet-500/20 rounded-3xl p-8 sm:p-12 text-center"
        >
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-white mb-4">
            Stop losing money in blind spots
          </h2>
          <p className="text-zinc-300 mb-8 max-w-xl mx-auto">
            Join hundreds of Indian exporters who now have complete visibility over their export finances.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              size="lg"
              onClick={() => navigate('/register')}
              className="bg-white text-violet-900 hover:bg-zinc-100 px-8 py-6 text-base font-semibold"
            >
              Track My Capital
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
            <Button
              size="lg"
              variant="outline"
              onClick={() => navigate('/login')}
              className="border-white/30 text-white hover:bg-white/10 px-8 py-6"
            >
              See Demo
            </Button>
          </div>
          <p className="text-xs text-zinc-400 mt-4">
            Free forever for up to 5 shipments • No credit card required
          </p>
        </motion.div>
      </div>
    </section>
  );
};

// Footer Component
const Footer = () => {
  return (
    <footer className="border-t border-zinc-800 py-12 px-4 sm:px-6">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-violet-600 rounded-lg flex items-center justify-center">
                <Wallet className="w-4 h-4 text-white" />
              </div>
              <span className="font-semibold text-white">ExportFlow</span>
            </div>
            <p className="text-sm text-zinc-500">
              Export finance visibility for Indian exporters.
            </p>
          </div>
          <div>
            <h4 className="text-sm font-medium text-white mb-4">Product</h4>
            <ul className="space-y-2 text-sm text-zinc-400">
              <li><a href="#features" className="hover:text-white transition-colors">Features</a></li>
              <li><a href="#pricing" className="hover:text-white transition-colors">Pricing</a></li>
              <li><a href="#calculator" className="hover:text-white transition-colors">Calculator</a></li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-medium text-white mb-4">Company</h4>
            <ul className="space-y-2 text-sm text-zinc-400">
              <li><a href="#about" className="hover:text-white transition-colors">About</a></li>
              <li><a href="#contact" className="hover:text-white transition-colors">Contact</a></li>
              <li><a href="/blog" className="hover:text-white transition-colors">Blog</a></li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-medium text-white mb-4">Legal</h4>
            <ul className="space-y-2 text-sm text-zinc-400">
              <li><a href="/privacy" className="hover:text-white transition-colors">Privacy Policy</a></li>
              <li><a href="/terms" className="hover:text-white transition-colors">Terms of Service</a></li>
            </ul>
          </div>
        </div>
        <div className="pt-8 border-t border-zinc-800 flex flex-col sm:flex-row justify-between items-center gap-4">
          <p className="text-xs text-zinc-500">
            © {new Date().getFullYear()} ExportFlow. All rights reserved.
          </p>
          <p className="text-xs text-zinc-500">
            Made with care for Indian exporters
          </p>
        </div>
      </div>
    </footer>
  );
};

// Main Landing Page Component
export default function LandingPage() {
  const navigate = useNavigate();
  const [activeIndustry, setActiveIndustry] = useState('brass');

  return (
    <PageTransition>
      <Helmet>
        <title>ExportFlow - Export Finance Visibility for Indian Exporters</title>
        <meta name="description" content="Track pending payments, GST refunds, and export incentives in one view. Export finance intelligence for Indian exporters." />
      </Helmet>

      <div className="min-h-screen bg-[#09090B] text-white">
        <Navbar />

        {/* Hero Section */}
        <ScrollSyncHero
          onIndustryChange={setActiveIndustry}
          initialIndustry="brass"
        >
          <div className="max-w-4xl mx-auto text-center">
            {/* CTAs */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center mt-8">
              <Button
                size="lg"
                onClick={() => navigate('/register')}
                className="bg-violet-600 hover:bg-violet-500 text-white px-8 py-6 text-base rounded-xl shadow-lg shadow-violet-500/20"
              >
                Track My Capital
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
              <Button
                size="lg"
                variant="outline"
                onClick={() => navigate('/login')}
                className="border-zinc-700 text-white hover:bg-zinc-800 px-8 py-6"
              >
                See Demo
              </Button>
            </div>
          </div>
        </ScrollSyncHero>

        {/* Blocked Capital Calculator */}
        <BlockedCapitalCalculator />

        {/* How It Works */}
        <HowItWorksSection />

        {/* Features */}
        <FeaturesSection />

        {/* Trust */}
        <TrustSection />

        {/* Testimonials */}
        <TestimonialsSection />

        {/* Pricing */}
        <PricingSection />

        {/* Final CTA */}
        <FinalCTASection />

        {/* Footer */}
        <Footer />
      </div>
    </PageTransition>
  );
}
