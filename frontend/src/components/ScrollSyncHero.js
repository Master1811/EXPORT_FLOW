import React, { useRef, useMemo, useState, useEffect } from 'react';
import { motion, useScroll, useTransform, useSpring, AnimatePresence } from 'framer-motion';

// Premium export/logistics images from Unsplash & Pexels
const HERO_IMAGES = [
  {
    url: 'https://images.pexels.com/photos/3076002/pexels-photo-3076002.jpeg?auto=compress&cs=tinysrgb&w=1920',
    alt: 'Illuminated aerial view of container terminal',
    caption: 'Global Logistics Network',
  },
  {
    url: 'https://images.pexels.com/photos/9806482/pexels-photo-9806482.jpeg?auto=compress&cs=tinysrgb&w=1920',
    alt: 'Cargo ship transporting containers across ocean',
    caption: 'Seamless International Trade',
  },
  {
    url: 'https://images.pexels.com/photos/1624695/pexels-photo-1624695.jpeg?auto=compress&cs=tinysrgb&w=1920',
    alt: 'Colorful shipping containers in busy port',
    caption: 'Port Operations Excellence',
  },
  {
    url: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1920',
    alt: 'Finance dashboard analytics screen',
    caption: 'Smart Financial Analytics',
  },
  {
    url: 'https://images.pexels.com/photos/67563/plane-aircraft-jet-airbase-67563.jpeg?auto=compress&cs=tinysrgb&w=1920',
    alt: 'Cargo plane on tarmac at night',
    caption: 'Air Freight Solutions',
  },
];

// Scroll progress bar
const ScrollProgressBar = React.memo(({ progress }) => {
  const width = useTransform(progress, [0, 1], ['0%', '100%']);
  
  return (
    <div className="absolute top-0 left-0 right-0 h-1 bg-zinc-800/50 z-50">
      <motion.div
        className="h-full bg-gradient-to-r from-violet-600 via-fuchsia-500 to-violet-600"
        style={{ width }}
      />
    </div>
  );
});

ScrollProgressBar.displayName = 'ScrollProgressBar';

// Main ScrollSyncHero component - Simplified for reliability
const ScrollSyncHero = ({ children, className = '' }) => {
  const containerRef = useRef(null);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [imagesLoaded, setImagesLoaded] = useState(false);
  
  // Scroll tracking
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start start', 'end start'],
  });
  
  // Smooth the scroll progress
  const smoothProgress = useSpring(scrollYProgress, {
    stiffness: 100,
    damping: 30,
  });

  // Preload images
  useEffect(() => {
    const preloadImages = async () => {
      const imagePromises = HERO_IMAGES.map((img) => {
        return new Promise((resolve) => {
          const image = new Image();
          image.onload = resolve;
          image.onerror = resolve;
          image.src = img.url;
        });
      });
      await Promise.all(imagePromises);
      setImagesLoaded(true);
    };
    preloadImages();
  }, []);
  
  // Auto-cycle through images
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentImageIndex((prev) => (prev + 1) % HERO_IMAGES.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);
  
  // Content parallax
  const contentY = useTransform(smoothProgress, [0, 0.5], [0, -50]);
  const contentOpacity = useTransform(smoothProgress, [0, 0.4], [1, 0]);
  
  return (
    <section
      ref={containerRef}
      className={`relative min-h-screen ${className}`}
      aria-label="Hero section with scroll animation"
    >
      {/* Background images with crossfade */}
      <div className="absolute inset-0 overflow-hidden">
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
            {/* Premium gradient overlays */}
            <div className="absolute inset-0 bg-gradient-to-b from-[#09090B]/60 via-[#09090B]/40 to-[#09090B]" />
            <div className="absolute inset-0 bg-gradient-to-r from-violet-900/10 via-transparent to-blue-900/10" />
          </motion.div>
        </AnimatePresence>
        
        {/* Image caption */}
        <div className="absolute bottom-32 left-8 md:left-16 z-30">
          <AnimatePresence mode="wait">
            <motion.span
              key={currentImageIndex}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
              className="inline-flex items-center px-4 py-2 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-sm text-zinc-300"
            >
              <span className="w-2 h-2 rounded-full bg-violet-500 mr-2 animate-pulse" />
              {HERO_IMAGES[currentImageIndex].caption}
            </motion.span>
          </AnimatePresence>
        </div>
        
        {/* Image indicator dots */}
        <div className="absolute right-6 md:right-12 top-1/2 -translate-y-1/2 z-30 flex flex-col gap-3">
          {HERO_IMAGES.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentImageIndex(index)}
              className={`w-2 h-2 rounded-full transition-all duration-300 ${
                index === currentImageIndex 
                  ? 'bg-violet-500 scale-125' 
                  : 'bg-white/30 hover:bg-white/50'
              }`}
              aria-label={`Go to image ${index + 1}`}
            />
          ))}
        </div>
      </div>
      
      <ScrollProgressBar progress={smoothProgress} />
      
      {/* Hero content */}
      <motion.div
        className="relative z-20 min-h-screen flex items-center justify-center px-4 sm:px-6 pt-16"
        style={{
          y: contentY,
          opacity: contentOpacity,
        }}
      >
        {children}
      </motion.div>
      
      {/* Scroll indicator */}
      <motion.div
        className="absolute bottom-8 left-1/2 -translate-x-1/2 z-30 flex flex-col items-center gap-2"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1, duration: 0.5 }}
      >
        <span className="text-xs text-zinc-400 uppercase tracking-wider">Scroll to explore</span>
        <motion.div className="w-6 h-10 rounded-full border-2 border-zinc-600 flex items-start justify-center p-1">
          <motion.div
            className="w-1.5 h-3 rounded-full bg-violet-500"
            animate={{ y: [0, 12, 0] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
          />
        </motion.div>
      </motion.div>
      
      {/* Noise texture */}
      <div 
        className="absolute inset-0 pointer-events-none z-10 opacity-[0.02]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
        }}
      />
    </section>
  );
};

export default ScrollSyncHero;
