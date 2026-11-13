import { useState, useEffect, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

type Transcript = {
  id: number;
  title: string;
  date: string;
  language: string;
};

type Line = {
  id: number;
  transcript_id: number;
  start_time: number;
  speaker?: string;
  text: string;
};

export default function TranscriptPage({
  params,
}: {
  params: { transcripts_id: string };
}) {
  const transcriptId = Number(params.transcripts_id);
  const router = useRouter();

  const [transcript, setTranscript] = useState<Transcript | null>(null);
  const [lines, setLines] = useState<Line[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [newText, setNewText] = useState("");
  const [newSpeaker, setNewSpeaker] = useState("");
  const [newStart, setNewStart] = useState("");

  const fetchData = async () => {
    try {
      setLoading(true);
      const [t, l] = await Promise.all([
        api<Transcript>(`/transcripts/${transcriptId}`),
        api<Line[]>(`/lines?transcript_id=${transcriptId}`),
      ]);
      setTranscript(t);
      setLines(l);
      setError(null);
    } catch (e: any) {
      setError(e.message ?? "Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [transcriptId]);

  const handleAdd = async (e: FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        transcript_id: transcriptId,
        start_time: parseFloat(newStart),
        speaker: newSpeaker || undefined,
        text: newText,
      };
      const created = await api<Line>("/lines", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      setLines((prev) => [...prev, created]);
      setNewText("");
      setNewSpeaker("");
      setNewStart("");
    } catch (e: any) {
      setError(e.message ?? "Failed to add line");
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this line?")) return;
    try {
      await api(`/lines/${id}`, { method: "DELETE" });
      setLines((prev) => prev.filter((l) => l.id !== id));
    } catch (e: any) {
      setError(e.message ?? "Failed to delete line");
    }
  };

  const handleDownload = () => {
    const content = lines
      .map(
        (l) =>
          `${l.start_time.toFixed(2)} ${l.speaker ? `[${l.speaker}] ` : ""}${l.text}`
      )
      .join("\n");
    const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${transcript?.title ?? "transcript"}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-gray-600">Loading transcript...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 max-w-2xl mx-auto">
        <p className="text-red-600">{error}</p>
        <button
          onClick={fetchData}
          className="mt-2 px-4 py-2 bg-blue-600 text-white rounded"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <main className="p-4 max-w-4xl mx-auto">
      <header className="mb-6">
        <h1 className="text-2xl font-bold">{transcript?.title}</h1>
        <p className="text-gray-500">{new Date(transcript?.date ?? "").toLocaleString()}</p>
        <button
          onClick={handleDownload}
          className="mt-2 px-4 py-2 bg-green-600 text-white rounded"
        >
          Download TXT
        </button>
      </header>

      {/* Add new line form */}
      <section className="mb-8 p-4 border rounded bg-gray-50">
        <h2 className="text-xl font-semibold mb-4">Add New Line</h2>
        <form onSubmit={handleAdd} className="grid gap-4">
          <div>
            <label htmlFor="start" className="block text-sm font-medium text-gray-700">
              Start Time (seconds)
            </label>
            <input
              id="start"
              type="number"
              step="0.01"
              required
              value={newStart}
              onChange={(e) => setNewStart(e.target.value)}
              className="mt-1 block w-full rounded border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
          <div>
            <label htmlFor="speaker" className="block text-sm font-medium text-gray-700">
              Speaker (optional)
            </label>
            <input
              id="speaker"
              type="text"
              value={newSpeaker}
              onChange={(e) => setNewSpeaker(e.target.value)}
              className="mt-1 block w-full rounded border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
          <div>
            <label htmlFor="text" className="block text-sm font-medium text-gray-700">
              Text
            </label>
            <textarea
              id="text"
              required
              rows={3}
              value={newText}
              onChange={(e) => setNewText(e.target.value)}
              className="mt-1 block w-full rounded border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
          <button
            type="submit"
            className="self-start px-4 py-2 bg-blue-600 text-white rounded"
          >
            Add Line
          </button>
        </form>
      </section>

      {/* Lines list */}
      <section>
        <h2 className="text-xl font-semibold mb-4">Lines</h2>
        {lines.length === 0 ? (
          <p className="text-gray-600">No lines yet.</p>
        ) : (
          <ul className="space-y-4">
            {lines.map((line) => (
              <li
                key={line.id}
                className="p-4 border rounded bg-white flex justify-between items-start"
              >
                <div className="flex-1">
                  <p className="text-sm text-gray-500">
                    {line.start_time.toFixed(2)}s {line.speaker && `[${line.speaker}]`}
                  </p>
                  <p className="mt-1">{line.text}</p>
                </div>
                <button
                  onClick={() => handleDelete(line.id)}
                  className="ml-4 text-red-600 hover:underline"
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
