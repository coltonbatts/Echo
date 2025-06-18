import React, { useState, useRef, useEffect } from "react";

const terminalStyle = {
  background: "#101010",
  color: "#00ff00",
  fontFamily: "Fira Mono, JetBrains Mono, monospace",
  border: "1.5px solid #00ff00",
  borderRadius: "6px",
  boxShadow: "0 0 8px #001a00",
  padding: "1.2rem 1.5rem 1.2rem 1.2rem",
  minHeight: 320,
  maxHeight: 420,
  overflowY: "auto",
  display: "flex",
  flexDirection: "column",
  justifyContent: "flex-end",
  margin: 0,
  position: "relative",
  whiteSpace: "pre-wrap",
};

const inputRowStyle = {
  display: "flex",
  alignItems: "center",
  width: "100%",
  marginTop: 12,
  borderTop: "1.5px solid #00ff00",
  paddingTop: 10,
};

const inputStyle = {
  flex: 1,
  background: "#101010",
  color: "#00ff00",
  fontFamily: "Fira Mono, JetBrains Mono, monospace",
  border: "none",
  outline: "none",
  fontSize: 16,
  padding: "0.5rem 0.6rem",
  caretColor: "#00ff00",
  letterSpacing: 1,
};

const sendBtnStyle = {
  background: "#00ff00",
  color: "#101010",
  border: "none",
  borderRadius: 4,
  fontWeight: 700,
  fontFamily: "Fira Mono, JetBrains Mono, monospace",
  fontSize: 16,
  marginLeft: 12,
  padding: "0.5rem 1.3rem",
  cursor: "pointer",
  transition: "background 0.2s",
};

const blinkStyle = {
  animation: "blink 1s step-end infinite",
};

const typewriterStyle = {
  display: "inline-block",
  whiteSpace: "pre-wrap",
};

// Keyframes for blinking cursor
const styleSheet = `@keyframes blink { 0% { opacity: 1; } 49% { opacity: 1; } 50% { opacity: 0; } 100% { opacity: 0; } }`;
if (typeof document !== 'undefined' && !document.getElementById('terminal-blink-keyframes')) {
  const style = document.createElement('style');
  style.id = 'terminal-blink-keyframes';
  style.innerHTML = styleSheet;
  document.head.appendChild(style);
}

function TerminalMessage({ text, sender, typewriter }) {
  const [displayed, setDisplayed] = useState(typewriter ? "" : text);
  useEffect(() => {
    if (!typewriter) return;
    let i = 0;
    const interval = setInterval(() => {
      setDisplayed(text.slice(0, i + 1));
      i++;
      if (i >= text.length) clearInterval(interval);
    }, 12);
    return () => clearInterval(interval);
  }, [text, typewriter]);
  return (
    <div
      style={{
        ...typewriterStyle,
        color: sender === "user" ? "#00ff66" : "#00ff00",
        alignSelf: sender === "user" ? "flex-end" : "flex-start",
        marginBottom: 4,
        maxWidth: "98%",
        fontWeight: sender === "user" ? 600 : 500,
        textShadow: sender === "user" ? "0 0 2px #00ff66" : "0 0 2px #00ff00",
      }}
    >
      {displayed}
      {typewriter && displayed.length < text.length && <span style={blinkStyle}>█</span>}
    </div>
  );
}

export default function ChatBox() {
  const [messages, setMessages] = useState([]); // {sender, text}
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const chatRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    setMessages((msgs) => [...msgs, { sender: "user", text: input }]);
    setLoading(true);
    setError("");
    const userMsg = input;
    setInput("");
    try {
      const res = await fetch("/api/echo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg }),
      });
      if (!res.ok) throw new Error("Network response was not ok");
      const data = await res.json();
      setMessages((msgs) => [
        ...msgs,
        { sender: "assistant", text: data.response, typewriter: true },
      ]);
    } catch {
      setMessages((msgs) => [
        ...msgs,
        { sender: "assistant", text: "[Echo] Backend unavailable. Please try again.", typewriter: false },
      ]);
      setError("Backend unavailable");
    } finally {
      setLoading(false);
      inputRef.current && inputRef.current.focus();
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", width: "100%" }}>
      <div ref={chatRef} style={terminalStyle}>
        {messages.length === 0 && (
          <div style={{ color: "#00800099", opacity: 0.6, fontStyle: "italic", marginBottom: 12 }}>
            Welcome to <span style={{ color: "#00ff66" }}>Echo Terminal</span>. Type your message below.
          </div>
        )}
        {messages.map((msg, i) => (
          <TerminalMessage key={i} text={msg.text} sender={msg.sender === "assistant" ? "assistant" : "user"} typewriter={msg.typewriter && msg.sender === "assistant"} />
        ))}
        {loading && (
          <div style={{ color: "#00ff00", opacity: 0.7, fontStyle: "italic", marginTop: 8 }}>Echo is thinking<span style={blinkStyle}>█</span></div>
        )}
      </div>
      <form onSubmit={sendMessage} style={inputRowStyle}>
        <span style={{ color: "#00ff00", fontWeight: 700, marginRight: 8 }}>&gt;</span>
        <input
          ref={inputRef}
          style={inputStyle}
          type="text"
          autoComplete="off"
          value={input}
          onChange={e => setInput(e.target.value)}
          disabled={loading}
          placeholder="Type and hit Enter..."
        />
        <button type="submit" style={sendBtnStyle} disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
