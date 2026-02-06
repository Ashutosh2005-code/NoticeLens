"use client";

import { useState, useRef, useEffect } from "react";

interface Message {
    role: "user" | "assistant";
    content: string;
    sources?: string[];
}

export default function ChatPage() {
    const [messages, setMessages] = useState<Message[]>([
        { role: "assistant", content: "I have analyzed the university website. Ask me anything about admissions, curriculum, or faculty." }
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMsg = input;
        setMessages(prev => [...prev, { role: "user", content: userMsg }]);
        setInput("");
        setLoading(true);

        try {
            const res = await fetch("http://localhost:8000/query", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question: userMsg })
            });

            const data = await res.json();
            setMessages(prev => [...prev, { role: "assistant", content: data.answer, sources: data.sources }]);
        } catch (e) {
            setMessages(prev => [...prev, { role: "assistant", content: "Error: Could not retrieve answer." }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="flex h-screen bg-[#050505] text-white font-mono overflow-hidden">
            {/* Sidebar (Visual only for now) */}
            <div className="hidden md:flex w-64 border-r border-white/10 flex-col p-4 bg-black/50 backdrop-blur-xl">
                <div className="text-cyan-400 font-bold mb-8 tracking-widest text-xs">ARCHIVED DOCUMENTS</div>
                <div className="space-y-2 opacity-50 text-xs">
                    <div className="p-2 bg-white/5 rounded border border-white/5">Curriculum.pdf</div>
                    <div className="p-2 bg-white/5 rounded border border-white/5">Admissions_2024.pdf</div>
                    <div className="p-2 bg-white/5 rounded border border-white/5">Faculty_List.html</div>
                </div>
            </div>

            {/* Chat Area */}
            <div className="flex-1 flex flex-col relative">
                <div className="p-4 border-b border-white/10 flex justify-between items-center bg-black/50 backdrop-blur-md z-10">
                    <h1 className="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-500">
                        The Archaeologist
                    </h1>
                    <a href="/" className="text-xs text-gray-500 hover:text-white transition-colors">NEW EXCAVATION</a>
                </div>

                <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6" ref={scrollRef}>
                    {messages.map((m, i) => (
                        <div key={i} className={`flex flex-col ${m.role === 'user' ? 'items-end' : 'items-start'} space-y-2`}>
                            <div className={`
                            max-w-[80%] p-4 rounded-2xl text-sm leading-relaxed
                            ${m.role === 'user'
                                    ? 'bg-gradient-to-br from-cyan-600/20 to-blue-600/20 border border-cyan-500/30 text-cyan-50'
                                    : 'bg-white/5 border border-white/10 text-gray-300'
                                }
                         `}>
                                <div className="whitespace-pre-wrap">{m.content}</div>
                                {m.sources && m.sources.length > 0 && (
                                    <div className="mt-4 pt-4 border-t border-white/10">
                                        <div className="text-xs font-bold text-cyan-400 mb-2">SOURCES ACQUIRED:</div>
                                        <div className="grid gap-2">
                                            {m.sources.map((src, idx) => (
                                                <a key={idx} href={src} target="_blank" rel="noopener noreferrer"
                                                    className="text-xs bg-black/20 p-2 rounded hover:bg-cyan-500/10 hover:text-cyan-300 transition-colors truncate block border border-white/5">
                                                    📄 {src.split('/').pop()}
                                                    <div className="text-[10px] text-gray-500 opacity-50 truncate">{src}</div>
                                                </a>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                    {loading && (
                        <div className="flex justify-start">
                            <div className="bg-white/5 border border-white/10 p-4 rounded-2xl flex gap-2 items-center">
                                <div className="w-2 h-2 bg-cyan-500 rounded-full animate-bounce" />
                                <div className="w-2 h-2 bg-cyan-500 rounded-full animate-bounce delay-75" />
                                <div className="w-2 h-2 bg-cyan-500 rounded-full animate-bounce delay-150" />
                            </div>
                        </div>
                    )}
                </div>

                <div className="p-4 md:p-8 pt-0">
                    <div className="relative">
                        <input
                            type="text"
                            className="w-full bg-white/5 border border-white/10 rounded-xl p-4 pr-12 outline-none focus:border-cyan-500/50 transition-all text-sm"
                            placeholder="Ask a question about the university..."
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                        />
                        <button
                            onClick={sendMessage}
                            className="absolute right-2 top-2 p-2 bg-cyan-500/10 hover:bg-cyan-500/20 rounded-lg text-cyan-400 transition-colors"
                        >
                            →
                        </button>
                    </div>
                </div>
            </div>
        </main>
    );
}
