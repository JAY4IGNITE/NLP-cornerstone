
import React, { useEffect, useRef } from 'react';
import gsap from 'gsap';

export default function ThinkingOrb({ isThinking = false }) {
  const orbRef = useRef(null);

  useEffect(() => {
    if (isThinking) {
      gsap.to(orbRef.current, {
        scale: 1.2,
        boxShadow: "0 0 20px 5px rgba(212, 175, 55, 0.6)",
        duration: 0.8,
        yoyo: true,
        repeat: -1,
        ease: "power1.inOut"
      });
    } else {
      gsap.killTweensOf(orbRef.current);
      gsap.to(orbRef.current, {
        scale: 1,
        boxShadow: "0 0 10px 2px rgba(212, 175, 55, 0.2)",
        duration: 0.5,
        ease: "power2.out"
      });
    }
  }, [isThinking]);

  return (
    <div style={{
      width: '12px',
      height: '12px',
      borderRadius: '50%',
      backgroundColor: 'var(--accent-gold)',
      margin: '0 8px',
      display: 'inline-block'
    }} ref={orbRef} />
  );
}
