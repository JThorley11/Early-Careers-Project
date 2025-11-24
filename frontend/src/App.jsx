import { useState } from "react";


export default function Home() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error("Search failed");
      }

      const data = await response.json();
      setSummary(data.summary || "");
      setResults(data.results || []);
    } catch (err) {
      setError("An error occurred while searching. Please try again.");
      console.error("Search error:", err);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyPress(e) {
    if (e.key === "Enter") {
      handleSearch();
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center font-sans bg-[#FFD902] text-[#171717]">
      <main className="flex min-h-screen w-full max-w-3xl flex-col items-centre gap-8 py-12 px-8">
        <div className="flex items-center gap-4">
          <img
            src="/plant-bot-yellow.png"
            alt="RhizAgain logo"
            className="w-36 h-36"
          />
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">RhizAgain</h1>
            <p className="text-lg text-black">
              Get to the root of urban nature challenges with AI insights.
            </p>
          </div>
        </div>

        <div className="w-full">
          <div className="flex gap-2">
            <input
              placeholder="Type your question here... (e.g., 'flooding solutions' or 'heat island')"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyPress}
              className="flex-1 rounded-lg border border-black p-3 text-black bg-white focus:outline-none focus:ring-2 focus:ring-green-500"
            />
            <button
              className="flex h-12 items-center justify-center gap-2 rounded-lg bg-[#191D64] px-6 text-white transition-colors hover:bg-[#0f1340] disabled:bg-gray-400 disabled:cursor-not-allowed"
              onClick={handleSearch}
              disabled={loading}
            >
              {loading ? "Searching..." : "Search"}
            </button>
          </div>

          {error && (
            <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-red-800 dark:text-red-200">{error}</p>
            </div>
          )}
        </div>
        
        {summary && (
          <div className="mb-2 p-4 border-gray-200 dark:border-zinc-700 rounded-lg hover:shadow-lg transition-shadow bg-white dark:bg-zinc-900 text-center">
            <h2 className="text-xl font-semibold mb-2 text-black dark:text-zinc-50">Summary</h2>
            <p className="text-gray-800 dark:text-gray-200">{summary}</p>
          </div>
        )}

        {results.length > 0 && (
          <div className="w-full">
            <h2 className="text-2xl font-semibold mb-4 text-black dark:text-zinc-50">
              Search Results ({results.length})
            </h2>
            <div className="space-y-4">
              {results.map((result) => (
                <div
                  key={result.id}
                  className="p-6 border border-gray-200 dark:border-zinc-700 rounded-lg hover:shadow-lg transition-shadow bg-white dark:bg-zinc-900"
                >
                  <div className="flex justify-between items-centre mb-3">
                    <h3 className="text-xl font-semibold text-black dark:text-zinc-50">
                      {result.name}
                    </h3>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${
                        result.priority === "high"
                          ? "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-200"
                          : result.priority === "medium"
                          ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-200"
                          : "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200"
                      }`}
                    >
                      {result.priority.toUpperCase()} PRIORITY
                    </span>
                  </div>

                  <p className="text-sm text-zinc-500 dark:text-zinc-400 mb-2">
                    📍 {result.location} • {result.area.toLocaleString()} m²
                  </p>

                  <p className="text-zinc-700 dark:text-zinc-300 mb-4">
                    {result.description}
                  </p>

                  <div className="mb-3">
                    <h4 className="text-sm font-semibold text-zinc-800 dark:text-zinc-200 mb-2">
                      Current Issues:
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {result.currentIssues.map((issue, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 text-xs rounded"
                        >
                          {issue}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="mb-3">
                    <h4 className="text-sm font-semibold text-zinc-800 dark:text-zinc-200 mb-2">
                      Suitable Solutions:
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {result.suitableSolutions.map((solution, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300 text-xs rounded"
                        >
                          {solution}
                        </span>
                      ))}
                    </div>
                  </div>

                  {result.relevanceScore && (
                    <div className="mt-3 pt-3 border-t border-gray-200 dark:border-zinc-700">
                      <p className="text-xs text-zinc-500 dark:text-zinc-400">
                        Relevance score: {(result.relevanceScore * 100).toFixed(1)}%
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        <footer className="w-full mt-auto pt-8 pb-4 text-center border-t border-black-300">
          <p className="text-sm text-zinc-600">
            The word rhiza comes from the Greek word <em>rhíza</em> (ῥίζα),
            which means &ldquo;root&rdquo;.
          </p>
          <p className="text-xs text-zinc-600">
            A Team Green Spark   Product
          </p>
        </footer>
      </main>
    </div>
  );
}