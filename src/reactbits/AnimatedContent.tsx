import React from "react";
import { motion } from "motion/react";

interface AnimatedContentProps {
  children: React.ReactNode;
  distance?: number;
  direction?: "vertical" | "horizontal";
  reverse?: boolean;
  duration?: number;
  delay?: number;
  className?: string;
  once?: boolean;
}

// ReactBits — AnimatedContent (motion implementation, no GSAP dependency)
export const AnimatedContent: React.FC<AnimatedContentProps> = ({
  children,
  distance = 40,
  direction = "vertical",
  reverse = false,
  duration = 0.8,
  delay = 0,
  className = "",
  once = true,
}) => {
  const axis = direction === "horizontal" ? "x" : "y";
  const offset = reverse ? -distance : distance;

  return (
    <motion.div
      className={className}
      initial={{ [axis]: offset, opacity: 0 } as any}
      whileInView={{ [axis]: 0, opacity: 1 } as any}
      viewport={{ once, amount: 0.15 }}
      transition={{ duration, delay, ease: [0.25, 0.4, 0.25, 1] }}
    >
      {children}
    </motion.div>
  );
};

export default AnimatedContent;
