import { cn } from '@/utils/cn';

interface LogoProps {
  className?: string;
  size?: number;
}

/**
 * GrowFlow "Flowing G" brand mark.
 * Connected Flow + Abstract G.
 * Uses currentColor for theme compatibility.
 */
export function Logo({ className, size = 32 }: LogoProps) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 40 40"
      fill="none"
      width={size}
      height={size}
      className={cn('gf-logo', className)}
      aria-hidden="true"
    >
      <path
        d="M20 4C11.163 4 4 11.163 4 20s7.163 16 16 16c4.418 0 8.418-1.791 11.314-4.686"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
        fill="none"
      />
      <path
        d="M36 20c0-8.837-7.163-16-16-16"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
        fill="none"
        opacity="0.4"
      />
      <path
        d="M36 20H22"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
      />
      <path
        d="M22 20v-8"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
      />
    </svg>
  );
}

/**
 * GrowFlow full brand — mark + wordmark.
 */
export function GrowFlowBrand({ className }: { className?: string }) {
  return (
    <span className={cn('gf-brand', className)}>
      <Logo size={28} />
      <span className="gf-brand__wordmark">GrowFlow</span>
    </span>
  );
}
