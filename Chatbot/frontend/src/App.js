import React, { useState } from "react";
import Chatbot from "./components/Chatbot";
import "./App.css";

function App() {
  const [language, setLanguage] = useState("");

  if (!language) {
    return (
      <div className="language-select">
        <h2>Hello, choose your language</h2>
        <button onClick={() => setLanguage("english")}>English</button>
        <button onClick={() => setLanguage("hinglish")}>हinglish</button>
      </div>
    );
  }

  return (
    <div className="App">
      <Chatbot language={language} />
    </div>
  );
}

export default App;
