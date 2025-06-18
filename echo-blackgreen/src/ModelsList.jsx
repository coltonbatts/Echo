import React, { useState } from "react";

const MODELS = [
  { id: "gpt-4", name: "GPT-4" },
  { id: "claude", name: "Claude" },
  { id: "gemini", name: "Gemini" },
  { id: "llama", name: "Llama" },
  { id: "mistral", name: "Mistral" },
];

export default function ModelsList() {
  const [selected, setSelected] = useState(MODELS[0].id);
  return (
    <div className="flex flex-col h-full">
      <div className="text-lg font-bold tracking-widest mb-4 text-green-400 select-none font-mono">Models</div>
      <div className="flex-1 flex flex-col gap-2">
        {MODELS.map((model) => (
          <button
            key={model.id}
            onClick={() => setSelected(model.id)}
            className={`w-full text-left px-4 py-2 rounded font-mono border border-green-700 focus:outline-none transition-colors
              ${selected === model.id ? "bg-green-950 text-green-200 font-bold border-green-400" : "bg-black text-green-400 hover:bg-green-900/20"}
            `}
          >
            {model.name}
          </button>
        ))}
      </div>
    </div>
  );
}
