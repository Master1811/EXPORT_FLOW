import React, { useRef, useState, useEffect, useCallback } from 'react';
import { motion, useScroll, useTransform, useSpring, AnimatePresence } from 'framer-motion';

// Premium export/logistics images - visually striking cargo and port scenes
const HERO_IMAGES = [
  {
    url: 'https://images.pexels.com/photos/3076002/pexels-photo-3076002.jpeg?auto=compress&cs=tinysrgb&w=1920',
    alt: 'Illuminated aerial view of container terminal at night',
    caption: 'Capital Visibility',
  },
  {
    url: 'https://images.pexels.com/photos/9806482/pexels-photo-9806482.jpeg?auto=compress&cs=tinysrgb&w=1920',
    alt: 'Cargo ship transporting containers across ocean',
    caption: 'Receivable Intelligence',
  },
  {
    url: 'https://images.pexels.com/photos/1624695/pexels-photo-1624695.jpeg?auto=compress&cs=tinysrgb&w=1920',
    alt: 'Colorful shipping containers stacked at port',
    caption: 'Export Finance Tracking',
  },
  {
    url: 'https://images.pexels.com/photos/67563/plane-aircraft-jet-airbase-67563.jpeg?auto=compress&cs=tinysrgb&w=1920',
    alt: 'Cargo plane on tarmac ready for freight',
    caption: 'Smart Finance Analysis',
  },
  {
    url: 'https://images.pexels.com/photos/1427107/pexels-photo-1427107.jpeg?auto=compress&cs=tinysrgb&w=1920',
    alt: 'Port cranes loading containers at dusk',
    caption: 'Capital Recovery',
  },
];

// Industry-specific hero content
const INDUSTRY_CONTENT = {
  brass: {
    headline: 'Stop losing export money in blind spots',
    subheadline: 'Track pending payments, GST refunds, and RoDTEP incentives for your brass exports — in one view.',
    stat: '₹4.2Cr+',
  },
  textile: {
    headline: 'Stop losing textile export margins',
    subheadline: 'Track pending payments, duty drawbacks, and RoSCTL benefits for your textile shipments — in one view.',
    stat: '₹5.8Cr+',
  },
  handicrafts: {
    headline: 'Stop losing handicraft export capital',
    subheadline: 'Track buyer payments, GST refunds, and export incentives for your artisan products — in one view.',
    stat: '₹2.1Cr+',
  },
  engineering: {
    headline: 'Stop losing engineering export margins',
    subheadline: 'Track receivables, GST refunds, and MEIS/RoDTEP benefits for your engineering goods — in one view.',
    stat: '₹8.4Cr+',
  },
};

// Floating particles for ambient animation
const FloatingParticles = React.memo(() => {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none z-5">
      {[...Array(20)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-1 h-1 bg-violet-500/20 rounded-full"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
          }}
          animate={{
            y: [0, -30, 0],
            opacity: [0.2, 0.5, 0.2],
          }}
          transition={{
            duration: 3 + Math.random() * 2,
            repeat: Infinity,
            delay: Math.random() * 2,
            ease: 'easeInOut',
          }}
        />
      ))}
    </div>
  );
});

FloatingParticles.displayName = 'FloatingParticles';

// Scroll progress bar - thin premium bar
const ScrollProgressBar = React.memo(({ progress }) => {
  const width = useTransform(progress, [0, 1], ['0%', '100%']);
  
  return (
    <div className="fixed top-0 left-0 right-0 h-[2px] bg-zinc-900 z-[100]">
      <motion.div
        className="h-full bg-gradient-to-r from-violet-600 via-fuchsia-500 to-violet-600"
        style={{ width }}
      />
    </div>
  );
});

ScrollProgressBar.displayName = 'ScrollProgressBar';

// Industry toggle component - mobile optimized
const IndustryToggle = React.memo(({ activeIndustry, setActiveIndustry }) => {
  const industries = [
    { id: 'brass', label: 'Brass' },
    { id: 'textile', label: 'Textile' },
    { id: 'handicrafts', label: 'Handicrafts' },
    { id: 'engineering', label: 'Engineering' },
  ];

  return (
    <div className="flex flex-wrap justify-center gap-2 mb-6 sm:mb-8 px-2">
      {industries.map((industry) => (
        <button
          key={industry.id}
          onClick={() => setActiveIndustry(industry.id)}
          className={`px-3 sm:px-4 py-1.5 sm:py-2 text-xs sm:text-sm rounded-full transition-all duration-300 ${
            activeIndustry === industry.id
              ? 'bg-violet-600 text-white shadow-lg shadow-violet-500/25'
              : 'bg-zinc-800/50 text-zinc-400 hover:bg-zinc-700/50 hover:text-zinc-300 border border-zinc-700'
          }`}
        >
          {industry.label}
        </button>
      ))}
    </div>
  );
});

