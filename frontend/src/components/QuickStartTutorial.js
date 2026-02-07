import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Progress } from '../components/ui/progress';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter
} from '../components/ui/dialog';
import {
  Ship, CreditCard, TrendingUp, CheckCircle, ArrowRight, ArrowLeft,
  Sparkles, Package, X, Rocket, Target, Zap
} from 'lucide-react';

const TUTORIAL_STEPS = [
  {
    id: 'welcome',
    title: 'Welcome to ExportFlow!',
    description: 'Let\'s get you started in 3 simple steps. We\'ll help you set up your first shipment and show you how to track payments and incentives.',
    icon: Rocket,
    color: 'violet',
    content: null
  },
  {
    id: 'shipment',
    title: 'Step 1: Create Your First Shipment',
    description: 'Enter basic shipment details to start tracking your export.',
    icon: Ship,
    color: 'blue',
    fields: [
      { name: 'shipment_number', label: 'Shipment Number', placeholder: 'SHP-2024-001', required: true },
      { name: 'buyer_name', label: 'Buyer Name', placeholder: 'ABC Trading Co.', required: true },
      { name: 'buyer_country', label: 'Destination Country', placeholder: 'USA', required: true },
      { name: 'total_value', label: 'FOB Value (₹)', placeholder: '500000', type: 'number', required: true }
    ]
  },
  {
    id: 'payment',
    title: 'Step 2: Record Expected Payment',
    description: 'Set up payment tracking to monitor your receivables.',
    icon: CreditCard,
    color: 'emerald',
    fields: [
      { name: 'expected_payment_date', label: 'Expected Payment Date', type: 'date', required: true },
      { name: 'payment_terms', label: 'Payment Terms', placeholder: 'LC at Sight / 30 Days', required: false }
    ]
  },
  {
    id: 'incentives',
    title: 'Step 3: Check Your Incentives',
    description: 'Add HS code to see eligible export incentives.',
    icon: TrendingUp,
    color: 'amber',
    fields: [
      { name: 'hs_code', label: 'HS Code (8-digit)', placeholder: '74181020', required: false }
    ],
    tip: 'Tip: Moradabad handicrafts like brass/copper items have RoDTEP rates of 0.5% - 2.5%'
  },
  {
    id: 'complete',
    title: 'You\'re All Set!',
    description: 'Your first shipment is created. Explore the dashboard to see your export insights.',
    icon: CheckCircle,
    color: 'green',
    content: null
  }
];

