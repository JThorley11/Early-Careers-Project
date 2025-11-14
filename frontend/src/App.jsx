import { useState, useRef } from "react";

function App() {
  const [question, setQuestion] = useState("");
  const [chat, setChat] = useState([]);
  const chatRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    // Add user message
    const userMessage = { sender: "user", text: question };
    setChat((prev) => [...prev, userMessage]);

    setQuestion("");

    // Add placeholder bot message
    const botMessage = { sender: "bot", text: "" };
    setChat((prev) => [...prev, botMessage]);

    // Send POST request to backend
    try {
      const res = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      const data = await res.json();

      // Update last bot message
      setChat((prev) => {
        const updated = [...prev];
        updated[updated.length - 1].text = data.text;
        return updated;
      });
    } catch (err) {
      console.error(err);
    }

    // Scroll chat into view
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  };

  return (
    <div className="max-w-xl mx-auto mt-10 p-4 border rounded-lg shadow">
      <div className="mb-4 space-y-2 h-96 overflow-y-auto" ref={chatRef}>
        {chat.map((msg, idx) => (
          <div
            key={idx}
            className={msg.sender === "user" ? "text-right" : "text-left"}
          >
            <span
              className={`inline-block p-2 rounded-lg ${
                msg.sender === "user"
                  ? "bg-blue-500 text-white"
                  : "bg-gray-200 text-black"
              }`}
            >
              {msg.text}
            </span>
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          className="flex-1 p-2 border rounded"
          placeholder="Ask me anything..."
        />
        <button type="submit" className="bg-blue-500 text-white p-2 rounded">
          Send
        </button>
      </form>
    </div>
  );
}

export default App;