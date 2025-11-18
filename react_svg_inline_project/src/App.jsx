import React, { useEffect } from "react";

export default function App() {
  const svgString = `
    <svg width="300" height="200">
      <rect id="btn1" x="20" y="20" width="120" height="60" rx="12" fill="#00AAAA"/>
      <text x="40" y="60" font-size="20" fill="#fff">Click Me</text>
    </svg>
  `;

  useEffect(() => {
    const el = document.getElementById("btn1");
    if (el) {
      el.style.cursor = "pointer";
      el.addEventListener("click", () => alert("SVG 버튼 클릭됨!"));
    }
  }, []);

  return (
    <div>
      <h1>Inline SVG + Click Event</h1>
      <div dangerouslySetInnerHTML={{ __html: svgString }} />
    </div>
  );
}
