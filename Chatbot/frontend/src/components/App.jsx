import React, { useState } from "react";
import ChatWindow from "./components/ChatWindow";
import LanguageSelector from "./components/LanguageSelector";
import "./styles/chat.css";

export default function App() {
  const [language, setLanguage] = useState(null);

  return (
    <>
      {language ? (
        <ChatWindow language={language} />
      ) : (
        <LanguageSelector onSelect={setLanguage} />
      )}
    </>
  );
}
