const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function Home() {
  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-8 px-6 py-24">
      <div className="max-w-lg text-center">
        <p className="mb-3 text-sm font-medium uppercase tracking-widest text-emerald-400">
          Upload 1 — Scaffold
        </p>
        <h1 className="text-4xl font-bold tracking-tight">
          Fantasy Sports Analytics
        </h1>
        <p className="mt-4 text-lg text-zinc-400">
          Multi-sport NFL and NBA analytics. Player search, stats, and
          watchlists coming in later uploads.
        </p>
      </div>
      <ul className="flex flex-col gap-2 text-sm text-zinc-500">
        <li>API: {API_URL}</li>
        <li>Health: {API_URL}/health</li>
      </ul>
    </main>
  );
}
