import React from "react";

export default function MessageBubble({ text, sender }) {
  return <div className={`message ${sender}`}>{text}</div>;
}
