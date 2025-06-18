import React, { useState, useEffect } from "react";
import ChatBox from "./ChatBox";

const paneStyle = {
  background: "rgba(0,0,0,0.92)",
  border: "1.5px solid #00ff00",
  borderRadius: "6px",
  color: "#00ff00",
  fontFamily: "Fira Mono, JetBrains Mono, monospace",
  boxShadow: "0 0 8px #001a00",
  padding: "1rem",
  margin: "0.5rem",
  minHeight: "64px",
  minWidth: "120px",
  filter: "contrast(1.1) grayscale(0.2)",
  position: "relative",
  overflow: "hidden",
};

const grainOverlay = {
  pointerEvents: "none",
  position: "fixed",
  top: 0,
  left: 0,
  width: "100vw",
  height: "100vh",
  zIndex: 100,
  opacity: 0.12,
  background: "url('https://grainy-gradients.vercel.app/noise.svg') repeat",
};

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
    <div style={{
      background: "#101010",
      minHeight: "100vh",
      minWidth: "100vw",
      display: "grid",
      gridTemplateRows: "56px 1fr",
      gridTemplateColumns: "1fr 2fr 1fr",
      gap: "0.5rem",
      padding: "0",
      position: "relative",
    }}>
      {/* Header */}
      <div style={{
        gridRow: 1,
        gridColumn: "1 / span 3",
        display: "flex",
        alignItems: "center",
        padding: "0 1.5rem",
        borderBottom: "1.5px solid #00ff00",
        fontFamily: 'Fira Mono, JetBrains Mono, monospace',
        color: '#00ff00',
        fontSize: 24,
        fontWeight: 900,
        letterSpacing: 2,
        height: 56,
        background: "#101010",
      }}>
        Echo <span style={{ fontWeight: 400, fontSize: 16, marginLeft: 16, opacity: 0.5 }}>| Linux Hub</span>
        <span style={{ flex: 1 }} />
        <span style={{ fontSize: 20, fontWeight: 700, letterSpacing: 2 }}>{time}</span>
      </div>

      {/* System Info */}
      <div style={{ ...paneStyle, gridRow: 2, gridColumn: 1, minWidth: 0, minHeight: 0, margin: 0, borderRadius: 4, fontSize: 14 }}>
        <div style={{ fontWeight: 700, letterSpacing: 1 }}>shell <span style={{ color: "#00ff66" }}>zsh</span></div>
        <div>wm <span style={{ color: "#00ff66" }}>herbstluftwm</span></div>
        <div>distro <span style={{ color: "#00ff66" }}>Ubuntu 17.04</span></div>
      </div>

      {/* Chat Terminal Center Pane */}
      <div style={{ ...paneStyle, gridRow: 2, gridColumn: 2, minWidth: 0, minHeight: 0, margin: 0, borderRadius: 4, fontSize: 13, display: "flex", flexDirection: "column", justifyContent: "flex-end", height: "100%" }}>
        <ChatBox />
      </div>

      {/* File List */}
      <div style={{ ...paneStyle, gridRow: 2, gridColumn: 3, minWidth: 0, minHeight: 0, margin: 0, borderRadius: 4, fontSize: 13 }}>
        <div>hlws.py</div>
        <div style={{ color: "#00ff66" }}>nerdinfo.sh</div>
        <div>spot.py</div>
        <div>plpause.py</div>
        <div>weather.py</div>
        <div>watest.lua</div>
        <div>fuz.sh</div>
        <div>luac.out</div>
        <div>pipes.sh</div>
      </div>

      {/* Grain overlay */}
      <div style={grainOverlay}></div>
    </div>
  );
}
