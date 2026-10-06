import { useEffect, useRef } from 'react';

export default function BrandMark({ className = '' }) {
  const containerRef = useRef(null);
  const eyesRef = useRef(null);

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!containerRef.current || !eyesRef.current) return;
      
      // Get logo center position
      const rect = containerRef.current.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      
      // Calculate distance from cursor to logo center
      const deltaX = e.clientX - centerX;
      const deltaY = e.clientY - centerY;
      
      const angle = Math.atan2(deltaY, deltaX);
      const maxMove = 2.5; // Max translation in pixels
      
      // Normalize distance so it maxes out at 100px away
      const distance = Math.min(Math.sqrt(deltaX * deltaX + deltaY * deltaY) / 80, 1) * maxMove;
      
      const moveX = Math.cos(angle) * distance;
      const moveY = Math.sin(angle) * distance;
      
      // Apply transform
      eyesRef.current.style.transform = `translate(${moveX}px, ${moveY}px)`;
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return (
    <svg 
      ref={containerRef}
      className={`brand-mark ${className}`} 
      viewBox="0 0 32 32" 
      fill="none" 
      aria-hidden="true"
    >
      {/* Face Base */}
      <circle cx="16" cy="16" r="14" fill="#0E4D34" />
      
      {/* Animated Eyes Group */}
      <g 
        ref={eyesRef} 
        style={{ 
          transition: 'transform 0.15s ease-out',
          willChange: 'transform'
        }}
      >
        <circle cx="11" cy="16" r="3" fill="#FFFFFF" />
        <circle cx="21" cy="16" r="3" fill="#FFFFFF" />
      </g>
    </svg>
  );
}
