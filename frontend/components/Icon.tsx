export default function Icon({ name, size = 24, filled = false }: { name: string; size?: number; filled?: boolean }) {
  return <span aria-hidden="true" className="material-symbols-outlined" style={{ fontSize: size, fontVariationSettings: `'FILL' ${filled ? 1 : 0}, 'wght' 400, 'GRAD' 0, 'opsz' 24` }}>{name}</span>;
}
