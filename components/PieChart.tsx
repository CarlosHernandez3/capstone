import React from 'react';

interface PieChartProps {
  score: number; // between 0 and 1
  size?: number;
}

const PieChart: React.FC<PieChartProps> = ({ score, size = 150 }) => {
  const radius = size / 2 - 10;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - score * circumference;

  let colorClass = 'text-accent'; // green for low risk
  if (score >= 0.75) {
    colorClass = 'text-danger'; // red for high risk
  } else if (score >= 0.4) {
    colorClass = 'text-secondary'; // yellow for medium risk
  }

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg className="absolute w-full h-full" viewBox={`0 0 ${size} ${size}`}>
        <circle
          className="text-neutral-200"
          strokeWidth="10"
          stroke="currentColor"
          fill="transparent"
          r={radius}
          cx={size / 2}
          cy={size / 2}
        />
        <circle
          className={`${colorClass} transition-all duration-1000 ease-out`}
          strokeWidth="10"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          stroke="currentColor"
          fill="transparent"
          r={radius}
          cx={size / 2}
          cy={size / 2}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </svg>
      <div className={`absolute text-3xl font-bold ${colorClass}`}>
        {Math.round(score * 100)}%
      </div>
    </div>
  );
};

export default PieChart;
