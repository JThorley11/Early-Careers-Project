import { useState, useRef } from "react";
import Banner from "./components/Banner";

function App() {
  const [question, setQuestion] = useState("");
  const [chat, setChat] = useState([]);
  const [showFilters, setShowFilters] = useState(true);
  const [filters, setFilters] = useState({
    category: "",
    startDate: "",
    endDate: "",
  });

  const chatRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    const userMessage = { sender: "user", text: question };
    setChat((prev) => [...prev, userMessage]);
    setQuestion("");

    const botMessage = { sender: "bot", text: "" };
    setChat((prev) => [...prev, botMessage]);

    try {
      const res = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          filters, // ⬅️ SEND FILTERS TO BACKEND
        }),
      });

      const data = await res.json();

      setChat((prev) => {
        const updated = [...prev];
        updated[updated.length - 1].text = data.text;
        return updated;
      });
    } catch (err) {
      console.error(err);
    }

    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  };

  return (
    <>
      <Banner />

      <div className="max-w-5xl mx-auto mt-10 grid grid-cols-1 md:grid-cols-3 gap-6 min-h-[80vh]">

        {/* ---------- LEFT FILTER FORM ---------- */}
        <div className="p-4 border rounded-lg shadow h-fit">

        {/* Header */}
        <button
          className="w-full flex justify-between items-center font-bold text-lg mb-2"
          onClick={() => setShowFilters(!showFilters)}
        >
          Filters
          <span className="text-xl">{showFilters ? "−" : "+"}</span>
        </button>

        {/* Collapsible content */}
        {showFilters && (
          <div className="flex flex-col gap-3 mt-2">

            <select
              value={filters.category}
              onChange={(e) =>
                setFilters({ ...filters, category: e.target.value })
              }
              className="p-2 border rounded"
            >
              <option value="">All Categories</option>
              <option value="gi">GI</option>
              <option value="iwr">IWR</option>
              <option value="c&m">C&M</option>
            </select>

            <input
              type="date"
              value={filters.startDate}
              onChange={(e) =>
                setFilters({ ...filters, startDate: e.target.value })
              }
              className="p-2 border rounded"
            />

            <input
              type="date"
              value={filters.endDate}
              onChange={(e) =>
                setFilters({ ...filters, endDate: e.target.value })
              }
              className="p-2 border rounded"
            />

          </div>
        )}
      </div>

        {/* ---------- RIGHT CHAT BOX ---------- */}
        <div className="md:col-span-2 p-4 border rounded-lg shadow flex flex-col">

          {/* Chat messages */}
          <div className="flex-1 mb-4 space-y-2 overflow-y-auto" ref={chatRef}>
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

          {/* Input bar */}
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
      </div>
    </>
  );
}

export default App;