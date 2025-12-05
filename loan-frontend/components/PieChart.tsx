import React from "react";

interface PieChartProps {
  score: number; // 0 to 1
  size?: number;
}

const PieChart: React.FC<PieChartProps> = ({ score, size = 200 }) => {
  const radius = size / 2 - 10;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - score * circumference;

  // Determine risk level color (same logic as RiskIndicator)
  let strokeColor = "#22c55e"; // green-500
  if (score >= 0.75) {
    strokeColor = "#ef4444"; // red-500
  } else if (score >= 0.4) {
    strokeColor = "#eab308"; // yellow-500
  }

  return (
    <svg width={size} height={size}>
      {/* Background circle */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        stroke="#e5e7eb" // neutral-300
        strokeWidth="12"
        fill="transparent"
      />

      {/* Risk progress circle */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        stroke={strokeColor}
        strokeWidth="12"
        fill="transparent"
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        strokeLinecap="round"
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
      />

      {/* Center text */}
      <text
        x="50%"
        y="50%"
        textAnchor="middle"
        dy="0.3em"
        fontSize="28"
        fontWeight="bold"
        fill="#374151"
      >
        {Math.round(score * 100)}%
      </text>
    </svg>
  );
};

export default PieChart;
