import { useState, useCallback, useRef } from "react"

export function useCodeRunner() {
  const [status, setStatus] = useState(null)
  const [stdout, setStdout] = useState("")
  const [stderr, setStderr] = useState("")
  const [execTime, setExecTime] = useState(null)
  const [loading, setLoading] = useState(false)
  const intervalRef = useRef(null)

  const reset = useCallback(() => {
    setStatus(null)
    setStdout("")
    setStderr("")
    setExecTime(null)
    setLoading(false)
    if (intervalRef.current) clearInterval(intervalRef.current)
  }, [])

  const run = useCallback(async (language, source_code, stdin = "") => {
    setLoading(true)
    setStatus("pending")
    setStdout("")
    setStderr("")
    setExecTime(null)
    if (intervalRef.current) clearInterval(intervalRef.current)

    try {
      const res = await fetch("/api/jobs/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ language, source_code, stdin }),
      })
      const job = await res.json()
      const jobId = job.id

      intervalRef.current = setInterval(async () => {
        try {
          const r = await fetch(`/api/jobs/${jobId}`)
          const data = await r.json()
          setStatus(data.status)

          if (data.status === "success" || data.status === "failed" || data.status === "timeout") {
            setStdout(data.stdout || "")
            setStderr(data.stderr || "")
            setExecTime(data.execution_time_ms)
            setLoading(false)
            clearInterval(intervalRef.current)
          }
        } catch (err) {
          setStatus("failed")
          setStderr(String(err))
          setLoading(false)
          clearInterval(intervalRef.current)
        }
      }, 500)

    } catch (err) {
      setStatus("failed")
      setStderr(String(err))
      setLoading(false)
    }
  }, [])

  return { status, stdout, stderr, execTime, loading, run, reset }
}