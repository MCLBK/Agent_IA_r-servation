"use client";

import { useState, useRef, useEffect } from "react";
import { api } from "@/lib/api";

interface Message {
  role: "user" | "assistant" | "system";
  content: string;
  offers?: any[];
  booking?: any;
}

const SUGGESTIONS = [
  "Je cherche une destination pour deux personnes en decembre, budget 1000 euros",
  "Quelles destinations proposez-vous pour un sejour plage ?",
  "Je voudrais partir a Marrakech la semaine prochaine",
  "Montrez-moi les vols pour Lisbonne",
];

function formatContent(text: string) {
  const lines = text.split("\n");
  return lines.map((line, i) => {
    if (line.startsWith("**") && line.endsWith("**")) {
      return (
        <p key={i} className="font-semibold text-navy-900 mt-2 mb-1">
          {line.replace(/\*\*/g, "")}
        </p>
      );
    }
    if (line.includes("**")) {
      const parts = line.split(/(\*\*[^*]+\*\*)/g);
      return (
        <p key={i} className="mb-1">
          {parts.map((part, j) =>
            part.startsWith("**") && part.endsWith("**") ? (
              <strong key={j} className="font-semibold text-navy-900">
                {part.replace(/\*\*/g, "")}
              </strong>
            ) : (
              <span key={j}>{part}</span>
            )
          )}
        </p>
      );
    }
    if (line.startsWith("_") && line.endsWith("_")) {
      return (
        <p key={i} className="text-xs text-gray-400 italic mt-1">
          {line.replace(/_/g, "")}
        </p>
      );
    }
    if (line.startsWith("  ")) {
      return (
        <p key={i} className="ml-4 text-sm text-gray-600 mb-0.5">
          {line.trim()}
        </p>
      );
    }
    if (line.trim() === "") return <br key={i} />;
    return <p key={i} className="mb-1">{line}</p>;
  });
}

