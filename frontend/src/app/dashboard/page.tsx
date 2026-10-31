"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

function StatCard({ label, value, sub, color = "navy" }: { label: string; value: string | number; sub?: string; color?: string }) {
  const colors: Record<string, string> = {
    navy: "bg-navy-50 text-navy-900",
    gold: "bg-gold-50 text-gold-800",
    green: "bg-green-50 text-green-800",
    red: "bg-red-50 text-red-800",
    orange: "bg-orange-50 text-orange-800",
  };
  return (
    <div className="bg-white rounded-xl border border-gray-100 p-5">
      <p className="text-xs font-medium text-gray-500 mb-1">{label}</p>
      <p className="text-2xl font-bold text-navy-900">{value}</p>
      {sub && (
        <span className={`inline-block mt-1.5 text-xs px-2 py-0.5 rounded-full ${colors[color]}`}>
          {sub}
        </span>
      )}
    </div>
  );
}

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getStats().then(setStats).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-navy-900 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!stats) return <p className="text-gray-500">Erreur de chargement</p>;

  return (
    <div>
      <div className="mb-6">
        <h1 className="font-display text-xl font-bold text-navy-900">Tableau de bord</h1>
        <p className="text-sm text-gray-500 mt-0.5">Vue d&apos;ensemble de votre activite</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
        <StatCard label="Conversations" value={stats.total_conversations} sub={`${stats.active_conversations} actives`} />
        <StatCard label="Reservations" value={stats.total_bookings} sub={`${stats.confirmed_bookings} confirmees`} color="green" />
        <StatCard label="En attente" value={stats.pending_bookings} sub="A traiter" color="orange" />
        <StatCard label="Escalades" value={stats.escalated_conversations} sub="Intervention requise" color="red" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-3 mb-6">
        <StatCard
          label="Chiffre d'affaires"
          value={`${stats.total_revenue.toFixed(0)} EUR`}
          sub="Reservations en cours"
          color="gold"
        />
        <StatCard label="Taux de conversion" value={`${stats.conversion_rate}%`} sub="Conversations → Reservations" color="green" />
        <StatCard
          label="Destinations populaires"
          value={stats.top_destinations?.[0]?.name || "—"}
          sub={stats.top_destinations?.[0] ? `${stats.top_destinations[0].count} reservation(s)` : "Aucune donnee"}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Recent bookings */}
        <div className="bg-white rounded-xl border border-gray-100 p-5">
          <h2 className="font-semibold text-navy-900 text-sm mb-3">Dernieres reservations</h2>
          {stats.recent_bookings?.length > 0 ? (
            <div className="space-y-2">
              {stats.recent_bookings.map((b: any) => (
                <div key={b.id} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                  <div>
                    <p className="text-sm font-medium text-gray-800">{b.reference}</p>
                    <p className="text-xs text-gray-400">{b.destination_name || "—"} · {b.num_adults} adulte(s)</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-navy-900">{b.total_price?.toFixed(0)} EUR</p>
                    <span className={`text-xs px-1.5 py-0.5 rounded ${
                      b.status === "confirmed" ? "bg-green-50 text-green-700" :
                      b.status === "pending" ? "bg-yellow-50 text-yellow-700" :
                      "bg-gray-50 text-gray-500"
                    }`}>
                      {b.status === "confirmed" ? "Confirmee" : b.status === "pending" ? "En attente" : b.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-400">Aucune reservation</p>
          )}
        </div>

        {/* Recent conversations */}
        <div className="bg-white rounded-xl border border-gray-100 p-5">
          <h2 className="font-semibold text-navy-900 text-sm mb-3">Dernieres conversations</h2>
          {stats.recent_conversations?.length > 0 ? (
            <div className="space-y-2">
              {stats.recent_conversations.map((c: any) => (
                <div key={c.id} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                  <div>
                    <p className="text-sm font-medium text-gray-800">{c.session_id.slice(0, 8)}...</p>
                    <p className="text-xs text-gray-400">{c.message_count} messages · {c.current_step}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    {c.needs_human && (
                      <span className="text-xs bg-red-50 text-red-600 px-1.5 py-0.5 rounded">Intervention</span>
                    )}
                    <span className={`text-xs px-1.5 py-0.5 rounded ${
                      c.status === "active" ? "bg-blue-50 text-blue-700" :
                      c.status === "escalated" ? "bg-red-50 text-red-600" :
                      "bg-gray-50 text-gray-500"
                    }`}>
                      {c.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-400">Aucune conversation</p>
          )}
        </div>
      </div>
    </div>
  );
}
