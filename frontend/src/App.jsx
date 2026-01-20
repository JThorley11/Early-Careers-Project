import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function Home() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [chats, setChats] = useState([
    {
      title: "Urban flooding solutions",
      summary: "Explored green roofs, rain gardens, and permeable pavements as mitigation strategies.",
      results: [
        { id: 1, name: "Rain Garden Project", location: "Downtown", area: 500, description: "Community rain garden initiative", priority: "high", currentIssues: ["water pooling"], suitableSolutions: ["permeable pavement"] },
        { id: 2, name: "Green Roof Pilot", location: "City Hall", area: 300, description: "Pilot green roof project", priority: "medium", currentIssues: ["roof maintenance"], suitableSolutions: ["green roof installation"] },
      ],
    },
    {
      title: "Heat island study",
      summary: "Investigated tree planting and reflective surfaces to reduce urban heat islands.",
      results: [
        { id: 3, name: "Downtown Tree Planting", location: "Central Ave", area: 800, description: "Tree planting along streets", priority: "high", currentIssues: ["soil quality"], suitableSolutions: ["tree planting"] },
        { id: 4, name: "Reflective Roofs", location: "Warehouse District", area: 1200, description: "Install reflective roofing to reduce heat absorption", priority: "medium", currentIssues: ["budget constraints"], suitableSolutions: ["reflective surfaces"] },
      ],
    },
    {
      title: "Community garden ideas",
      summary: "Reviewed potential locations and suitable crops for urban community gardens.",
      results: [
        { id: 5, name: "Rooftop Garden Pilot", location: "West Side", area: 200, description: "Rooftop garden for vegetables", priority: "low", currentIssues: ["accessibility"], suitableSolutions: ["container gardens"] },
      ],
    },
  ]);

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);

  async function handleSearch() {
    if (!query.trim()) {
      setError("Please enter a search query");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) throw new Error("Search failed");

      const data = await response.json();
      
      // Move search bar up and show results
      setHasSearched(true); 
      setSummary(data.summary || "");
      setResults(data.results || []);
      setChats([{ title: query, summary: data.summary, results: data.results }, ...chats]);
    } catch (err) {
      setError("An error occurred while searching. Please try again.");
      console.error("Search error:", err);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyPress(e) {
    if (e.key === "Enter") handleSearch();
  }

  function handleNewChat() {
    setQuery("");
    setResults([]);
    setSummary("");
    setError(null);
    setHasSearched(false);
  }

  return (
    <div className="relative min-h-screen font-sans bg-[#E6F2EA] text-[#1F2937] flex flex-col w-full">
      {/* Sidebar overlay */}
      <motion.div
        animate={{ width: sidebarOpen ? 256 : 0 }}
        className="fixed top-0 left-0 h-full flex flex-col bg-[#f2f2e6] border-r border-gray-200 overflow-hidden z-50"
        transition={{ type: "spring", stiffness: 200, damping: 25 }}
      >
        {sidebarOpen && (
          <>
            <h2 className="p-4 font-bold text-lg border-b border-gray-200">Chats</h2>
            <ul className="flex-1 flex flex-col gap-2 p-2 overflow-y-auto">
              {chats.map((chat, idx) => (
                <li
                  key={idx}
                  className="p-2 rounded hover:bg-[#eeeed2] cursor-pointer"
                  onClick={() => {
                    setSummary(chat.summary);
                    setResults(chat.results);
                    setQuery("");
                    setError(null);
                    setHasSearched(true); // Move bar up when viewing history
                  }}
                >
                  {chat.title}
                </li>
              ))}
            </ul>

            <button
              onClick={toggleSidebar}
              className="absolute top-4 right-0 transition-all duration-300 p-2 bg-gray-200 hover:bg-gray-300 rounded-l z-50"
            >
              ←
            </button>
          </>
        )}
      </motion.div>

      {/* Sidebar toggle button when closed */}
      {!sidebarOpen && (
        <button
          onClick={toggleSidebar}
          className="fixed top-4 left-0 z-50 p-2 bg-gray-200 hover:bg-gray-300 rounded-r"
        >
          →
        </button>
      )}

      {/* Main content */}
      <main 
        className={`flex-1 flex flex-col items-center px-8 w-full transition-all duration-700 ease-in-out ${
          hasSearched ? "pt-12 justify-start" : "justify-center"
        }`}
      >
        {/* Animated Header & Search Container */}
        <motion.div 
          layout
          transition={{ type: "spring", stiffness: 100, damping: 20 }}
          className="w-full max-w-3xl flex flex-col items-center gap-8"
        >
          {/* Logo + Header */}
          <div className="flex items-center gap-4">
            <img src="/plant-bot-removebg.png" alt="RhizAgain logo" className="w-24 h-24" />
            <div>
              <h1 className="text-3xl font-semibold tracking-tight">GreenIQ</h1>
              {!hasSearched && (
                <motion.p 
                  initial={{ opacity: 1 }} 
                  exit={{ opacity: 0 }}
                  className="text-lg text-black"
                >
                  Harvest insights, grow sustainable impact.
                </motion.p>
              )}
            </div>
          </div>

          {/* Search bar group */}
          <div className="w-full flex gap-2">
            <input
              placeholder="Type your question here..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyPress}
              className="flex-1 rounded-lg border border-black p-3 text-black bg-[#F9FAF8] focus:outline-none focus:ring-2 focus:ring-green-500"
            />
            
            <button
              className="flex h-12 items-center justify-center gap-2 rounded-lg bg-[#2F855A] px-6 text-[#F9FAF8] transition-colors hover:bg-[#276749] disabled:bg-gray-400 disabled:cursor-not-allowed"
              onClick={handleSearch}
              disabled={loading}
            >
              {loading ? "Searching" : "Search"}
            </button>

            <button
              className="flex h-12 items-center justify-center gap-2 rounded-lg bg-[#D69E2E] px-6 text-[#F9FAF8] transition-colors hover:bg-[#b67b07]"
              onClick={handleNewChat}
            >
              New Chat
            </button>
          </div>
        </motion.div>

        {/* Results Area */}
        <div className="w-full max-w-3xl mt-8">
          <AnimatePresence>
            {hasSearched && !loading && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.4, delay: 0.3 }}
              >
                {/* Error message */}
                {error && (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg mb-4">
                    <p className="text-red-800">{error}</p>
                  </div>
                )}

                {/* Summary */}
                {summary && (
                  <div className="p-4 mb-8 border-gray-200 rounded-lg bg-[#F9FAF8] shadow-sm">
                    <h2 className="text-xl font-semibold mb-2 text-black text-center">Summary</h2>
                    <p className="text-gray-800 text-center">{summary}</p>
                  </div>
                )}

                {/* Search Results */}
                {results.length > 0 && (
                  <div className="pb-12">
                    <h2 className="text-2xl font-semibold mb-4 text-black">
                      Search Results ({results.length})
                    </h2>
                    <div className="space-y-4">
                      {results.map((result) => (
                        <div
                          key={result.id}
                          className="p-6 border border-gray-200 rounded-lg hover:shadow-lg transition-shadow bg-[#F9FAF8]"
                        >
                          <div className="flex justify-between items-center mb-3">
                            <h3 className="text-xl font-semibold text-black">{result.name}</h3>
                            <span
                              className={`px-3 py-1 rounded-full text-xs font-medium ${
                                result.priority === "high"
                                  ? "bg-red-100 text-red-800"
                                  : result.priority === "medium"
                                  ? "bg-yellow-100 text-yellow-800"
                                  : "bg-green-100 text-green-800"
                              }`}
                            >
                              {result.priority.toUpperCase()} PRIORITY
                            </span>
                          </div>

                          <p className="text-sm text-zinc-500 mb-2">
                            📍 {result.location} {result.area ? " • " + result.area.toLocaleString() + " m²" : null}
                          </p>
                          <p className="text-zinc-700 mb-4">{result.description}</p>

                          {result.currentIssues && (
                            <div className="mb-3">
                              <h4 className="text-sm font-semibold text-zinc-800 mb-2">Current Issues:</h4>
                              <div className="flex flex-wrap gap-2">
                                {result.currentIssues?.map((issue, idx) => (
                                  <span key={idx} className="px-2 py-1 bg-red-50 text-red-700 text-xs rounded">
                                    {issue}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}

                          {result.suitableSolutions && (
                            <div className="mb-3">
                              <h4 className="text-sm font-semibold text-zinc-800 mb-2">Suitable Solutions:</h4>
                              <div className="flex flex-wrap gap-2">
                                {result.suitableSolutions?.map((solution, idx) => (
                                  <span key={idx} className="px-2 py-1 bg-green-50 text-green-700 text-xs rounded">
                                    {solution}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        
                        {result.relevanceScore && (
                          <div className="mt-3 pt-3 border-t border-gray-200">
                            <p className="text-xs text-zinc-500">
                              Relevance score: {(result.relevanceScore * 100).toFixed(1)}%
                            </p>
                          </div>
                        )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-auto pt-8 pb-4 text-center border-t border-gray-200">
        <p className="text-sm text-zinc-600">
          GreenIQ grows insights from past projects into a sustainable future.
        </p>
        <p className="text-xs text-zinc-600">A Team Green Spark Product</p>
      </footer>
    </div>
  );
}