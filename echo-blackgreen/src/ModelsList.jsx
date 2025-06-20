import React, { useState, useEffect } from "react";

export default function ModelsList() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/tools/stats');
        if (!response.ok) throw new Error('Failed to fetch stats');
        const data = await response.json();
        setStats(data);
      } catch (err) {
        console.error('Failed to fetch stats:', err);
        setError('Failed to load statistics');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
    // Refresh stats every 30 seconds
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col h-full">
        <div className="text-lg font-bold tracking-widest mb-4 text-green-400 select-none font-mono">System</div>
        <div className="text-green-700 italic">Loading stats...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col h-full">
        <div className="text-lg font-bold tracking-widest mb-4 text-green-400 select-none font-mono">System</div>
        <div className="text-red-400 italic">{error}</div>
      </div>
    );
  }

  const serverStats = stats?.server_stats?.servers || {};
  const toolStats = stats?.server_stats?.tools || {};
  const selectionStats = stats?.selection_stats || {};

  return (
    <div className="flex flex-col h-full">
      <div className="text-lg font-bold tracking-widest mb-4 text-green-400 select-none font-mono">System</div>
      <div className="flex-1 overflow-y-auto space-y-4">
        {/* MCP Servers */}
        <div>
          <div className="text-sm font-bold text-green-300 mb-2 font-mono">MCP Servers</div>
          <div className="space-y-2">
            {Object.entries(serverStats).map(([serverUrl, serverInfo]) => (
              <div key={serverUrl} className="bg-gray-900/50 p-2 rounded border border-green-800">
                <div className="flex items-center gap-2">
                  <span className={`inline-block w-2 h-2 rounded-full ${
                    serverInfo.healthy ? 'bg-green-400' : 'bg-red-400'
                  }`}></span>
                  <span className="text-green-200 text-xs font-mono truncate flex-1">
                    {serverUrl.replace('http://', '').replace('https://', '')}
                  </span>
                </div>
                {serverInfo.response_time && (
                  <div className="text-green-600 text-xs mt-1">
                    {Math.round(serverInfo.response_time)}ms
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Tool Statistics */}
        <div>
          <div className="text-sm font-bold text-green-300 mb-2 font-mono">Tools</div>
          <div className="bg-gray-900/50 p-2 rounded border border-green-800">
            <div className="text-green-200 text-xs font-mono">
              Total: {toolStats.total_count || 0}
            </div>
            {toolStats.by_category && Object.keys(toolStats.by_category).length > 0 && (
              <div className="mt-2">
                <div className="text-green-600 text-xs mb-1">By Category:</div>
                {Object.entries(toolStats.by_category).map(([category, count]) => (
                  <div key={category} className="text-green-400 text-xs flex justify-between">
                    <span>{category || 'Unknown'}:</span>
                    <span>{count}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Most Used Tools */}
        {toolStats.most_used && toolStats.most_used.length > 0 && (
          <div>
            <div className="text-sm font-bold text-green-300 mb-2 font-mono">Most Used</div>
            <div className="space-y-1">
              {toolStats.most_used.slice(0, 5).map((tool, idx) => (
                <div key={idx} className="bg-gray-900/50 p-2 rounded border border-green-800">
                  <div className="text-green-200 text-xs font-mono truncate">
                    {tool.name}
                  </div>
                  <div className="text-green-600 text-xs">
                    Used {tool.usage_count} times
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Selection Statistics */}
        {selectionStats && Object.keys(selectionStats).length > 0 && (
          <div>
            <div className="text-sm font-bold text-green-300 mb-2 font-mono">AI Selection</div>
            <div className="bg-gray-900/50 p-2 rounded border border-green-800">
              {selectionStats.total_selections && (
                <div className="text-green-200 text-xs font-mono">
                  Selections: {selectionStats.total_selections}
                </div>
              )}
              {selectionStats.avg_confidence && (
                <div className="text-green-400 text-xs">
                  Avg Confidence: {Math.round(selectionStats.avg_confidence * 100)}%
                </div>
              )}
              {selectionStats.success_rate && (
                <div className="text-green-400 text-xs">
                  Success Rate: {Math.round(selectionStats.success_rate * 100)}%
                </div>
              )}
            </div>
          </div>
        )}

        {/* Last Updated */}
        <div className="text-green-700 text-xs opacity-60 font-mono">
          Updated: {new Date(stats?.timestamp * 1000).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
}
