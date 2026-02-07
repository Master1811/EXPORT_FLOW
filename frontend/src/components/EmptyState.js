import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { 
  Package, CreditCard, TrendingUp, Plus, Sparkles, 
  ArrowRight, Ship, FileText, Calculator
} from 'lucide-react';

const EmptyState = ({ 
  type = 'shipments',
  onAction,
  title,
  description,
  actionLabel,
  icon: CustomIcon
}) => {
  const navigate = useNavigate();
  
  const configs = {
    shipments: {
      icon: Package,
      title: "No Shipments Yet",
      description: "Start by adding your first export shipment to track documents, payments, and compliance in one place.",
      actionLabel: "Create First Shipment",
      tips: [
        "Track shipment status from draft to delivered",
        "Monitor e-BRC deadlines automatically",
        "Get alerts for compliance requirements"
      ],
      color: "primary"
    },
    payments: {
      icon: CreditCard,
      title: "No Payments Recorded",
      description: "Once you have shipments, record payments to track receivables and aging analysis.",
      actionLabel: "Go to Shipments",
      tips: [
        "Track payment aging (0-30, 30-60, 60-90+ days)",
        "Visualize outstanding receivables",
        "Get alerts for overdue payments"
      ],
      color: "amber",
      navigateTo: "/shipments"
    },
    incentives: {
      icon: TrendingUp,
      title: "No Incentives Data",
      description: "Add shipments with HS codes to automatically calculate RoDTEP, RoSCTL, and Drawback incentives.",
      actionLabel: "Add Shipments",
      tips: [
        "Automatic incentive calculation based on HS codes",
        "Track claimed vs unclaimed benefits",
        "Never leave money on the table again"
      ],
      color: "neon",
      navigateTo: "/shipments"
    },
    dashboard: {
      icon: Ship,
      title: "Welcome to ExportFlow!",
      description: "Get started by adding your export shipments to unlock powerful insights and automation.",
      actionLabel: "Create First Shipment",
      tips: [
        "Dashboard shows export trends and payment status",
        "AI-powered risk alerts and recommendations",
        "Track incentives and GST refunds automatically"
      ],
      color: "primary",
      navigateTo: "/shipments"
    }
  };
  
  const config = configs[type] || configs.shipments;
  const Icon = CustomIcon || config.icon;
  const colorClasses = {
    primary: "from-primary/20 to-primary/5 border-primary/30 text-primary",
    amber: "from-amber/20 to-amber/5 border-amber/30 text-amber",
    neon: "from-neon/20 to-neon/5 border-neon/30 text-neon"
  };
  
  const handleAction = () => {
    if (onAction) {
      onAction();
    } else if (config.navigateTo) {
      navigate(config.navigateTo);
    }
  };
  
  return (
    <Card className={`bg-gradient-to-br ${colorClasses[config.color]} border`} data-testid={`empty-state-${type}`}>
      <CardContent className="p-8 md:p-12">
        <div className="flex flex-col items-center text-center max-w-lg mx-auto">
          {/* Icon */}
          <div className={`w-20 h-20 rounded-2xl bg-${config.color}/10 flex items-center justify-center mb-6`}>
            <Icon className={`w-10 h-10 text-${config.color}`} />
          </div>
          
          {/* Title & Description */}
          <h2 className="font-heading text-2xl md:text-3xl text-foreground mb-3">
            {title || config.title}
          </h2>
          <p className="text-muted-foreground text-lg mb-6">
            {description || config.description}
          </p>
          
          {/* Tips */}
          <div className="w-full bg-background/50 rounded-lg p-4 mb-6">
            <p className="text-sm font-medium text-foreground mb-3 flex items-center justify-center gap-2">
              <Sparkles className="w-4 h-4 text-amber" />
              What you'll unlock
            </p>
            <ul className="space-y-2 text-sm text-muted-foreground text-left">
              {config.tips.map((tip, index) => (
                <li key={index} className="flex items-start gap-2">
                  <ArrowRight className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>{tip}</span>
                </li>
              ))}
            </ul>
          </div>
          
          {/* CTA Button */}
          <Button 
            size="lg" 
            className={`bg-${config.color} hover:bg-${config.color}/90`}
            onClick={handleAction}
            data-testid={`empty-state-${type}-action-btn`}
          >
            <Plus className="w-4 h-4 mr-2" />
            {actionLabel || config.actionLabel}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default EmptyState;
