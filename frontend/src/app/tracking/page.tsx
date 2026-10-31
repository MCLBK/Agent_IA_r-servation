"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { api } from "@/lib/api";

const STATUS_MAP: Record<string, { label: string; color: string; bg: string }> = {
  pending: { label: "En attente", color: "text-amber-700", bg: "bg-amber-50 border-amber-200" },
  confirmed: { label: "Confirmee", color: "text-green-700", bg: "bg-green-50 border-green-200" },
  cancelled: { label: "Annulee", color: "text-red-700", bg: "bg-red-50 border-red-200" },
  modified: { label: "Modifiee", color: "text-blue-700", bg: "bg-blue-50 border-blue-200" },
};

const PAYMENT_MAP: Record<string, { label: string; color: string }> = {
  pending: { label: "En attente", color: "text-amber-600" },
  paid: { label: "Paye", color: "text-green-600" },
  refunded: { label: "Rembourse", color: "text-gray-600" },
};

function formatDate(d: string | null) {
  if (!d) return "-";
  const parts = d.split("-");
  if (parts.length === 3) return `${parts[2]}/${parts[1]}/${parts[0]}`;
  return d;
}

export default function TrackingPage() {
  const searchParams = useSearchParams();
  const [reference, setReference] = useState("");
  const [email, setEmail] = useState("");
  const [booking, setBooking] = useState<any>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [autoSearched, setAutoSearched] = useState(false);

  useEffect(() => {
    const ref = searchParams.get("ref");
    if (ref && !autoSearched) {
      setReference(ref.toUpperCase());
      setAutoSearched(true);
      setLoading(true);
      api.trackBooking(ref.trim(), undefined)
        .then(setBooking)
        .catch((err: any) => setError(err.message || "Reservation introuvable"))
        .finally(() => setLoading(false));
    }
  }, [searchParams, autoSearched]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reference.trim()) return;

    setLoading(true);
    setError("");
    setBooking(null);

    try {
      const result = await api.trackBooking(reference.trim(), email.trim() || undefined);
      setBooking(result);
    } catch (err: any) {
      setError(err.message || "Reservation introuvable");
    } finally {
      setLoading(false);
    }
  };

  const status = booking ? STATUS_MAP[booking.status] || STATUS_MAP.pending : null;
  const payment = booking ? PAYMENT_MAP[booking.payment_status] || PAYMENT_MAP.pending : null;

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Header */}
      <header className="bg-white border-b border-gray-100 px-4 py-3">
        <div className="max-w-2xl mx-auto flex items-center gap-3">
          <a href="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
            <div className="w-9 h-9 bg-navy-900 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-gold-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </div>
            <div>
              <h1 className="font-display font-bold text-navy-900 text-sm leading-tight">GrowUp AI</h1>
              <p className="text-xs text-gray-400">Suivi de reservation</p>
            </div>
          </a>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-8">
        {/* Search form */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-6">
          <h2 className="font-display text-xl font-bold text-navy-900 mb-1">
            Suivre ma reservation
          </h2>
          <p className="text-sm text-gray-500 mb-6">
            Entrez votre reference de reservation pour consulter le statut de votre dossier.
          </p>

          <form onSubmit={handleSearch} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Reference de reservation *
              </label>
              <input
                type="text"
                value={reference}
                onChange={(e) => setReference(e.target.value.toUpperCase())}
                placeholder="Ex: GUA-F7YBHB3"
                className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm
                         focus:outline-none focus:ring-2 focus:ring-navy-100 focus:border-navy-300
                         placeholder-gray-400 font-mono text-lg tracking-wider"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email <span className="text-gray-400 font-normal">(optionnel, pour verification)</span>
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="votre@email.com"
                className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm
                         focus:outline-none focus:ring-2 focus:ring-navy-100 focus:border-navy-300
                         placeholder-gray-400"
              />
            </div>

            <button
              type="submit"
              disabled={loading || !reference.trim()}
              className="w-full bg-navy-900 hover:bg-navy-800 disabled:bg-gray-300
                       text-white font-semibold py-3 px-6 rounded-xl transition-colors text-sm"
            >
              {loading ? "Recherche en cours..." : "Rechercher"}
            </button>
          </form>

          {error && (
            <div className="mt-4 bg-red-50 border border-red-200 rounded-xl p-4">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}
        </div>

        {/* Booking result */}
        {booking && status && payment && (
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden animate-fade-in-up">
            {/* Reference header */}
            <div className="bg-navy-900 px-6 py-5 text-center">
              <p className="text-xs text-gray-400 mb-1">Reference</p>
              <p className="text-2xl font-bold text-gold-400 font-mono tracking-widest">
                {booking.reference}
              </p>
            </div>

            {/* Status */}
            <div className="px-6 py-4 flex items-center justify-center gap-4 border-b border-gray-100">
              <span className={`px-4 py-1.5 rounded-full text-sm font-semibold border ${status.bg} ${status.color}`}>
                {status.label}
              </span>
              <span className={`text-sm font-medium ${payment.color}`}>
                Paiement : {payment.label}
              </span>
            </div>

            {/* Details */}
            <div className="px-6 py-5 space-y-4">
              {/* Destination */}
              {booking.destination_name && (
                <div className="flex items-center gap-3 pb-4 border-b border-gray-100">
                  <div className="w-10 h-10 bg-navy-50 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-navy-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-semibold text-navy-900">{booking.destination_name}</p>
                    <p className="text-xs text-gray-500">{booking.destination_country}</p>
                  </div>
                </div>
              )}

              {/* Dates & travelers */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-gray-500 mb-1">Dates</p>
                  <p className="text-sm font-medium text-gray-800">
                    {formatDate(booking.departure_date)} — {formatDate(booking.return_date)}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 mb-1">Voyageurs</p>
                  <p className="text-sm font-medium text-gray-800">
                    {booking.num_adults} adulte(s)
                    {booking.num_children > 0 && `, ${booking.num_children} enfant(s)`}
                  </p>
                </div>
              </div>

              {/* Flight */}
              {booking.flight_summary && (
                <div className="bg-gray-50 rounded-xl p-4">
                  <p className="text-xs text-gray-500 mb-1 font-medium uppercase tracking-wide">Vol</p>
                  <p className="text-sm text-gray-800">{booking.flight_summary}</p>
                </div>
              )}

              {/* Hotel */}
              {booking.hotel_summary && (
                <div className="bg-gray-50 rounded-xl p-4">
                  <p className="text-xs text-gray-500 mb-1 font-medium uppercase tracking-wide">Hotel</p>
                  <p className="text-sm text-gray-800">{booking.hotel_summary}</p>
                </div>
              )}

              {/* Total */}
              <div className="bg-navy-50 rounded-xl p-4 flex items-center justify-between">
                <p className="text-sm font-medium text-navy-700">Montant total</p>
                <p className="text-xl font-bold text-navy-900">
                  {booking.total_price?.toFixed(2)} {booking.currency}
                </p>
              </div>

              {/* Timestamps */}
              <div className="text-xs text-gray-400 pt-2 border-t border-gray-100 space-y-1">
                <p>Reservee le : {new Date(booking.created_at).toLocaleDateString("fr-FR", {
                  day: "numeric", month: "long", year: "numeric", hour: "2-digit", minute: "2-digit"
                })}</p>
                {booking.confirmed_at && (
                  <p>Confirmee le : {new Date(booking.confirmed_at).toLocaleDateString("fr-FR", {
                    day: "numeric", month: "long", year: "numeric", hour: "2-digit", minute: "2-digit"
                  })}</p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Back link */}
        <div className="text-center mt-8">
          <a
            href="/"
            className="text-sm text-navy-600 hover:text-navy-800 transition-colors"
          >
            &larr; Retour a l&apos;assistant voyage
          </a>
        </div>
      </main>
    </div>
  );
}
