import { useEffect, useRef, useId } from 'react';

export default function BrandMark({ className = '' }) {
  const containerRef = useRef(null);
  const eyesRef = useRef(null);
  // Generate a unique ID for the mask to prevent conflicts when multiple logos are rendered
  const maskId = `eyes-mask-${useId().replace(/:/g, '')}`;

  useEffect(() => {
    let animationFrameId;
    let targetX = 0;
    let targetY = 0;
    let currentX = 0;
    let currentY = 0;

    const handleMouseMove = (e) => {
      if (!containerRef.current) return;
      
      // Get logo center position
      const rect = containerRef.current.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      
      // Calculate distance from cursor to logo center
      const deltaX = e.clientX - centerX;
      const deltaY = e.clientY - centerY;
      
      const angle = Math.atan2(deltaY, deltaX);
      const maxMove = 3; // Max translation in pixels
      
      // Normalize distance so it maxes out at 80px away
      const distance = Math.min(Math.sqrt(deltaX * deltaX + deltaY * deltaY) / 80, 1) * maxMove;
      
      targetX = Math.cos(angle) * distance;
      targetY = Math.sin(angle) * distance;
    };

    const animate = () => {
      // Lerp (linear interpolation) for extreme smoothness
      currentX += (targetX - currentX) * 0.12;
      currentY += (targetY - currentY) * 0.12;
      
      if (eyesRef.current) {
        eyesRef.current.style.transform = `translate(${currentX}px, ${currentY}px)`;
      }
      animationFrameId = requestAnimationFrame(animate);
    };

    window.addEventListener('mousemove', handleMouseMove);
    animate();

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <svg 
      ref={containerRef}
      className={`brand-mark ${className}`} 
      viewBox="0 0 32 32" 
      fill="none" 
      aria-hidden="true"
    >
      <defs>
        <mask id={maskId}>
          {/* White keeps the background visible */}
          <rect x="0" y="0" width="32" height="32" fill="white" />
          {/* Black punches transparent holes for the eyes */}
          <g ref={eyesRef} style={{ willChange: 'transform' }}>
            <circle cx="11" cy="16" r="3.5" fill="black" />
            <circle cx="21" cy="16" r="3.5" fill="black" />
          </g>
        </mask>
      </defs>

      {/* Face Base using currentColor to adapt to theme, and r=16 for larger size */}
      <circle cx="16" cy="16" r="16" fill="currentColor" mask={`url(#${maskId})`} />
    </svg>
  );
}