export default function QuickStartTutorial({ open, onClose, onComplete }) {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({});
  const [loading, setLoading] = useState(false);
  const [completed, setCompleted] = useState(false);

  const step = TUTORIAL_STEPS[currentStep];
  const progress = ((currentStep) / (TUTORIAL_STEPS.length - 1)) * 100;
  const isFirstStep = currentStep === 0;
  const isLastStep = currentStep === TUTORIAL_STEPS.length - 1;
  const hasFields = step.fields && step.fields.length > 0;

  const handleInputChange = (name, value) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const validateStep = () => {
    if (!hasFields) return true;
    return step.fields.filter(f => f.required).every(f => formData[f.name]);
  };

  const handleNext = async () => {
    if (!validateStep()) return;

    if (currentStep === TUTORIAL_STEPS.length - 2) {
      // Last content step - create shipment
      setLoading(true);
      try {
        // Simulated API call - in real app, call api.post('/shipments', formData)
        await new Promise(resolve => setTimeout(resolve, 1000));
        setCompleted(true);
        setCurrentStep(currentStep + 1);
      } catch (error) {
        console.error('Failed to create shipment:', error);
      } finally {
        setLoading(false);
      }
    } else {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleFinish = () => {
    onComplete?.();
    onClose();
    navigate('/shipments');
  };

  const handleSkip = () => {
    localStorage.setItem('quickstart_skipped', 'true');
    onClose();
  };

  const StepIcon = step.icon;
  const colorMap = {
    violet: 'from-violet-500/20 to-violet-600/5 border-violet-500/30 text-violet-400',
    blue: 'from-blue-500/20 to-blue-600/5 border-blue-500/30 text-blue-400',
    emerald: 'from-emerald-500/20 to-emerald-600/5 border-emerald-500/30 text-emerald-400',
    amber: 'from-amber-500/20 to-amber-600/5 border-amber-500/30 text-amber-400',
    green: 'from-green-500/20 to-green-600/5 border-green-500/30 text-green-400'
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-lg bg-zinc-900 border-zinc-800 p-0 overflow-hidden" data-testid="quickstart-dialog">
        {/* Progress Bar */}
        <div className="h-1 bg-zinc-800">
          <div 
            className="h-full bg-gradient-to-r from-violet-500 to-blue-500 transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* Header with step indicator */}
        <div className="px-6 pt-6 pb-2 flex items-center justify-between">
          <div className="flex items-center gap-2">
            {TUTORIAL_STEPS.slice(0, -1).map((s, i) => (
              <div 
                key={s.id}
                className={`w-2 h-2 rounded-full transition-colors ${
                  i < currentStep ? 'bg-green-500' : 
                  i === currentStep ? 'bg-violet-500' : 'bg-zinc-700'
                }`}
              />
            ))}
          </div>
          <Button variant="ghost" size="icon" onClick={handleSkip} className="text-zinc-500 hover:text-zinc-300">
            <X className="w-4 h-4" />
          </Button>
        </div>

        {/* Content */}
        <div className="px-6 pb-6">
          {/* Icon */}
          <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${colorMap[step.color]} flex items-center justify-center mb-6 mx-auto`}>
            <StepIcon className="w-8 h-8" />
          </div>

          {/* Title & Description */}
          <div className="text-center mb-6">
            <h2 className="text-2xl font-bold text-white mb-2">{step.title}</h2>
            <p className="text-zinc-400">{step.description}</p>
          </div>

          {/* Form Fields */}
          {hasFields && (
            <div className="space-y-4 mb-6">
              {step.fields.map(field => (
                <div key={field.name} className="space-y-2">
                  <Label className="text-zinc-300">{field.label}</Label>
                  <Input
                    type={field.type || 'text'}
                    placeholder={field.placeholder}
                    value={formData[field.name] || ''}
                    onChange={(e) => handleInputChange(field.name, e.target.value)}
                    className="bg-zinc-800 border-zinc-700 text-white placeholder:text-zinc-500"
                    data-testid={`quickstart-${field.name}`}
                  />
                </div>
              ))}
              {step.tip && (
                <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20">
                  <p className="text-sm text-amber-300 flex items-start gap-2">
                    <Sparkles className="w-4 h-4 mt-0.5 flex-shrink-0" />
                    {step.tip}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Welcome Step Content */}
          {step.id === 'welcome' && (
            <div className="grid grid-cols-3 gap-3 mb-6">
              {[
                { icon: Ship, label: 'Track Shipments', color: 'blue' },
                { icon: CreditCard, label: 'Monitor Payments', color: 'emerald' },
                { icon: TrendingUp, label: 'Optimize Incentives', color: 'amber' }
              ].map((item, i) => (
                <div key={i} className={`p-4 rounded-xl bg-${item.color}-500/10 border border-${item.color}-500/20 text-center`}>
                  <item.icon className={`w-6 h-6 text-${item.color}-400 mx-auto mb-2`} />
                  <p className="text-xs text-zinc-400">{item.label}</p>
                </div>
              ))}
            </div>
          )}

          {/* Complete Step Content */}
          {step.id === 'complete' && (
            <div className="space-y-4 mb-6">
              <div className="p-4 rounded-xl bg-green-500/10 border border-green-500/20">
                <div className="flex items-center gap-3">
                  <CheckCircle className="w-6 h-6 text-green-400" />
                  <div>
                    <p className="font-medium text-white">Shipment Created!</p>
                    <p className="text-sm text-zinc-400">You can now track it in your dashboard</p>
                  </div>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-lg bg-zinc-800 border border-zinc-700">
                  <Target className="w-5 h-5 text-violet-400 mb-2" />
                  <p className="text-sm text-white">Track e-BRC deadlines</p>
                </div>
                <div className="p-3 rounded-lg bg-zinc-800 border border-zinc-700">
                  <Zap className="w-5 h-5 text-amber-400 mb-2" />
                  <p className="text-sm text-white">Auto-calculate incentives</p>
                </div>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3">
            {!isFirstStep && !isLastStep && (
              <Button variant="outline" onClick={handlePrev} className="flex-1 border-zinc-700 hover:bg-zinc-800">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
            )}
            
            {isFirstStep && (
              <Button variant="outline" onClick={handleSkip} className="flex-1 border-zinc-700 hover:bg-zinc-800">
                Skip Tutorial
              </Button>
            )}

            {isLastStep ? (
              <Button onClick={handleFinish} className="flex-1 bg-green-600 hover:bg-green-700">
                Go to Dashboard
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            ) : (
              <Button 
                onClick={handleNext} 
                disabled={loading || (hasFields && !validateStep())}
                className="flex-1 bg-violet-600 hover:bg-violet-700"
              >
                {loading ? 'Creating...' : currentStep === TUTORIAL_STEPS.length - 2 ? 'Create Shipment' : 'Continue'}
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
