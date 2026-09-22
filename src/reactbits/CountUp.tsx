import { useEffect, useRef } from "react";
import { useInView, useMotionValue, useSpring } from "motion/react";

interface CountUpProps {
  to: number;
  from?: number;
  direction?: "up" | "down";
  delay?: number;
  duration?: number;
  className?: string;
  decimals?: number;
  separator?: string;
  suffix?: string;
  prefix?: string;
}

// ReactBits — CountUp
export default function CountUp({
  to,
  from = 0,
  direction = "up",
  delay = 0,
  duration = 2,
  className = "",
  decimals = 0,
  separator = "",
  suffix = "",
  prefix = "",
}: CountUpProps) {
  const ref = useRef<HTMLSpanElement>(null);
  const motionValue = useMotionValue(direction === "down" ? to : from);

  const damping = 20 + 40 * (1 / duration);
  const stiffness = 100 * (1 / duration);
  const springValue = useSpring(motionValue, { damping, stiffness });
  const isInView = useInView(ref, { once: true, margin: "0px" });

  const format = (value: number) => {
    const fixed = value.toFixed(decimals);
    const [intPart, decPart] = fixed.split(".");
    const withSep = separator
      ? intPart.replace(/\B(?=(\d{3})+(?!\d))/g, separator)
      : intPart;
    return `${prefix}${decPart ? `${withSep}.${decPart}` : withSep}${suffix}`;
  };

  useEffect(() => {
    if (ref.current) ref.current.textContent = format(direction === "down" ? to : from);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (isInView) {
      const t = setTimeout(() => {
        motionValue.set(direction === "down" ? from : to);
      }, delay * 1000);
      return () => clearTimeout(t);
    }
  }, [isInView, motionValue, to, from, direction, delay]);

  useEffect(() => {
    const unsub = springValue.on("change", (latest) => {
      if (ref.current) ref.current.textContent = format(latest);
    });
    return () => unsub();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [springValue, decimals, separator, suffix, prefix]);

  return <span className={className} ref={ref} />;
}
