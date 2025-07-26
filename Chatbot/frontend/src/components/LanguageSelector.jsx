import React from "react";

export default function LanguageSelector({ onSelect }) {
  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h2>Hello, choose your language</h2>
      <button onClick={() => onSelect("english")}>English</button>
      <button onClick={() => onSelect("hinglish")}>Hinglish</button>
    </div>
  );
}
