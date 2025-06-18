import React, { useState } from "react";

const TOOLS = [
  { id: "weatherTool", name: "weatherTool" },
  { id: "calendarTool", name: "calendarTool" },
  { id: "scriptRunner", name: "scriptRunner" },
  { id: "notifier", name: "notifier" },
  { id: "fileSync", name: "fileSync" },
];

export default function ToolsPanel() {
  const [toggles, setToggles] = useState(
    Object.fromEntries(TOOLS.map((t) => [t.id, false]))
  );
  const toggleTool = (id) =>
    setToggles((prev) => ({ ...prev, [id]: !prev[id] }));

  return (
    <div className="flex flex-col h-full">
      <div className="text-lg font-bold tracking-widest mb-4 text-green-400 select-none font-mono">Tools</div>
      <div className="flex-1 flex flex-col gap-3">
        {TOOLS.map((tool) => (
          <button
            key={tool.id}
            onClick={() => toggleTool(tool.id)}
            className={`flex items-center gap-3 px-4 py-2 rounded font-mono border border-green-700 focus:outline-none transition-colors
              ${toggles[tool.id] ? "bg-green-950 text-green-200 font-bold border-green-400" : "bg-black text-green-400 hover:bg-green-900/20"}
            `}
          >
            <span
              className={`inline-block w-4 h-4 rounded-full border-2 mr-2 ${
                toggles[tool.id]
                  ? "bg-green-400 border-green-300"
                  : "bg-transparent border-green-600"
              }`}
            ></span>
            {tool.name}
          </button>
        ))}
      </div>
    </div>
  );
}
