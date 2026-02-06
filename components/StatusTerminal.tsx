"use client";

import { useEffect, useRef } from "react";

interface StatusTerminalProps {
    logs: string[];
}

export default function StatusTerminal({ logs }: StatusTerminalProps) {
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs]);

    return (
        <div className="w-full h-64 bg-black/80 rounded-xl border border-white/10 p-4 font-mono text-xs overflow-hidden flex flex-col shadow-2xl backdrop-blur-md">
            <div className="flex items-center gap-2 mb-2 border-b border-white/10 pb-2">
                <div className="w-2 h-2 rounded-full bg-red-500" />
                <div className="w-2 h-2 rounded-full bg-yellow-500" />
                <div className="w-2 h-2 rounded-full bg-green-500" />
                <span className="ml-auto text-gray-500 text-[10px] tracking-widest">SYSTEM_LOGS</span>
            </div>
            <div ref={scrollRef} className="flex-1 overflow-y-auto space-y-1 scrollbar-thin scrollbar-thumb-white/10">
                {logs.length === 0 && (
                    <span className="text-gray-600 italic">Waiting for crawling process...</span>
                )}
                {logs.map((log, i) => (
                    <div key={i} className="text-green-400 border-l-2 border-green-500/30 pl-2">
                        <span className="text-gray-600 mr-2 opacity-50">›</span>
                        {log}
                    </div>
                ))}
            </div>
        </div>
    );
}
