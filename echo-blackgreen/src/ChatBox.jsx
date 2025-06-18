import React, { useState, useRef, useEffect } from "react";


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
    <div className="flex flex-col h-full w-full">
      <div
        ref={chatRef}
        className="bg-black text-green-400 font-mono border border-green-500 px-5 py-4 min-h-[320px] max-h-[420px] overflow-y-auto flex flex-col justify-end whitespace-pre-wrap"
        style={{margin:0}}
      >
        {messages.length === 0 && (
          <div className="text-green-700 italic mb-3 opacity-70">
            Welcome to <span className="text-green-400">Echo Terminal</span>. Type your message below.
          </div>
        )}
        {messages.map((msg, i) => (
          <TerminalMessage key={i} text={msg.text} sender={msg.sender === "assistant" ? "assistant" : "user"} typewriter={msg.typewriter && msg.sender === "assistant"} />
        ))}
        {loading && (
          <div className="text-green-400 italic mt-2 opacity-80">Echo is thinking<span style={blinkStyle}>█</span></div>
        )}
      </div>
      <form onSubmit={sendMessage} className="flex items-center w-full mt-3 border-t border-green-500 pt-3">
        <span className="text-green-400 font-bold mr-2">&gt;</span>
        <input
          ref={inputRef}
          className="flex-1 bg-black text-green-400 font-mono border-0 outline-none text-base px-2 py-1 caret-green-400 tracking-wider"
          type="text"
          autoComplete="off"
          value={input}
          onChange={e => setInput(e.target.value)}
          disabled={loading}
          placeholder="Type and hit Enter..."
        />
        <button
          type="submit"
          className="ml-3 bg-green-900 text-green-200 font-mono font-bold px-4 py-1 border border-green-700 hover:bg-green-800 disabled:opacity-40"
          disabled={loading || !input.trim()}
        >
          Send
        </button>
      </form>
    </div>
  );
}
