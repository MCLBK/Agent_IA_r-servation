"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function ConversationsPage() {
  const [conversations, setConversations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<any>(null);
  const [detail, setDetail] = useState<any>(null);
  const [showHumanOnly, setShowHumanOnly] = useState(false);

  useEffect(() => {
    loadConversations();
  }, [showHumanOnly]);

  const loadConversations = async () => {
    setLoading(true);
    try {
      const data = await api.getConversations(undefined, showHumanOnly ? true : undefined);
      setConversations(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const viewConversation = async (id: number) => {
    try {
      const data = await api.getConversation(id);
      setDetail(data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-display text-xl font-bold text-navy-900">Conversations</h1>
          <p className="text-sm text-gray-500 mt-0.5">{conversations.length} conversation(s)</p>
        </div>
        <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
          <input
            type="checkbox"
            checked={showHumanOnly}
            onChange={(e) => setShowHumanOnly(e.target.checked)}
            className="rounded border-gray-300"
          />
          Interventions requises
        </label>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* List */}
        <div className="lg:col-span-1 space-y-2">
          {loading ? (
            <div className="flex items-center justify-center h-40">
              <div className="w-6 h-6 border-2 border-navy-900 border-t-transparent rounded-full animate-spin" />
            </div>
          ) : conversations.length === 0 ? (
            <div className="bg-white rounded-xl border border-gray-100 p-6 text-center">
              <p className="text-sm text-gray-400">Aucune conversation</p>
            </div>
          ) : (
            conversations.map((c) => (
              <button
                key={c.id}
                onClick={() => viewConversation(c.id)}
                className={`w-full text-left bg-white rounded-xl border p-4 transition-colors ${
                  detail?.id === c.id ? "border-navy-300 ring-2 ring-navy-100" : "border-gray-100 hover:border-gray-200"
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-mono text-gray-400">{c.session_id.slice(0, 12)}...</span>
                  <div className="flex gap-1">
                    {c.needs_human && (
                      <span className="text-xs bg-red-50 text-red-600 px-1.5 py-0.5 rounded">!</span>
                    )}
                    <span className={`text-xs px-1.5 py-0.5 rounded ${
                      c.status === "active" ? "bg-blue-50 text-blue-600" :
                      c.status === "escalated" ? "bg-red-50 text-red-600" :
                      "bg-gray-50 text-gray-500"
                    }`}>
                      {c.status}
                    </span>
                  </div>
                </div>
                <p className="text-xs text-gray-500">
                  {c.message_count} messages · Etape: {c.current_step}
                </p>
                {c.traveler_name && (
                  <p className="text-xs text-gray-400 mt-0.5">{c.traveler_name}</p>
                )}
              </button>
            ))
          )}
        </div>

        {/* Detail */}
        <div className="lg:col-span-2">
          {detail ? (
            <div className="bg-white rounded-xl border border-gray-100 h-[70vh] flex flex-col">
              <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-navy-900">
                    Conversation {detail.session_id.slice(0, 12)}...
                  </p>
                  <p className="text-xs text-gray-400">
                    Etape: {detail.current_step} · {detail.messages?.length} messages
                  </p>
                </div>
                {detail.escalation_reason && (
                  <span className="text-xs bg-red-50 text-red-600 px-2 py-1 rounded-lg max-w-xs truncate">
                    {detail.escalation_reason}
                  </span>
                )}
              </div>

              <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {detail.messages?.map((m: any) => (
                  <div
                    key={m.id}
                    className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-xl px-3 py-2 text-sm ${
                        m.role === "user"
                          ? "bg-navy-900 text-white rounded-tr-sm"
                          : m.role === "agent"
                          ? "bg-blue-50 text-blue-900 rounded-tl-sm"
                          : "bg-gray-50 text-gray-700 rounded-tl-sm"
                      }`}
                    >
                      {m.role === "agent" && (
                        <p className="text-xs font-medium text-blue-600 mb-1">Conseiller</p>
                      )}
                      <p className="whitespace-pre-wrap">{m.content}</p>
                      <p className={`text-xs mt-1 ${
                        m.role === "user" ? "text-navy-300" : "text-gray-400"
                      }`}>
                        {new Date(m.created_at).toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" })}
                      </p>
                    </div>
                  </div>
                ))}
              </div>

              {detail.travel_project && Object.keys(detail.travel_project).length > 0 && (
                <div className="border-t border-gray-100 px-4 py-3">
                  <p className="text-xs font-medium text-gray-500 mb-1">Projet de voyage</p>
                  <div className="flex flex-wrap gap-2">
                    {detail.travel_project.destination && (
                      <span className="text-xs bg-navy-50 text-navy-600 px-2 py-0.5 rounded-full">
                        {detail.travel_project.destination}
                      </span>
                    )}
                    {detail.travel_project.departure_date && (
                      <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">
                        {detail.travel_project.departure_date}
                      </span>
                    )}
                    {detail.travel_project.num_adults && (
                      <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">
                        {detail.travel_project.num_adults} adulte(s)
                      </span>
                    )}
                    {detail.travel_project.budget && (
                      <span className="text-xs bg-gold-50 text-gold-700 px-2 py-0.5 rounded-full">
                        Budget: {detail.travel_project.budget} EUR
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-white rounded-xl border border-gray-100 h-[70vh] flex items-center justify-center">
              <p className="text-sm text-gray-400">Selectionnez une conversation</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
