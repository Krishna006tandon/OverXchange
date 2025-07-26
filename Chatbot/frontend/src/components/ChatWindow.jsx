import React, { useState, useEffect } from "react";
import axios from "axios";
import MessageBubble from "./MessageBubble";
import QuickButtons from "./QuickButtons";

export default function ChatWindow({ language }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [showOptions, setShowOptions] = useState(true);

  useEffect(() => {
    axios.post("http://127.0.0.1:5000/chat/language", { language });
    addBotMessage(language === "english" ? "How can I help you?" : "Main aapki kaise madad karu?");
  }, [language]);

  const addBotMessage = (text) => setMessages((prev) => [...prev, { text, sender: "bot" }]);
  const addUserMessage = (text) => setMessages((prev) => [...prev, { text, sender: "user" }]);

  const handleOption = async (value) => {
    setShowOptions(false);

    if (value === "vendor") {
      const res = await axios.get("http://127.0.0.1:5000/chat/vendors");
      if (res.data.vendors.length === 0) {
        addBotMessage(language === "english" ? "No vendors found!" : "Koi vendor nahi mila!");
      } else {
        addBotMessage(language === "english" ? "Here are some vendors:" : "Yeh rahe kuch vendors:");
        res.data.vendors.forEach((v) =>
          addBotMessage(`${v.name} - ${v.location} - ${v.phone}`)
        );}}}}
