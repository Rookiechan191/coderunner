export default function OutputPanel({ stdout, stderr, status, loading }) {
  if (loading && !stdout && !stderr) {
    return (
      <div style={{ padding: 16, color: '#71717a', fontFamily: 'monospace', fontSize: 13 }}>
        Executing...
      </div>
    )
  }

  if (!stdout && !stderr) {
    return (
      <div style={{ padding: 16, color: '#3f3f46', fontFamily: 'monospace', fontSize: 13 }}>
        {status === 'success' ? 'No output' : 'Run your code to see output here.'}
      </div>
    )
  }

  return (
    <div style={{ flex: 1, overflow: 'auto', padding: 16 }}>
      {stdout && (
        <pre style={{
          color: '#d4d4d4',
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: 13,
          margin: 0,
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
        }}>
          {stdout}
        </pre>
      )}
      {stderr && (
        <pre style={{
          color: '#f48771',
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: 13,
          margin: 0,
          marginTop: stdout ? 12 : 0,
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
        }}>
          {stderr}
        </pre>
      )}
    </div>
  )
}