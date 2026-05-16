const COLORS = {
  pending: '#f0a500',
  running: '#3b9eff',
  success: '#4ec94e',
  failed: '#f48771',
  timeout: '#f48771',
}

export default function StatusBadge({ status }) {
  if (!status) return null
  return (
    <span style={{
      background: COLORS[status] || '#888',
      color: '#000',
      borderRadius: 4,
      padding: '2px 8px',
      fontSize: 12,
      fontWeight: 600,
    }}>
      {status.toUpperCase()}
    </span>
  )
}