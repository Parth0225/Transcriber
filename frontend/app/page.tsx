import Link from "next/link";

const pages = [{"route": "transcripts_id", "label": "Transcripts Id"}, {"route": "search", "label": "Search"}];

export default function Home() {
  return (
    <div>
      <h1 className="mb-4 text-2xl font-semibold">Transcriber App</h1>
      <ul className="space-y-2">
        {pages.map((p) => (
          <li key={p.route}>
            <Link className="text-blue-700 underline" href={`/${p.route}`}>{p.label}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
