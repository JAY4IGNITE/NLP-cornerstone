export default function BrandMark({ className = '' }) {
  return <svg className={`brand-mark ${className}`} viewBox="0 0 32 32" fill="none" aria-hidden="true">
    <path d="M16 3 28 10v12l-12 7L4 22V10L16 3Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
    <path d="m4 10 12 7 12-7M16 17v12M10 6.5l12 7v12M22 6.5l-12 7v12" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
  </svg>;
}
