import React, { useEffect, useRef, useState } from 'react';
import { motion, useInView, useScroll, useTransform } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { 
  Factory, Ship, Landmark, ArrowRight, Shield, Eye, Lock, 
  Database, FileCheck, TrendingUp, Clock, AlertTriangle, 
  IndianRupee, CheckCircle, Sparkles, ChevronDown
} from 'lucide-react';

// Animation variants
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
const ExportJourney = () => {
  const [activeStep, setActiveStep] = useState(0);
  const steps = [
    { icon: Factory, label: 'Factory', color: '#7C3AED', desc: 'Invoice created & shipment logged' },
    { icon: Ship, label: 'Port', color: '#3B82F6', desc: 'Documents secured & compliance tracked' },
    { icon: Landmark, label: 'Bank', color: '#10B981', desc: 'Payments reconciled & incentives recovered' }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev + 1) % 3);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="relative w-full max-w-4xl mx-auto">
      {/* Connection Line */}
      <div className="absolute top-1/2 left-0 right-0 h-1 bg-gradient-to-r from-violet-600/20 via-blue-500/20 to-emerald-500/20 -translate-y-1/2 hidden md:block" />
      
      {/* Progress Line */}
      <motion.div 
        className="absolute top-1/2 left-0 h-1 bg-gradient-to-r from-violet-600 via-blue-500 to-emerald-500 -translate-y-1/2 hidden md:block"
        initial={{ width: '0%' }}
        animate={{ width: `${(activeStep + 1) * 33.33}%` }}
        transition={{ duration: 0.8, ease: 'easeInOut' }}
      />
      
      <div className="flex flex-col md:flex-row justify-between items-center gap-8 md:gap-4">
        {steps.map((step, index) => {
          const Icon = step.icon;
          const isActive = index <= activeStep;
          
          return (
            <motion.div
              key={step.label}
              className="relative flex flex-col items-center cursor-pointer group"
              onClick={() => setActiveStep(index)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {/* Glow Effect */}
              <motion.div
                className="absolute inset-0 rounded-full blur-xl opacity-0 group-hover:opacity-50 transition-opacity"
                style={{ backgroundColor: step.color }}
                animate={isActive ? { opacity: 0.3, scale: 1.2 } : { opacity: 0, scale: 1 }}
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
                />
                
                {/* Floating coin animation */}
                {index === 2 && isActive && (
                  <motion.div
                    className="absolute -top-2 -right-2"
                    initial={{ scale: 0, rotate: -180 }}
                    animate={{ scale: 1, rotate: 0 }}
                    transition={{ delay: 0.3, type: 'spring', stiffness: 200 }}
                  >
                    <div className="w-8 h-8 rounded-full bg-emerald-500 flex items-center justify-center">
                      <IndianRupee className="w-4 h-4 text-white" />
                    </div>
                  </motion.div>
                )}
              </motion.div>
              
              {/* Label */}
              <motion.p 
                className={`mt-4 font-medium text-lg ${isActive ? 'text-white' : 'text-zinc-500'}`}
                animate={isActive ? { y: 0 } : { y: 5 }}
              >
                {step.label}
              </motion.p>
              
              {/* Description */}
              <motion.p 
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
};

// Problem Card Component
const ProblemCard = ({ icon: Icon, title, amount, description, color, delay }) => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });
  
  return (
    <motion.div
      ref={ref}
      initial="hidden"
      animate={isInView ? 'visible' : 'hidden'}
      variants={scaleIn}
      transition={{ delay }}
      className="group relative"
    >
      <div className={`absolute inset-0 bg-gradient-to-br ${color} opacity-0 group-hover:opacity-10 rounded-2xl transition-opacity duration-500`} />
      <div className="relative p-8 rounded-2xl border border-zinc-800 bg-zinc-900/50 backdrop-blur-sm hover:border-zinc-700 transition-all duration-500">
        <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center mb-6`}>
          <Icon className="w-7 h-7 text-white" />
        </div>
        <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
        <p className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-orange-400 mb-3">
          {amount}
        </p>
        <p className="text-zinc-400 leading-relaxed">{description}</p>
      </div>
    </motion.div>
  );
};

// Feature Card Component
const FeatureCard = ({ icon: Icon, title, description, gradient }) => {
  return (
    <motion.div
      whileHover={{ y: -8, scale: 1.02 }}
      transition={{ type: 'spring', stiffness: 300 }}
      className="group relative overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-900/50 p-8 hover:border-violet-500/50 transition-colors duration-500"
    >
      {/* Background gradient on hover */}
      <div className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-500`} />
      
      <div className="relative z-10">
        <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center mb-5`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
        <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
        <p className="text-zinc-400 text-sm leading-relaxed">{description}</p>
      </div>
    </motion.div>
  );
};

// Trust Badge Component
const TrustBadge = ({ icon: Icon, text }) => (
  <motion.div 
    whileHover={{ scale: 1.05 }}
    className="flex items-center gap-3 px-5 py-3 rounded-full border border-zinc-800 bg-zinc-900/50"
  >
    <Icon className="w-5 h-5 text-emerald-400" />
    <span className="text-zinc-300 text-sm">{text}</span>
  </motion.div>
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

  return (
    <div className="min-h-screen bg-[#09090B] text-white overflow-x-hidden">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 px-6 py-4 bg-[#09090B]/80 backdrop-blur-xl border-b border-zinc-800/50">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-600 to-violet-800 flex items-center justify-center">
              <Ship className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight">Export<span className="text-violet-400">Flow</span></span>
          </div>
          
          <div className="flex items-center gap-4">
            <Button 
              variant="ghost" 
              className="text-zinc-400 hover:text-white"
              onClick={() => navigate('/login')}
            >
              Sign In
            </Button>
            <Button 
              className="bg-violet-600 hover:bg-violet-700 text-white px-6"
              onClick={() => navigate('/register')}
            >
              Get Started
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section ref={heroRef} className="relative min-h-screen flex items-center justify-center pt-20 overflow-hidden">
        {/* Gradient Orbs */}
        <div className="absolute top-1/4 left-1/4 w-[600px] h-[600px] bg-violet-600/20 rounded-full blur-[120px] animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] bg-blue-600/10 rounded-full blur-[100px] animate-pulse" style={{ animationDelay: '1s' }} />
        
        <motion.div 
          style={{ opacity: heroOpacity, y: heroY }}
          className="relative z-10 max-w-5xl mx-auto px-6 text-center"
        >
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-violet-500/30 bg-violet-500/10 mb-8"
          >
            <Sparkles className="w-4 h-4 text-violet-400" />
            <span className="text-sm text-violet-300">Built for Indian Exporters</span>
          </motion.div>
          
          {/* Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.8 }}
            className="text-4xl sm:text-5xl lg:text-7xl font-bold leading-tight tracking-tight mb-6"
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
            className="text-lg sm:text-xl text-zinc-400 max-w-2xl mx-auto mb-10 leading-relaxed"
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
              className="bg-gradient-to-r from-violet-600 to-violet-700 hover:from-violet-500 hover:to-violet-600 text-white px-10 py-7 text-lg rounded-xl shadow-lg shadow-violet-500/25 hover:shadow-violet-500/40 transition-all duration-300"
              onClick={() => navigate('/register')}
            >
              Start Recovering Capital
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </motion.div>
          
          {/* Trust Line */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1 }}
            className="mt-8 text-sm text-zinc-500"
          >
            No credit card required • Free for first 5 shipments
          </motion.p>
          
          {/* Scroll Indicator */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.5 }}
            className="absolute bottom-10 left-1/2 -translate-x-1/2"
          >
            <motion.div
              animate={{ y: [0, 10, 0] }}
              transition={{ repeat: Infinity, duration: 2 }}
            >
              <ChevronDown className="w-6 h-6 text-zinc-500" />
            </motion.div>
          </motion.div>
        </motion.div>
      </section>

      {/* Problem Section */}
      <section className="py-24 px-6 relative">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: '-100px' }}
            variants={fadeInUp}
            className="text-center mb-16"
          >
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Where Indian Exporters{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-orange-400">
                Lose Money
              </span>{' '}
              (Silently)
            </h2>
            <p className="text-zinc-400 text-lg max-w-2xl mx-auto">
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
      <section className="py-24 px-6 relative bg-gradient-to-b from-transparent via-violet-950/10 to-transparent">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: '-100px' }}
            variants={fadeInUp}
            className="text-center mb-16"
          >
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              From Shipment to Money —{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-blue-400">
                Visually
              </span>
            </h2>
            <p className="text-zinc-400 text-lg max-w-2xl mx-auto">
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
      <section className="py-24 px-6 relative">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: '-100px' }}
            variants={fadeInUp}
            className="text-center mb-16"
          >
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              What ExportFlow Does{' '}
              <span className="text-zinc-500">(No Noise)</span>
            </h2>
            <p className="text-zinc-400 text-lg">
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
      <section className="py-24 px-6 relative">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: '-100px' }}
            variants={fadeInUp}
            className="text-center mb-12"
          >
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Built for{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-400">
                Trust
              </span>
              , Not Tricks
            </h2>
            <p className="text-zinc-400 text-lg">
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

      {/* Final CTA Section */}
      <section className="py-32 px-6 relative">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-t from-violet-950/30 via-transparent to-transparent" />
        
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
          variants={fadeInUp}
          className="relative z-10 max-w-3xl mx-auto text-center"
        >
          <h2 className="text-3xl sm:text-5xl font-bold mb-6">
            Ready to see your{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-fuchsia-400">
              hidden money
            </span>
            ?
          </h2>
          <p className="text-zinc-400 text-lg mb-10">
            ExportFlow is not accounting software.<br />
            <span className="text-white">It is a money visibility tool for Indian exporters.</span>
          </p>
          
          <Button
            size="lg"
            className="bg-gradient-to-r from-violet-600 to-violet-700 hover:from-violet-500 hover:to-violet-600 text-white px-12 py-7 text-lg rounded-xl shadow-lg shadow-violet-500/25 hover:shadow-violet-500/40 transition-all duration-300"
            onClick={() => navigate('/register')}
          >
            Start Free — No Card Needed
            <ArrowRight className="w-5 h-5 ml-2" />
          </Button>
          
          <p className="mt-6 text-sm text-zinc-500">
            Join 100+ exporters already recovering capital
          </p>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-zinc-800">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-600 to-violet-800 flex items-center justify-center">
              <Ship className="w-4 h-4 text-white" />
            </div>
            <span className="font-semibold">ExportFlow</span>
          </div>
          
          <div className="flex items-center gap-6 text-sm text-zinc-500">
            <a href="#" className="hover:text-white transition-colors">Privacy</a>
            <a href="#" className="hover:text-white transition-colors">Terms</a>
            <a href="#" className="hover:text-white transition-colors">Support</a>
          </div>
          
          <p className="text-sm text-zinc-500">
            © 2025 ExportFlow. Made in India.
          </p>
        </div>
      </footer>
    </div>
  );
}
