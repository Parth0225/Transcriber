import { useState, useEffect, FormEvent } from "react";
import { api } from "@/lib/api";

type Transcript = {
  id: string;
  title: string;
  date: string; // ISO string
  language: string;
};

export default function SearchPage() {
  const [transcripts, setTranscripts] = useState<Transcript[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [title, setTitle] = useState("");
  const [date, setDate] = useState("");
  const [language, setLanguage] = useState("");

  const fetchTranscripts = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api<Transcript[]>("/transcripts");
      setTranscripts(data);
    } catch (e: any) {
      setError(e.message ?? "Failed to load transcripts");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTranscripts();
  }, []);

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault();
    if (!title || !date || !language) return;
    setError(null);
    try {
      const newItem = await api<Transcript>("/transcripts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, date, language }),
      });
      setTranscripts((prev) => [...prev, newItem]);
      setTitle("");
      setDate("");
      setLanguage("");
    } catch (e: any) {
      setError(e.message ?? "Failed to create transcript");
    }
  };

  const handleDelete = async (id: string) => {
    setError(null);
    try {
      await api<void>(`/transcripts/${id}`, { method: "DELETE" });
      setTranscripts((prev) => prev.filter((t) => t.id !== id));
    } catch (e: any) {
      setError(e.message ?? "Failed to delete transcript");
    }
  };

  return (
    <main className="max-w-4xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Transcripts</h1>

      {/* Create Form */}
      <section className="mb-6 p-4 border rounded bg-gray-50">
        <h2 className="text-xl font-semibold mb-2">Add New Transcript</h2>
        <form onSubmit={handleCreate} className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700">
              Title
            </label>
            <input
              id="title"
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="mt-1 block w-full rounded border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label htmlFor="date" className="block text-sm font-medium text-gray-700">
              Date
            </label>
            <input
              id="date"
              type="datetime-local"
              required
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="mt-1 block w-full rounded border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label htmlFor="language" className="block text-sm font-medium text-gray-700">
              Language (ISO code)
            </label>
            <input
              id="language"
              type="text"
              required
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="mt-1 block w-full rounded border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
          </div>
          <div className="md:col-span-3 flex justify-end">
            <button
              type="submit"
              className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              Add Transcript
            </button>
          </div>
        </form>
      </section>

      {/* Loading / Error */}
      {loading && <p className="text-gray-600">Loading transcripts...</p>}
      {error && <p className="text-red-600">{error}</p>}

      {/* List */}
      {!loading && transcripts.length === 0 && (
        <p className="text-gray-600">No transcripts found.</p>
      )}

      <ul className="space-y-4">
        {transcripts.map((t) => (
          <li key={t.id} className="p-4 border rounded bg-white flex justify-between items-start">
            <div>
              <h3 className="text-lg font-medium">{t.title}</h3>
              <p className="text-sm text-gray-500">
                {new Date(t.date).toLocaleString()} • {t.language}
              </p>
            </div>
            <button
              onClick={() => handleDelete(t.id)}
              className="text-sm text-red-600 hover:underline"
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
    </main>
  );
}
