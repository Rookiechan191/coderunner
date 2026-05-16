import { useState, useCallback } from "react";
import Editor from "@monaco-editor/react";
import { LANGUAGES } from "./languages.js";
import { useCodeRunner } from "./hooks/useCodeRunner.js";
import LanguageSelector from "./components/LanguageSelector.jsx";
import StatusBadge from "./components/StatusBadge.jsx";
import OutputPanel from "./components/OutputPanel.jsx";

const PANEL = {
  borderRight: "1px solid #27272a",
  display: "flex",
  flexDirection: "column",
};

export default function App() {
  const [language, setLanguage] = useState("python");
  const [code, setCode] = useState(LANGUAGES["python"].starter);
  const [stdin, setStdin] = useState("");
  const [stdinOpen, setStdinOpen] = useState(false);

  const { status, stdout, stderr, execTime, loading, run, reset } = useCodeRunner();

  const handleLanguageChange = useCallback((lang) => {
    setLanguage(lang);
    setCode(LANGUAGES[lang].starter);
    reset();
  }, [reset]);

  const handleRun = useCallback(() => {
    run(language, code, stdin);
  }, [language, code, stdin, run]);

  // Ctrl/Cmd + Enter to run
  const handleKeyDown = useCallback((e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") handleRun();
  }, [handleRun]);

  return (
    <div
      onKeyDown={handleKeyDown}
      style={{ height: "100vh", display: "flex", flexDirection: "column", background: "#0d0d0f" }}
    >
      {/* ── Header ── */}
      <header style={{
        height: 48,
        borderBottom: "1px solid #27272a",
        display: "flex",
        alignItems: "center",
        padding: "0 16px",
        gap: 16,
        flexShrink: 0,
      }}>
        {/* Logo */}
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginRight: 8 }}>
          <span style={{ fontSize: 18 }}>⚡</span>
          <span style={{ fontWeight: 600, fontSize: 15, color: "#e4e4e7" }}>CodeRunner</span>
        </div>

        {/* Language tabs */}
        <LanguageSelector selected={language} onChange={handleLanguageChange} />

        {/* Right side */}
        <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 12 }}>
          <StatusBadge status={status} execTime={execTime} />

          {/* stdin toggle */}
          <button
            onClick={() => setStdinOpen((o) => !o)}
            title="Toggle stdin panel"
            style={{
              padding: "4px 10px",
              borderRadius: 6,
              border: "1px solid #27272a",
              background: stdinOpen ? "#27272a" : "transparent",
              color: "#71717a",
              fontSize: 12,
              cursor: "pointer",
            }}
          >
            stdin
          </button>

          {/* Run button */}
          <button
            onClick={handleRun}
            disabled={loading}
            style={{
              padding: "6px 18px",
              borderRadius: 7,
              border: "none",
              background: loading ? "#4338ca" : "#6366f1",
              color: "#fff",
              fontWeight: 600,
              fontSize: 14,
              cursor: loading ? "not-allowed" : "pointer",
              display: "flex",
              alignItems: "center",
              gap: 6,
              transition: "background 0.15s",
            }}
          >
            {loading ? (
              <>
                <Spinner /> Running
              </>
            ) : (
              <>▶ Run</>
            )}
          </button>
        </div>
      </header>

      {/* ── Body: Editor | Output ── */}
      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>

        {/* Left: Code editor */}
        <div style={{ ...PANEL, flex: 1 }}>

          {/* Editor top bar */}
          <div style={{
            height: 32,
            borderBottom: "1px solid #1e1e21",
            display: "flex",
            alignItems: "center",
            padding: "0 16px",
            gap: 8,
            flexShrink: 0,
          }}>
            <span style={{
              width: 8, height: 8, borderRadius: "50%",
              background: LANGUAGES[language].color,
              display: "inline-block",
            }} />
            <span style={{ fontSize: 12, color: "#52525b" }}>
              {language === "java" ? "Main.java"
                : language === "go" ? "main.go"
                : language === "rust" ? "main.rs"
                : `solution.${language === "javascript" ? "js" : language === "python" ? "py" : language}`}
            </span>
            <span style={{ marginLeft: "auto", fontSize: 11, color: "#3f3f46" }}>
              Ctrl+Enter to run
            </span>
          </div>

          {/* Monaco editor */}
          <div style={{ flex: 1, overflow: "hidden" }}>
            <Editor
              height="100%"
              language={LANGUAGES[language].monacoLang}
              value={code}
              onChange={(val) => setCode(val ?? "")}
              theme="vs-dark"
              options={{
                fontSize: 14,
                fontFamily: "'JetBrains Mono', monospace",
                fontLigatures: true,
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                lineNumbers: "on",
                renderLineHighlight: "line",
                padding: { top: 12, bottom: 12 },
                smoothScrolling: true,
                cursorSmoothCaretAnimation: "on",
                tabSize: 4,
              }}
            />
          </div>

          {/* stdin panel (collapsible) */}
          {stdinOpen && (
            <div style={{
              borderTop: "1px solid #27272a",
              padding: "10px 16px",
              flexShrink: 0,
            }}>
              <div style={{ fontSize: 11, color: "#52525b", marginBottom: 6, textTransform: "uppercase", letterSpacing: 1 }}>
                stdin
              </div>
              <textarea
                value={stdin}
                onChange={(e) => setStdin(e.target.value)}
                placeholder="Input for your program (optional)..."
                rows={3}
                style={{
                  width: "100%",
                  background: "#111113",
                  color: "#e4e4e7",
                  border: "1px solid #27272a",
                  borderRadius: 6,
                  padding: "8px 10px",
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: 13,
                  resize: "vertical",
                  outline: "none",
                }}
              />
            </div>
          )}
        </div>

        {/* Right: Output panel */}
        <div style={{ ...PANEL, width: "42%", borderRight: "none" }}>

          {/* Output top bar */}
          <div style={{
            height: 32,
            borderBottom: "1px solid #1e1e21",
            display: "flex",
            alignItems: "center",
            padding: "0 16px",
            gap: 8,
            flexShrink: 0,
          }}>
            <span style={{ fontSize: 12, color: "#52525b" }}>output</span>
            {(stdout || stderr) && (
              <button
                onClick={reset}
                style={{
                  marginLeft: "auto",
                  fontSize: 11,
                  color: "#52525b",
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                  padding: "2px 6px",
                  borderRadius: 4,
                }}
              >
                clear
              </button>
            )}
          </div>

          <OutputPanel
            status={status}
            stdout={stdout}
            stderr={stderr}
            loading={loading}
          />
        </div>
      </div>
    </div>
  );
}

function Spinner() {
  return (
    <svg
      width="14" height="14"
      viewBox="0 0 14 14"
      style={{ animation: "spin 0.7s linear infinite" }}
    >
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <circle cx="7" cy="7" r="5.5" fill="none" stroke="rgba(255,255,255,0.3)" strokeWidth="2" />
      <path d="M7 1.5A5.5 5.5 0 0 1 12.5 7" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}
