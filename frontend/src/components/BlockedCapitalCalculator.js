import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Calculator, TrendingUp, ArrowRight } from 'lucide-react';
import { Button } from './ui/button';
import { useNavigate } from 'react-router-dom';

const BlockedCapitalCalculator = () => {
  const navigate = useNavigate();
  const [monthlyExports, setMonthlyExports] = useState(50);
  const [paymentDelay, setPaymentDelay] = useState(45);
  const [incentivePercent, setIncentivePercent] = useState(2);

  const blockedCapital = useMemo(() => {
    // Blocked receivables = monthly exports * (payment delay / 30)
    const blockedReceivables = (monthlyExports * paymentDelay) / 30;
    // Blocked incentives = monthly exports * incentive% * (delay / 30)
    const blockedIncentives = (monthlyExports * (incentivePercent / 100) * paymentDelay) / 30;
    // GST blocked (assumed 18% GST on portion, delayed refund)
    const gstBlocked = (monthlyExports * 0.18 * 0.5); // 50% exportable GST blocked
    
    return {
      receivables: blockedReceivables,
      incentives: blockedIncentives,
      gst: gstBlocked,
      total: blockedReceivables + blockedIncentives + gstBlocked,
    };
  }, [monthlyExports, paymentDelay, incentivePercent]);

  const formatCurrency = (value) => {
    if (value >= 100) {
      return `₹${(value / 100).toFixed(1)}Cr`;
    }
    return `₹${value.toFixed(1)}L`;
  };

  return (
    <section className="py-20 px-4 sm:px-6 relative" id="calculator">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-400 text-sm mb-6">
            <Calculator className="w-4 h-4" />
            Capital Calculator
          </div>
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-white mb-4">
            How much export capital is blocked?
          </h2>
          <p className="text-zinc-400 max-w-xl mx-auto">
            Estimate how much of your working capital is tied up in pending payments, refunds, and incentives.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="bg-zinc-900/50 backdrop-blur-sm border border-zinc-800 rounded-2xl p-6 sm:p-8"
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {/* Monthly Exports Input */}
            <div className="space-y-3">
              <label className="text-sm text-zinc-400">Monthly Exports (₹ Lakhs)</label>
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-500">₹</span>
                <input
                  type="number"
                  value={monthlyExports}
                  onChange={(e) => setMonthlyExports(Math.max(0, Number(e.target.value)))}
                  className="w-full bg-zinc-800/50 border border-zinc-700 rounded-xl pl-8 pr-4 py-3 text-white focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition-colors"
                  placeholder="50"
                />
                <span className="absolute right-4 top-1/2 -translate-y-1/2 text-zinc-500 text-sm">L</span>
              </div>
            </div>

            {/* Payment Delay Input */}
            <div className="space-y-3">
              <label className="text-sm text-zinc-400">Avg Payment Delay (Days)</label>
              <select
                value={paymentDelay}
                onChange={(e) => setPaymentDelay(Number(e.target.value))}
                className="w-full bg-zinc-800/50 border border-zinc-700 rounded-xl px-4 py-3 text-white focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition-colors appearance-none cursor-pointer"
              >
                <option value={30}>30 days</option>
                <option value={45}>45 days</option>
                <option value={60}>60 days</option>
                <option value={90}>90 days</option>
                <option value={120}>120 days</option>
              </select>
            </div>

            {/* Incentive Percent Input */}
            <div className="space-y-3">
              <label className="text-sm text-zinc-400">Export Incentives (%)</label>
              <select
                value={incentivePercent}
                onChange={(e) => setIncentivePercent(Number(e.target.value))}
                className="w-full bg-zinc-800/50 border border-zinc-700 rounded-xl px-4 py-3 text-white focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition-colors appearance-none cursor-pointer"
              >
                <option value={1}>1%</option>
                <option value={2}>2%</option>
                <option value={3}>3%</option>
                <option value={4}>4%</option>
                <option value={5}>5%</option>
              </select>
            </div>
          </div>

          {/* Results */}
          <div className="bg-zinc-800/30 rounded-xl p-6 mb-6">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="w-5 h-5 text-violet-400" />
              <span className="text-sm text-zinc-400">Estimated Blocked Capital</span>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <p className="text-xs text-zinc-500 mb-1">Receivables</p>
                <p className="text-lg font-semibold text-amber-400">
                  {formatCurrency(blockedCapital.receivables)}
                </p>
              </div>
              <div className="text-center">
                <p className="text-xs text-zinc-500 mb-1">Incentives</p>
                <p className="text-lg font-semibold text-emerald-400">
                  {formatCurrency(blockedCapital.incentives)}
                </p>
              </div>
              <div className="text-center">
                <p className="text-xs text-zinc-500 mb-1">GST Refunds</p>
                <p className="text-lg font-semibold text-blue-400">
                  {formatCurrency(blockedCapital.gst)}
                </p>
              </div>
              <div className="text-center border-l border-zinc-700 pl-4">
                <p className="text-xs text-zinc-500 mb-1">Total Blocked</p>
                <motion.p 
                  key={blockedCapital.total}
                  initial={{ scale: 1.1, color: '#A78BFA' }}
                  animate={{ scale: 1, color: '#FFFFFF' }}
                  className="text-2xl font-bold text-white"
                >
                  {formatCurrency(blockedCapital.total)}
                </motion.p>
              </div>
            </div>
          </div>

          {/* CTA */}
          <div className="text-center">
            <Button
              onClick={() => navigate('/register')}
              className="bg-gradient-to-r from-violet-600 to-violet-700 hover:from-violet-500 hover:to-violet-600 text-white px-8 py-6 text-base rounded-xl shadow-lg shadow-violet-500/20"
            >
              Track this in ExportFlow
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
            <p className="text-xs text-zinc-500 mt-3">Free for first 5 shipments • No credit card</p>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default BlockedCapitalCalculator;