IndustryToggle.displayName = 'IndustryToggle';

// Skip animation button
const SkipButton = React.memo(({ onClick, visible }) => {
  if (!visible) return null;
  
  return (
    <motion.button
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClick}
      className="absolute top-20 right-6 z-50 px-3 py-1.5 text-xs text-zinc-400 bg-zinc-900/80 backdrop-blur-sm border border-zinc-700 rounded-full hover:text-white hover:border-zinc-500 transition-colors"
    >
      Skip animation ↓
    </motion.button>
  );
});

SkipButton.displayName = 'SkipButton';

// Main ScrollSyncHero component
const ScrollSyncHero = ({ 
  children, 
  className = '',
  onIndustryChange,
  initialIndustry = 'brass',
  showSkipButton = true,
}) => {
  const containerRef = useRef(null);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [activeIndustry, setActiveIndustry] = useState(initialIndustry);
  const [isScrollMode, setIsScrollMode] = useState(false);
  const [showSkip, setShowSkip] = useState(showSkipButton);
  const [hasUserScrolled, setHasUserScrolled] = useState(false);
  
  // Scroll tracking
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start start', 'end start'],
  });
  
  const smoothProgress = useSpring(scrollYProgress, {
    stiffness: 100,
    damping: 30,
  });

  // Preload images
  useEffect(() => {
    HERO_IMAGES.forEach((img) => {
      const image = new Image();
      image.src = img.url;
    });
  }, []);
  
  // Handle scroll-based image transitions
  useEffect(() => {
    const handleScroll = () => {
      if (!hasUserScrolled) {
        setHasUserScrolled(true);
        setShowSkip(false);
      }
      
      const scrollY = window.scrollY;
      const windowHeight = window.innerHeight;
      const scrollProgress = Math.min(scrollY / windowHeight, 1);
      
      // Change image based on scroll position (every 25% of viewport)
      const newIndex = Math.min(
        Math.floor(scrollProgress * HERO_IMAGES.length),
        HERO_IMAGES.length - 1
      );
      
      if (newIndex !== currentImageIndex && isScrollMode) {
        setCurrentImageIndex(newIndex);
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [currentImageIndex, isScrollMode, hasUserScrolled]);
  
  // Auto-cycle through images when not in scroll mode
  useEffect(() => {
    if (isScrollMode) return;
    
    const interval = setInterval(() => {
      setCurrentImageIndex((prev) => (prev + 1) % HERO_IMAGES.length);
    }, 5000);
    return () => clearInterval(interval);
  }, [isScrollMode]);
  
  // Notify parent of industry change
  useEffect(() => {
    onIndustryChange?.(activeIndustry);
  }, [activeIndustry, onIndustryChange]);
  
  const handleSkip = useCallback(() => {
    window.scrollTo({ top: window.innerHeight, behavior: 'smooth' });
    setShowSkip(false);
  }, []);
  
  const toggleScrollMode = useCallback(() => {
    setIsScrollMode((prev) => !prev);
  }, []);
  
  // Content parallax
  const contentY = useTransform(smoothProgress, [0, 0.5], [0, -60]);
  const contentOpacity = useTransform(smoothProgress, [0, 0.35], [1, 0]);
  const backgroundScale = useTransform(smoothProgress, [0, 1], [1, 1.1]);
  
  const currentContent = INDUSTRY_CONTENT[activeIndustry];
  
  return (
    <section
      ref={containerRef}
      className={`relative min-h-screen overflow-hidden ${className}`}
      aria-label="Hero section"
    >
      <ScrollProgressBar progress={smoothProgress} />
      
      {/* Skip animation button */}
      <AnimatePresence>
        {showSkip && <SkipButton onClick={handleSkip} visible={showSkip} />}
      </AnimatePresence>
      
      {/* Background layer with parallax */}
      <motion.div 
        className="absolute inset-0 overflow-hidden"
        style={{ scale: backgroundScale }}
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={currentImageIndex}
            initial={{ opacity: 0, scale: 1.05 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1.2, ease: 'easeInOut' }}
            className="absolute inset-0"
          >
            <img
              src={HERO_IMAGES[currentImageIndex].url}
              alt={HERO_IMAGES[currentImageIndex].alt}
              className="w-full h-full object-cover"
              loading="eager"
            />
            {/* Dark overlay for text readability */}
            <div className="absolute inset-0 bg-gradient-to-b from-[#09090B]/80 via-[#09090B]/60 to-[#09090B]" />
            <div className="absolute inset-0 bg-gradient-to-r from-[#09090B]/40 via-transparent to-[#09090B]/40" />
          </motion.div>
        </AnimatePresence>
        
        {/* Floating particles */}
        <FloatingParticles />
      </motion.div>
      
      {/* Image caption badge */}
      <div className="absolute bottom-28 left-8 md:left-12 z-30">
        <AnimatePresence mode="wait">
          <motion.span
            key={currentImageIndex}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center px-4 py-2 rounded-full bg-white/5 backdrop-blur-md border border-white/10 text-sm text-zinc-400"
          >
            <span className="w-2 h-2 rounded-full bg-violet-500 mr-2 animate-pulse" />
            {HERO_IMAGES[currentImageIndex].caption}
          </motion.span>
        </AnimatePresence>
      </div>
      
      {/* Progress dots - right side - hidden on mobile */}
      <div className="absolute right-4 md:right-12 top-1/2 -translate-y-1/2 z-30 hidden sm:flex flex-col gap-3">
        {HERO_IMAGES.map((_, index) => (
          <button
            key={index}
            onClick={() => setCurrentImageIndex(index)}
            className={`w-2 h-2 rounded-full transition-all duration-300 ${
              index === currentImageIndex 
                ? 'bg-violet-500 scale-125' 
                : 'bg-white/20 hover:bg-white/40'
            }`}
            aria-label={`Go to image ${index + 1}`}
          />
        ))}
      </div>
      
      {/* Scroll/Auto toggle - repositioned for mobile */}
      <button
        onClick={toggleScrollMode}
        className="absolute bottom-28 right-4 md:right-12 z-30 px-3 py-1.5 text-xs text-zinc-400 bg-zinc-900/60 backdrop-blur-sm border border-zinc-700/50 rounded-full hover:text-white transition-colors hidden sm:block"
      >
        {isScrollMode ? '⏸ Auto' : '↓ Scroll'}
      </button>
      
      {/* Main content */}
      <motion.div
        className="relative z-20 min-h-screen flex flex-col items-center justify-center px-4 sm:px-6 pt-16 sm:pt-20"
        style={{
          y: contentY,
          opacity: contentOpacity,
        }}
      >
        {/* Industry Toggle */}
        <IndustryToggle 
          activeIndustry={activeIndustry} 
          setActiveIndustry={setActiveIndustry} 
        />
        
        {/* Dynamic headline based on industry */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeIndustry}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.4 }}
            className="text-center max-w-4xl mx-auto px-2"
          >
            {/* Always show industry-specific headline */}
            <h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl font-bold leading-tight tracking-tight mb-4 sm:mb-6 text-white">
              {currentContent.headline}
            </h1>
            <p className="text-sm sm:text-base md:text-lg lg:text-xl text-zinc-300 max-w-2xl mx-auto mb-6 sm:mb-8 leading-relaxed">
              {currentContent.subheadline}
            </p>
            <p className="text-xs sm:text-sm text-zinc-500 mb-6 sm:mb-8">
              {currentContent.stat} capital tracked by exporters like you
            </p>
            {/* Render children (CTAs) after headline */}
            {children}
          </motion.div>
        </AnimatePresence>
      </motion.div>
      
      {/* Scroll indicator */}
      <motion.div
        className="absolute bottom-8 left-1/2 -translate-x-1/2 z-30 flex flex-col items-center gap-2"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.5, duration: 0.5 }}
      >
        <span className="text-xs text-zinc-500 uppercase tracking-wider">Scroll</span>
        <motion.div className="w-5 h-8 rounded-full border border-zinc-700 flex items-start justify-center p-1">
          <motion.div
            className="w-1 h-2 rounded-full bg-violet-500"
            animate={{ y: [0, 10, 0] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
          />
        </motion.div>
      </motion.div>
      
      {/* Noise texture overlay */}
      <div 
        className="absolute inset-0 pointer-events-none z-10 opacity-[0.015]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
        }}
      />
    </section>
  );
};

export default ScrollSyncHero;
