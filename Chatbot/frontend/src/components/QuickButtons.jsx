import React from "react";

export default function QuickButtons({ options, onSelect }) {
  return (
    <div className="quick-buttons">
      {options.map((option, idx) => (
        <button key={idx} onClick={() => onSelect(option.value)}>
          {option.label}
        </button>
      ))}
    </div>
  );
}
