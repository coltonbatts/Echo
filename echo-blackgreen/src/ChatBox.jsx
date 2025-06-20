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

function ToolUsageDisplay({ tool }) {
  return (
    <div className="mb-2 px-3 py-2 rounded bg-green-950/50 text-green-300 text-xs font-mono border border-green-800 max-w-[90%] mr-auto">
      <div className="flex items-center gap-2 mb-1">
        <span className="inline-block w-2 h-2 bg-green-400 rounded-full"></span>
        <span className="font-semibold text-green-200">Tool: {tool.name}</span>
        {tool.execution_time && (
          <span className="text-green-600">({tool.execution_time}ms)</span>
        )}
      </div>
      {tool.parameters && Object.keys(tool.parameters).length > 0 && (
        <div className="text-green-600 mb-1">
          Params: {JSON.stringify(tool.parameters, null, 0)}
        </div>
      )}
      {tool.result && (
        <div className="text-green-400 break-words">
          Result: {typeof tool.result === 'string' ? tool.result : JSON.stringify(tool.result, null, 2)}
        </div>
      )}
      {tool.confidence && (
        <div className="text-green-600 mt-1">
          Confidence: {Math.round(tool.confidence * 100)}%
        </div>
      )}
    </div>
  );
}

function ToolErrorDisplay({ error }) {
  return (
    <div className="mb-2 px-3 py-2 rounded bg-red-950/50 text-red-300 text-xs font-mono border border-red-800 max-w-[90%] mr-auto">
      <div className="flex items-center gap-2 mb-1">
        <span className="inline-block w-2 h-2 bg-red-400 rounded-full"></span>
        <span className="font-semibold text-red-200">Tool Error: {error.name}</span>
      </div>
      <div className="text-red-400 break-words">
        {error.error}
      </div>
    </div>
  );
}

export default function ChatBox() {
  const [messages, setMessages] = useState([]); // {sender, text, tools_used?, tool_errors?}
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
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
        { 
          sender: "assistant", 
          text: data.response, 
          typewriter: true,
          tools_used: data.tools_used || [],
          tool_errors: data.tool_errors || [],
          processing_time: data.processing_time,
          model_used: data.model_used
        },
      ]);
    } catch {
      setMessages((msgs) => [
        ...msgs,
        { sender: "assistant", text: "[Echo] Backend unavailable. Please try again.", typewriter: false },
      ]);
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
          <div key={i} className="mb-2">
            {/* Show tool usage before assistant response */}
            {msg.tools_used && msg.tools_used.length > 0 && (
              <div className="mb-2">
                {msg.tools_used.map((tool, idx) => (
                  <ToolUsageDisplay key={idx} tool={tool} />
                ))}
              </div>
            )}
            {/* Show tool errors if any */}
            {msg.tool_errors && msg.tool_errors.length > 0 && (
              <div className="mb-2">
                {msg.tool_errors.map((error, idx) => (
                  <ToolErrorDisplay key={idx} error={error} />
                ))}
              </div>
            )}
            {/* Main message */}
            <TerminalMessage 
              text={msg.text} 
              sender={msg.sender === "assistant" ? "assistant" : "user"} 
              typewriter={msg.typewriter && msg.sender === "assistant"} 
            />
            {/* Show processing time for assistant messages */}
            {msg.sender === "assistant" && msg.processing_time && (
              <div className="text-green-700 text-xs mt-1 opacity-60">
                Processed in {msg.processing_time}s
                {msg.model_used && ` using ${msg.model_used}`}
              </div>
            )}
          </div>
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
