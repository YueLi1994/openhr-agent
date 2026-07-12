import { useEffect, useState } from 'react'

type Connection = 'checking' | 'connected' | 'unavailable'

export function App() {
  const [connection, setConnection] = useState<Connection>('checking')

  useEffect(() => {
    const controller = new AbortController()
    fetch(`${import.meta.env.VITE_API_BASE_URL ?? '/api'}/health`, { signal: controller.signal })
      .then((response) => { if (!response.ok) throw new Error('Health check failed'); return response.json() })
      .then(() => setConnection('connected'))
      .catch((error: unknown) => { if (!(error instanceof DOMException && error.name === 'AbortError')) setConnection('unavailable') })
    return () => controller.abort()
  }, [])

  return <main className="shell">
    <section className="hero">
      <p className="eyebrow">OPEN-SOURCE REFERENCE FRAMEWORK</p>
      <h1>Build safer HR agents,<br /><span>one clear layer at a time.</span></h1>
      <p className="intro">OpenHR Agent is a modular, evaluable foundation for responsible HR AI experiments—running locally with a mock model and synthetic data.</p>
      <div className={`status ${connection}`} role="status"><i /> API {connection}</div>
      <div className="cards">
        <article><strong>Private by design</strong><p>Fictional policies and synthetic people only.</p></article>
        <article><strong>Offline by default</strong><p>No API key. No model calls. Deterministic tests.</p></article>
        <article><strong>Built to evaluate</strong><p>Clear boundaries ready for future safety checks.</p></article>
      </div>
    </section>
    <footer>Acme Corporation examples are entirely fictional · Apache-2.0</footer>
  </main>
}
