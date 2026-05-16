'use client';

export default function ConfidenceRing({ confidence, size = 100 }: { confidence: number; size?: number }) {
  const radius = (size - 10) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = (confidence / 100) * circumference;
  const color = confidence >= 70 ? 'var(--green)' : confidence >= 50 ? 'var(--amber)' : 'var(--red)';

  return (
    <div className="confidence-ring" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {/* Background circle */}
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" stroke="var(--surface2)" strokeWidth={8}
        />
        {/* Progress arc */}
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" stroke={color} strokeWidth={8}
          strokeDasharray={circumference}
          strokeDashoffset={circumference - progress}
          strokeLinecap="butt"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          style={{ transition: 'stroke-dashoffset 1.5s cubic-bezier(0.4, 0, 0.2, 1)' }}
        />
        {/* Glow */}
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" stroke={color} strokeWidth={2} opacity={0.5}
          strokeDasharray={circumference}
          strokeDashoffset={circumference - progress}
          strokeLinecap="butt"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          filter="url(#glow)"
        />
        <defs>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur" />
            <feMerge><feMergeNode in="coloredBlur" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
        </defs>
      </svg>
      <div style={{
        position: 'absolute',
        textAlign: 'center',
      }}>
        <div style={{
          fontFamily: 'var(--font-mono)',
          fontSize: size * 0.28,
          fontWeight: 700,
          color,
          lineHeight: 1,
        }}>
          {confidence}
        </div>
        <div style={{
          fontFamily: 'var(--font-head)',
          fontSize: size * 0.1,
          color: 'var(--muted)',
          letterSpacing: '0.1em',
          marginTop: 2,
        }}>
          CONFIDENCE
        </div>
      </div>
    </div>
  );
}
