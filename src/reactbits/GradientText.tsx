import React from "react";

interface GradientTextProps {
  children: React.ReactNode;
  className?: string;
  colors?: string[];
  animationSpeed?: number;
  showBorder?: boolean;
}

// ReactBits — GradientText
export const GradientText: React.FC<GradientTextProps> = ({
  children,
  className = "",
  colors = ["#818cf8", "#c084fc", "#38bdf8", "#818cf8"],
  animationSpeed = 8,
  showBorder = false,
}) => {
  const gradientStyle: React.CSSProperties = {
    backgroundImage: `linear-gradient(to right, ${colors.join(", ")})`,
    animationDuration: `${animationSpeed}s`,
  };

  return (
    <span className={`animated-gradient-text ${className}`}>
      {showBorder && (
        <span className="gradient-overlay" style={gradientStyle}></span>
      )}
      <span className="text-content" style={gradientStyle}>
        {children}
      </span>
    </span>
  );
};

export default GradientText;
