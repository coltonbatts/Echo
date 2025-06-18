import React, { useState, useEffect } from "react";
import ChatBox from "./ChatBox";
import ModelsList from "./ModelsList";
import ToolsPanel from "./ToolsPanel";


export default function BlackGreenMockup() {
  // Live clock logic
  const [time, setTime] = useState(() => {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  });
  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date();
      setTime(now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-black min-h-screen min-w-full grid" style={{gridTemplateRows:'56px 1fr',gridTemplateColumns:'1fr 2fr 1fr'}}>
      {/* Header */}
      <div className="flex items-center px-6 border-b border-green-500 font-mono text-green-400 text-2xl font-extrabold tracking-widest uppercase h-14 bg-black col-span-3" style={{gridRow:1,gridColumn:'1 / span 3'}}>
        ECHO <span className="ml-4 text-base font-normal opacity-60">| LINUX HUB</span>
        <span className="flex-1" />
        <span className="text-lg font-bold tracking-widest">{time}</span>
      </div>

      {/* LLM Selector */}
      <div className="bg-black border border-green-500 p-3 m-0 min-w-0 min-h-0 font-mono text-green-400 flex flex-col justify-start" style={{gridRow:2,gridColumn:1,borderRadius:0}}>
        <ModelsList />
      </div>

      {/* Chat Terminal Center Pane */}
      <div className="bg-black border border-green-500 p-3 m-0 min-w-0 min-h-0 font-mono text-green-400 flex flex-col justify-end h-full" style={{gridRow:2,gridColumn:2,borderRadius:0,fontSize:13}}>
        <ChatBox />
      </div>

      {/* MCP Tools Panel */}
      <div className="bg-black border border-green-500 p-3 m-0 min-w-0 min-h-0 font-mono text-green-400 flex flex-col justify-start" style={{gridRow:2,gridColumn:3,borderRadius:0}}>
        <ToolsPanel />
      </div>
    </div>
  );
}