function OfferCard({ offer }: { offer: any }) {
  if (offer.type === "destination") {
    return (
      <div className="bg-white rounded-xl border border-gray-100 overflow-hidden shadow-sm hover:shadow-md transition-shadow">
        {offer.image_url && (
          <div className="h-36 bg-gray-100 overflow-hidden">
            <img
              src={offer.image_url}
              alt={offer.name}
              className="w-full h-full object-cover"
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = "none";
              }}
            />
          </div>
        )}
        <div className="p-4">
          <h3 className="font-display font-bold text-navy-900">{offer.name}</h3>
          <p className="text-sm text-gray-500 mb-2">{offer.country}</p>
          <p className="text-sm text-gray-600 line-clamp-2">{offer.description}</p>
          {offer.highlights?.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {offer.highlights.slice(0, 3).map((h: string, i: number) => (
                <span
                  key={i}
                  className="text-xs bg-gold-50 text-gold-700 px-2 py-0.5 rounded-full"
                >
                  {h}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  if (offer.type === "flight") {
    return (
      <div className="bg-white rounded-xl border border-gray-100 p-4 shadow-sm">
        <div className="flex items-center justify-between mb-3">
          <span className="font-semibold text-navy-900">{offer.airline}</span>
          <span className="text-xs text-gray-400">{offer.flight_number}</span>
        </div>
        <div className="flex items-center gap-3 mb-3">
          <div className="text-center">
            <p className="font-bold text-lg">{offer.departure_time}</p>
            <p className="text-xs text-gray-500">{offer.departure?.split("(")[1]?.replace(")", "")}</p>
          </div>
          <div className="flex-1 flex flex-col items-center">
            <p className="text-xs text-gray-400">
              {Math.floor(offer.duration_minutes / 60)}h{String(offer.duration_minutes % 60).padStart(2, "0")}
            </p>
            <div className="w-full h-px bg-gray-200 relative my-1">
              <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1.5 h-1.5 bg-navy-900 rounded-full" />
              <div className="absolute right-0 top-1/2 -translate-y-1/2 w-1.5 h-1.5 bg-navy-900 rounded-full" />
            </div>
            <p className="text-xs text-gray-400">
              {offer.stops === 0 ? "Direct" : `${offer.stops} escale(s)`}
            </p>
          </div>
          <div className="text-center">
            <p className="font-bold text-lg">{offer.arrival_time}</p>
            <p className="text-xs text-gray-500">{offer.arrival?.split("(")[1]?.replace(")", "")}</p>
          </div>
        </div>
        <div className="flex items-end justify-between">
          <div className="text-xs text-gray-500">
            {offer.baggage?.cabin && <span>Cabine: {offer.baggage.cabin}</span>}
            {offer.baggage?.checked && <span className="ml-2">Soute: {offer.baggage.checked}</span>}
          </div>
          <p className="font-bold text-lg text-navy-900">
            {offer.total_price?.toFixed(0)} <span className="text-sm">{offer.currency}</span>
          </p>
        </div>
      </div>
    );
  }

  if (offer.type === "hotel") {
    return (
      <div className="bg-white rounded-xl border border-gray-100 overflow-hidden shadow-sm">
        {offer.image_url && (
          <div className="h-32 bg-gray-100 overflow-hidden">
            <img
              src={offer.image_url}
              alt={offer.name}
              className="w-full h-full object-cover"
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = "none";
              }}
            />
          </div>
        )}
        <div className="p-4">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-semibold text-navy-900">{offer.name}</h3>
            <span className="text-gold-400 text-sm">{"★".repeat(offer.category)}</span>
          </div>
          <p className="text-xs text-gray-500 mb-2">{offer.city} · {offer.meal_plan}</p>
          {offer.amenities?.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-2">
              {offer.amenities.slice(0, 4).map((a: string, i: number) => (
                <span key={i} className="text-xs bg-gray-50 text-gray-600 px-2 py-0.5 rounded">
                  {a}
                </span>
              ))}
            </div>
          )}
          <div className="flex items-end justify-between">
            <p className="text-xs text-gray-500">{offer.nights} nuits</p>
            <p className="font-bold text-navy-900">
              {offer.total_price?.toFixed(0)} <span className="text-sm">{offer.currency}</span>
            </p>
          </div>
        </div>
      </div>
    );
  }

  return null;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const sendMessage = async (text: string) => {
    if (!text.trim() || loading) return;
    const userMsg: Message = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await api.chat(text, sessionId);
      setSessionId(res.session_id);
      const assistantMsg: Message = {
        role: "assistant",
        content: res.message,
        offers: res.offers,
        booking: res.booking,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Desole, une erreur s'est produite. Veuillez reessayer ou contacter un conseiller.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-b from-gray-50 to-white">
      {/* Header */}
      <header className="bg-white border-b border-gray-100 px-4 py-3 sticky top-0 z-10">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-navy-900 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-gold-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </div>
            <div>
              <h1 className="font-display font-bold text-navy-900 text-sm leading-tight">
                GrowUp AI
              </h1>
              <p className="text-xs text-gray-400">Assistant Voyage</p>
            </div>
          </div>
          <a
            href="/login"
            className="text-xs text-gray-400 hover:text-navy-900 transition-colors"
          >
            Espace agence
          </a>
        </div>
      </header>

      {/* Chat area */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-4 py-6">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center min-h-[60vh]">
              <div className="w-16 h-16 bg-navy-900 rounded-2xl flex items-center justify-center mb-6 shadow-lg">
                <svg className="w-8 h-8 text-gold-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </div>
              <h2 className="font-display text-2xl font-bold text-navy-900 mb-2 text-center">
                Ou souhaitez-vous voyager ?
              </h2>
              <p className="text-gray-500 text-center mb-8 max-w-md">
                Decrivez votre projet et je vous guiderai vers les meilleures offres
                de notre catalogue.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-lg">
                {SUGGESTIONS.map((s, i) => (
                  <button
                    key={i}
                    onClick={() => sendMessage(s)}
                    className="text-left text-sm px-4 py-3 bg-white border border-gray-200 rounded-xl hover:border-navy-300 hover:bg-navy-50 transition-all text-gray-600"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              className={`mb-4 animate-fade-in-up ${
                msg.role === "user" ? "flex justify-end" : "flex justify-start"
              }`}
            >
              {msg.role === "assistant" && (
                <div className="w-7 h-7 bg-navy-900 rounded-lg flex items-center justify-center mr-2 mt-1 flex-shrink-0">
                  <svg className="w-3.5 h-3.5 text-gold-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                </div>
              )}
              <div
                className={`max-w-[85%] ${
                  msg.role === "user"
                    ? "bg-navy-900 text-white rounded-2xl rounded-tr-md px-4 py-3"
                    : "bg-white border border-gray-100 rounded-2xl rounded-tl-md px-4 py-3 shadow-sm"
                }`}
              >
                <div className={`text-sm leading-relaxed chat-content ${
                  msg.role === "user" ? "text-white" : "text-gray-700"
                }`}>
                  {formatContent(msg.content)}
                </div>

                {msg.offers && msg.offers.length > 0 && (
                  <div className="mt-3 grid grid-cols-1 gap-3">
                    {msg.offers.map((offer, j) => (
                      <OfferCard key={j} offer={offer} />
                    ))}
                  </div>
                )}

                {msg.booking && (
                  <div className="mt-3 bg-green-50 border border-green-200 rounded-lg p-3">
                    <p className="text-sm font-semibold text-green-800">
                      Reservation enregistree
                    </p>
                    <p className="text-sm text-green-700">
                      Ref: {msg.booking.reference} · {msg.booking.total_price?.toFixed(2)} EUR
                    </p>
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex items-start mb-4 animate-fade-in-up">
              <div className="w-7 h-7 bg-navy-900 rounded-lg flex items-center justify-center mr-2 mt-1">
                <svg className="w-3.5 h-3.5 text-gold-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </div>
              <div className="bg-white border border-gray-100 rounded-2xl rounded-tl-md px-4 py-3 shadow-sm">
                <div className="flex gap-1.5 py-1">
                  <span className="typing-dot" />
                  <span className="typing-dot" />
                  <span className="typing-dot" />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Input */}
      <footer className="sticky bottom-0 bg-white border-t border-gray-100 px-4 py-3">
        <div className="max-w-3xl mx-auto">
          <div className="flex items-end gap-2 bg-gray-50 rounded-2xl border border-gray-200 focus-within:border-navy-300 focus-within:ring-2 focus-within:ring-navy-100 transition-all px-4 py-2">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Decrivez votre projet de voyage..."
              rows={1}
              className="flex-1 bg-transparent resize-none outline-none text-sm text-gray-800 placeholder-gray-400 max-h-32"
              style={{ minHeight: "24px" }}
              onInput={(e) => {
                const target = e.target as HTMLTextAreaElement;
                target.style.height = "24px";
                target.style.height = Math.min(target.scrollHeight, 128) + "px";
              }}
            />
            <button
              onClick={() => sendMessage(input)}
              disabled={!input.trim() || loading}
              className="w-8 h-8 bg-navy-900 hover:bg-navy-800 disabled:bg-gray-300 rounded-lg flex items-center justify-center transition-colors flex-shrink-0"
            >
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 12h14m-7-7l7 7-7 7" />
              </svg>
            </button>
          </div>
          <p className="text-center text-xs text-gray-300 mt-2">
            Assistant IA · Les offres proviennent du catalogue de l&apos;agence · Donnees de demonstration
          </p>
        </div>
      </footer>
    </div>
  );
}
