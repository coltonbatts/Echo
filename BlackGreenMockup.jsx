import React from "react";

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
  return (
    <div style={{
      background: "#101010",
      minHeight: "100vh",
      minWidth: "100vw",
      display: "grid",
      gridTemplateColumns: "1fr 1.2fr 1fr",
      gridTemplateRows: "0.7fr 1.3fr 0.7fr",
      gap: "0.7rem",
      padding: "2rem",
      position: "relative",
    }}>
      {/* Shell info */}
      <div style={{ ...paneStyle, gridColumn: 1, gridRow: 1 }}>
        <div style={{ fontWeight: 700, letterSpacing: 1 }}>shell <span style={{ color: "#00ff66" }}>zsh</span></div>
        <div>wm <span style={{ color: "#00ff66" }}>herbstluftwm</span></div>
        <div>distro <span style={{ color: "#00ff66" }}>Ubuntu 17.04</span></div>
        <div style={{ marginTop: 10, fontSize: 12 }}>l-r &lt;--&gt; NerdyPepper</div>
      </div>

      {/* Digital clock */}
      <div style={{ ...paneStyle, gridColumn: 2, gridRow: 1, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "4rem", fontWeight: 700, letterSpacing: 2 }}>
        22:04
      </div>

      {/* Editor/terminal mock */}
      <div style={{ ...paneStyle, gridColumn: 1, gridRow: "2 / span 2", fontSize: 13, whiteSpace: "pre", overflow: "auto" }}>
        {`#!/bin/bash
# nerdinfo.sh - by yours truly
# ...
color-echo() {
  # print with colors
  echo -e "\033[1;32m$1\033[0m"
}
color-echo 'shell' 'zsh'
color-echo 'wm' 'herbstluftwm'
color-echo 'distro' 'Ubuntu 17.04'
`}
      </div>

      {/* Python mock */}
      <div style={{ ...paneStyle, gridColumn: 2, gridRow: 2, fontSize: 13, whiteSpace: "pre", overflow: "auto" }}>
        {`import os
cmd = os.popen('playerctl -p spotify status').read()
if 'Playing' in cmd:
    print('▶')
elif 'Paused' in cmd:
    print('‖')
else:
    print('■')`}
      </div>

      {/* File tree mock */}
      <div style={{ ...paneStyle, gridColumn: 3, gridRow: 1, fontSize: 13 }}>
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

      {/* Histogram mock */}
      <div style={{ ...paneStyle, gridColumn: 2, gridRow: 3, gridColumnEnd: 4, display: "flex", alignItems: "flex-end", justifyContent: "center", minHeight: 80 }}>
        {/* ASCII bar chart */}
        <pre style={{ margin: 0, color: "#00ff00", fontSize: 20, lineHeight: 1, letterSpacing: 2 }}>{`
  ▂▃▅▇█▇▅▃▂
`}</pre>
      </div>
      {/* Grain overlay */}
      <div style={grainOverlay}></div>
    </div>
  );
}
