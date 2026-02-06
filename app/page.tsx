"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import StatusTerminal from "@/components/StatusTerminal";

export default function Home() {
  const [url, setUrl] = useState("");
  const [depth, setDepth] = useState(3);
  const [maxPages, setMaxPages] = useState(100);
  const [isProcessing, setIsProcessing] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const socketRef = useRef<WebSocket | null>(null);
  const router = useRouter();

  const startExcavation = async () => {
    if (!url) return;
    setIsProcessing(true);
    setLogs([]);

    // 1. Connect WebSocket
    const ws = new WebSocket("ws://localhost:8000/ws");
    socketRef.current = ws;

    ws.onopen = () => {
      setLogs(prev => [...prev, "Connected to Digital Archaeology System..."]);
    };

    ws.onmessage = (event) => {
      setLogs(prev => [...prev, event.data]);
      if (event.data.includes("Indexing complete")) {
        setIsProcessing(false);
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket Error:", error);
      setLogs(prev => [...prev, "Error: Connection to backend failed."]);
      setIsProcessing(false);
    };

    // 2. Trigger Crawl
    try {
      const res = await fetch("http://localhost:8000/crawl", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, max_depth: depth, max_pages: maxPages })
      });
      if (!res.ok) throw new Error("Failed to start crawl");
    } catch (e) {
      setLogs(prev => [...prev, "Error: Could not start crawl API."]);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 md:p-24 relative overflow-hidden">
      {/* Background Gradients */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10">
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-purple-900/20 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-cyan-900/20 rounded-full blur-[120px]" />
      </div>

      <div className="z-10 w-full max-w-5xl items-center justify-center font-mono text-sm lg:flex-col lg:flex">

        {/* Hero Section */}
        <div className="text-center mb-16 space-y-6">
          <div className="inline-block px-4 py-1.5 rounded-full border border-cyan-500/30 bg-cyan-500/10 text-cyan-400 mb-4 animate-pulse">
            System Online • Ready for Analysis
          </div>
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-gray-200 to-gray-500 pb-2">
            Digital Archaeology
          </h1>
          <p className="text-gray-400 text-lg md:text-xl max-w-2xl mx-auto">
            Exhaustive University Website Intelligence System.
            <br />
            Extract, Analyze, and Query every document and detail.
          </p>
        </div>

        {/* Input Console */}
        <div className="w-full max-w-2xl mx-auto space-y-6">
          <div className="glass-panel rounded-2xl p-2 md:p-3 flex flex-col gap-2 transition-all duration-300 hover:border-cyan-500/50">
            <div className="flex flex-col md:flex-row gap-2">
              <div className="flex-1 relative group">
                <input
                  type="text"
                  className="w-full bg-black/40 text-white rounded-xl py-4 px-4 outline-none border border-transparent focus:border-cyan-500/50 transition-all font-mono"
                  placeholder="https://university.edu"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && startExcavation()}
                />
              </div>
              <div className="flex gap-2">
                <input
                  type="number"
                  min="1" max="5"
                  value={depth}
                  onChange={(e) => setDepth(parseInt(e.target.value))}
                  className="w-20 bg-black/40 text-white rounded-xl py-4 px-2 text-center outline-none border border-transparent focus:border-cyan-500/50 font-mono"
                  title="Crawl Depth"
                />
                <input
                  type="number"
                  min="10" max="500"
                  value={maxPages}
                  onChange={(e) => setMaxPages(parseInt(e.target.value))}
                  className="w-24 bg-black/40 text-white rounded-xl py-4 px-2 text-center outline-none border border-transparent focus:border-cyan-500/50 font-mono"
                  title="Max Pages"
                />
              </div>
            </div>

            <button
              onClick={startExcavation}
              disabled={isProcessing}
              className={`
                w-full py-4 rounded-xl font-bold tracking-wide transition-all duration-300
                ${isProcessing
                  ? "bg-gray-800 text-gray-400 cursor-not-allowed"
                  : "bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/40 transform hover:-translate-y-0.5"
                }
              `}
            >
              {isProcessing ? "SCANNING..." : "START EXCAVATION"}
            </button>
          </div>

          {/* Terminal Output */}
          <div className={`transition-all duration-500 ease-in-out ${isProcessing || logs.length > 0 ? 'opacity-100 max-h-96' : 'opacity-0 max-h-0'}`}>
            <StatusTerminal logs={logs} />
          </div>

          {!isProcessing && logs.length > 0 && (
            <div className="flex justify-center animate-fade-in-up my-8">
              <button
                onClick={() => router.push('/chat')}
                className="px-8 py-3 bg-white text-black font-bold rounded-full hover:scale-105 transition-transform shadow-[0_0_20px_rgba(255,255,255,0.3)]"
              >
                ENTER KNOWLEDGE BASE →
              </button>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center text-xs text-gray-500 font-mono">
            <div className="border border-white/5 rounded-lg p-3 bg-white/5">
              <span className="block text-cyan-400 mb-1">DEEP CRAWL</span>
              Recursive Traversal
            </div>
            <div className="border border-white/5 rounded-lg p-3 bg-white/5">
              <span className="block text-cyan-400 mb-1">OCR VISION</span>
              Scanned Doc Analysis
            </div>
            <div className="border border-white/5 rounded-lg p-3 bg-white/5">
              <span className="block text-cyan-400 mb-1">RAG ENGINE</span>
              Vector Embeddings
            </div>
          </div>
        </div>

      </div>
    </main>
  );
}
