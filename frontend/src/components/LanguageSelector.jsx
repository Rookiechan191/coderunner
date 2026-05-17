const LANGUAGES = ['python', 'javascript', 'go', 'java', 'rust', 'cpp']

export default function LanguageSelector({ value, onChange, selected }) {
  const current = value || selected
  return (
    <select
      value={current}
      onChange={e => onChange(e.target.value)}
      style={{
        background: '#1e1e1e',
        color: '#d4d4d4',
        border: '1px solid #444',
        borderRadius: 4,
        padding: '4px 8px',
        fontSize: 14,
      }}
    >
      {LANGUAGES.map(lang => (
        <option key={lang} value={lang}>{lang}</option>
      ))}
    </select>
  )
}