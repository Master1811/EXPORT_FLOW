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

// Individual image frame for the scroll animation
const ImageFrame = React.memo(({ 
  image, 
  index, 
  scrollProgress, 
  totalFrames,
  isActive,
}) => {
  // Calculate when this frame should be visible - first image starts visible
  const frameStart = index === 0 ? 0 : (index - 0.2) / totalFrames;
  const framePeak = (index + 0.3) / totalFrames;
  const frameEnd = (index + 0.8) / totalFrames;
  
  // First image should start visible
  const opacity = useTransform(
    scrollProgress,
    index === 0 
      ? [0, 0.15, framePeak] 
      : [frameStart, (frameStart + framePeak) / 2, framePeak, frameEnd],
    index === 0 
      ? [1, 1, 0]
      : [0, 1, 1, index === totalFrames - 1 ? 1 : 0]
  );
  
  // Parallax zoom effect
  const scale = useTransform(
    scrollProgress,
    [frameStart, framePeak, frameEnd],
    [1.1, 1, 0.98]
  );
  
  // Vertical parallax movement
  const y = useTransform(
    scrollProgress,
    [frameStart, framePeak, frameEnd],
    [30, 0, -20]
  );

  const springConfig = { stiffness: 100, damping: 30 };
  const smoothOpacity = useSpring(opacity, springConfig);
  const smoothScale = useSpring(scale, springConfig);
  const smoothY = useSpring(y, springConfig);

  return (
    <motion.div
      className="absolute inset-0 will-change-transform"
      style={{
        opacity: smoothOpacity,
        scale: smoothScale,
        y: smoothY,
        zIndex: index,
      }}
    >
      <div className="absolute inset-0 overflow-hidden">
        <img
          src={image.url}
          alt={image.alt}
          className="w-full h-full object-cover"
          loading={index === 0 ? 'eager' : 'lazy'}
          decoding="async"
        />
        {/* Premium gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#09090B]/60 via-[#09090B]/40 to-[#09090B]/90" />
        <div className="absolute inset-0 bg-gradient-to-r from-violet-900/10 via-transparent to-blue-900/10" />
      </div>
      
      {/* Frame caption */}
      <AnimatePresence>
        {isActive && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5 }}
            className="absolute bottom-32 left-8 md:left-16 z-30"
          >
            <span className="inline-flex items-center px-4 py-2 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-sm text-zinc-300">
              <span className="w-2 h-2 rounded-full bg-violet-500 mr-2 animate-pulse" />
              {image.caption}
            </span>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
});

ImageFrame.displayName = 'ImageFrame';

// Progress indicator dots
const ProgressDots = React.memo(({ activeIndex, totalFrames }) => {
  return (
    <div className="absolute right-6 md:right-12 top-1/2 -translate-y-1/2 z-30 flex flex-col gap-3">
      {Array.from({ length: totalFrames }).map((_, index) => (
        <motion.div
          key={index}
          className={`w-2 h-2 rounded-full transition-all duration-300 ${
            index === activeIndex 
              ? 'bg-violet-500 scale-125' 
              : 'bg-white/30 hover:bg-white/50'
          }`}
          initial={false}
          animate={{
            scale: index === activeIndex ? 1.25 : 1,
            opacity: index === activeIndex ? 1 : 0.5,
          }}
        />
      ))}
    </div>
  );
});

ProgressDots.displayName = 'ProgressDots';

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

// Main ScrollSyncHero component
const ScrollSyncHero = ({ children, className = '' }) => {
  const containerRef = useRef(null);
  const [activeFrame, setActiveFrame] = useState(0);
  const totalFrames = HERO_IMAGES.length;
  
  // Scroll tracking with offset for smooth parallax
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start start', 'end end'],
  });
  
  // Smooth the scroll progress for premium feel
  const smoothProgress = useSpring(scrollYProgress, {
    stiffness: 100,
    damping: 30,
    restDelta: 0.001,
  });
  
  // Track active frame based on scroll position
  useEffect(() => {
    const unsubscribe = scrollYProgress.on('change', (latest) => {
      const frameIndex = Math.min(
        Math.floor(latest * totalFrames),
        totalFrames - 1
      );
      setActiveFrame(frameIndex);
    });
    
    return () => unsubscribe();
  }, [scrollYProgress, totalFrames]);
  
  // Content animations tied to scroll - start visible
  const contentY = useTransform(smoothProgress, [0, 0.2], [0, -80]);
  const contentOpacity = useTransform(smoothProgress, [0, 0.15, 0.25], [1, 1, 0]);
  const contentScale = useTransform(smoothProgress, [0, 0.2], [1, 0.98]);
  
  // Memoize image frames
  const imageFrames = useMemo(() => (
    HERO_IMAGES.map((image, index) => (
      <ImageFrame
        key={index}
        image={image}
        index={index}
        scrollProgress={smoothProgress}
        totalFrames={totalFrames}
        isActive={index === activeFrame}
      />
    ))
  ), [smoothProgress, totalFrames, activeFrame]);
  
  return (
    <section
      ref={containerRef}
      className={`relative ${className}`}
      style={{ height: `${(totalFrames + 0.5) * 100}vh` }}
      aria-label="Scroll-synced hero animation"
    >
      {/* Sticky container for the hero */}
      <div className="sticky top-0 h-screen overflow-hidden">
        <ScrollProgressBar progress={smoothProgress} />
        
        {/* Image frames */}
        <div className="absolute inset-0">
          {imageFrames}
        </div>
        
        {/* Progress dots */}
        <ProgressDots activeIndex={activeFrame} totalFrames={totalFrames} />
        
        {/* Hero content overlay */}
        <motion.div
          className="relative z-20 h-full flex items-center justify-center px-4 sm:px-6 pt-16"
          style={{
            y: contentY,
            opacity: contentOpacity,
            scale: contentScale,
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
          <motion.div
            className="w-6 h-10 rounded-full border-2 border-zinc-600 flex items-start justify-center p-1"
          >
            <motion.div
              className="w-1.5 h-3 rounded-full bg-violet-500"
              animate={{
                y: [0, 12, 0],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            />
          </motion.div>
        </motion.div>
        
        {/* Noise texture overlay for premium feel */}
        <div 
          className="absolute inset-0 pointer-events-none z-10 opacity-[0.02]"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
          }}
        />
      </div>
    </section>
  );
};

export default ScrollSyncHero;
