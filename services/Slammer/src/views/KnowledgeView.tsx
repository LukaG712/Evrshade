// Knowledge view — search and browse stored knowledge

import { useState, useEffect, useCallback } from 'react';
import { api } from '../lib/api';

export default function KnowledgeView() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [memory, setMemory] = useState<any[]>([]);
  const [memoryLoading, setMemoryLoading] = useState(true);

  const fetchMemory = useCallback(async () => {
    try {
      const data = await api.getMemory();
      setMemory(data.entries || []);
    } catch {
      // Memory endpoint may not be available
    } finally {
      setMemoryLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMemory();
  }, [fetchMemory]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const data = await api.searchKnowledge(query);
      setResults(data.results || []);
    } catch (err: any) {
      setError(err.message);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold">Knowledge Base</h2>

      {/* Search */}
      <form onSubmit={handleSearch} className="flex gap-3">
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          className="flex-1 bg-gray-800 border border-gray-700 rounded-md px-4 py-2 text-sm focus:border-blue-500 outline-none"
          placeholder="Search knowledge base..."
        />
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-md text-sm"
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {error && (
        <div className="bg-red-900/30 border border-red-800 rounded-lg p-4 text-red-400">
          {error}
          <button onClick={() => setError(null)} className="ml-4 text-red-300">✕</button>
        </div>
      )}

      {/* Search results */}
      {results.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-sm text-gray-400">Search Results ({results.length})</h3>
          {results.map((result) => (
            <div key={result.id} className="bg-gray-800 rounded-lg border border-gray-700 p-4">
              <div className="flex items-start justify-between">
                <div>
                  <h4 className="font-medium">{result.title || 'Untitled'}</h4>
                  {result.source && (
                    <p className="text-xs text-gray-500 mt-1">Source: {result.source}</p>
                  )}
                </div>
                {result.score !== undefined && (
                  <span className="text-xs text-gray-500">Score: {result.score.toFixed(3)}</span>
                )}
              </div>
              <p className="text-sm text-gray-300 mt-2 line-clamp-3">{result.content}</p>
              {result.tags && result.tags.length > 0 && (
                <div className="flex gap-2 mt-3">
                  {result.tags.map((tag: string, i: number) => (
                    <span key={i} className="text-xs bg-gray-700 text-gray-300 px-2 py-0.5 rounded">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Memory entries */}
      <div>
        <h3 className="text-sm text-gray-400 mb-3">Memory Entries ({memory.length})</h3>
        {memoryLoading ? (
          <p className="text-gray-400 text-sm">Loading memory...</p>
        ) : memory.length === 0 ? (
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-8 text-center">
            <span className="text-3xl">🧠</span>
            <p className="text-gray-400 mt-3">No memory entries yet. Memory is populated as agents learn and store context.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {memory.slice(0, 20).map((entry) => (
              <div key={entry.id} className="bg-gray-800 rounded-lg border border-gray-700 p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="font-medium text-sm">{entry.title || 'Untitled'}</h4>
                    {entry.source && (
                      <p className="text-xs text-gray-500 mt-1">Source: {entry.source}</p>
                    )}
                  </div>
                  <span className="text-xs text-gray-500">
                    {entry.createdAt ? new Date(entry.createdAt).toLocaleDateString() : ''}
                  </span>
                </div>
                <p className="text-sm text-gray-300 mt-2 line-clamp-2">{entry.content}</p>
              </div>
            ))}
            {memory.length > 20 && (
              <p className="text-center text-sm text-gray-500">Showing 20 of {memory.length} entries</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
