import React, { useState, useEffect } from "react";

export default function ToolsPanel() {
  const [tools, setTools] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [toggles, setToggles] = useState({});

  // Fetch tools from backend
  useEffect(() => {
    const fetchTools = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/tools');
        if (!response.ok) throw new Error('Failed to fetch tools');
        const data = await response.json();
        setTools(data.tools || []);
        
        // Initialize toggles for all tools (default: false)
        const initialToggles = {};
        (data.tools || []).forEach(tool => {
          initialToggles[tool.name] = false;
        });
        setToggles(initialToggles);
      } catch (err) {
        console.error('Failed to fetch tools:', err);
        setError('Failed to load tools');
      } finally {
        setLoading(false);
      }
    };

    fetchTools();
  }, []);

  const toggleTool = (toolName) =>
    setToggles((prev) => ({ ...prev, [toolName]: !prev[toolName] }));

  if (loading) {
    return (
      <div className="flex flex-col h-full">
        <div className="text-lg font-bold tracking-widest mb-4 text-green-400 select-none font-mono">Tools</div>
        <div className="text-green-700 italic">Loading tools...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col h-full">
        <div className="text-lg font-bold tracking-widest mb-4 text-green-400 select-none font-mono">Tools</div>
        <div className="text-red-400 italic">{error}</div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="text-lg font-bold tracking-widest mb-4 text-green-400 select-none font-mono">
        Tools ({tools.length})
      </div>
      <div className="flex-1 flex flex-col gap-3 max-h-96 overflow-y-auto">
        {tools.length === 0 ? (
          <div className="text-green-700 italic">No tools available</div>
        ) : (
          tools.map((tool) => (
            <button
              key={tool.name}
              onClick={() => toggleTool(tool.name)}
              className={`flex items-center gap-3 px-4 py-2 rounded font-mono border border-green-700 focus:outline-none transition-colors text-left
                ${toggles[tool.name] ? "bg-green-950 text-green-200 font-bold border-green-400" : "bg-black text-green-400 hover:bg-green-900/20"}
              `}
              title={tool.description}
            >
              <span
                className={`inline-block w-4 h-4 rounded-full border-2 mr-2 flex-shrink-0 ${
                  toggles[tool.name]
                    ? "bg-green-400 border-green-300"
                    : "bg-transparent border-green-600"
                }`}
              ></span>
              <div className="flex-1 min-w-0">
                <div className="truncate">{tool.name}</div>
                {tool.category && (
                  <div className="text-xs text-green-600 truncate">
                    {tool.category}
                  </div>
                )}
                {tool.usage_count > 0 && (
                  <div className="text-xs text-green-700">
                    Used {tool.usage_count} times
                  </div>
                )}
              </div>
            </button>
          ))
        )}
      </div>
    </div>
  );
}
