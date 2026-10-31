"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function BookingsPage() {
  const [bookings, setBookings] = useState<any[]>([]);
  const [filter, setFilter] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<any>(null);

  useEffect(() => {
    loadBookings();
  }, [filter]);

  const loadBookings = async () => {
    setLoading(true);
    try {
      const data = await api.getBookings(filter || undefined);
      setBookings(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async (id: number) => {
    try {
      await api.confirmBooking(id);
      loadBookings();
      setSelected(null);
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleCancel = async (id: number) => {
    const reason = prompt("Raison de l'annulation :");
    if (reason === null) return;
    try {
      await api.cancelBooking(id, reason);
      loadBookings();
      setSelected(null);
    } catch (err: any) {
      alert(err.message);
    }
  };

  const statusLabels: Record<string, { label: string; classes: string }> = {
    pending: { label: "En attente", classes: "bg-yellow-50 text-yellow-700" },
    confirmed: { label: "Confirmee", classes: "bg-green-50 text-green-700" },
    cancelled: { label: "Annulee", classes: "bg-red-50 text-red-600" },
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-display text-xl font-bold text-navy-900">Reservations</h1>
          <p className="text-sm text-gray-500 mt-0.5">{bookings.length} reservation(s)</p>
        </div>
        <div className="flex gap-1 bg-gray-100 rounded-lg p-1">
          {[
            { key: "", label: "Toutes" },
            { key: "pending", label: "En attente" },
            { key: "confirmed", label: "Confirmees" },
            { key: "cancelled", label: "Annulees" },
          ].map((f) => (
            <button
              key={f.key}
              onClick={() => setFilter(f.key)}
              className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                filter === f.key ? "bg-white text-navy-900 shadow-sm" : "text-gray-500"
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-40">
          <div className="w-6 h-6 border-2 border-navy-900 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : bookings.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-100 p-8 text-center">
          <p className="text-gray-400">Aucune reservation</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Reference</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Destination</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Voyageurs</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Dates</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Prix</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Statut</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Actions</th>
                </tr>
              </thead>
              <tbody>
                {bookings.map((b) => {
                  const st = statusLabels[b.status] || { label: b.status, classes: "bg-gray-50 text-gray-500" };
                  return (
                    <tr key={b.id} className="border-t border-gray-50 hover:bg-gray-50">
                      <td className="px-4 py-3 font-mono text-xs font-medium text-navy-900">{b.reference}</td>
                      <td className="px-4 py-3 text-gray-700">{b.destination_name || "—"}</td>
                      <td className="px-4 py-3 text-gray-600">
                        {b.num_adults} ad.{b.num_children > 0 ? ` ${b.num_children} enf.` : ""}
                      </td>
                      <td className="px-4 py-3 text-xs text-gray-500">
                        {b.departure_date || "—"}{b.return_date ? ` → ${b.return_date}` : ""}
                      </td>
                      <td className="px-4 py-3 font-semibold text-navy-900">{b.total_price?.toFixed(0)} EUR</td>
                      <td className="px-4 py-3">
                        <span className={`text-xs px-2 py-0.5 rounded-full ${st.classes}`}>{st.label}</span>
                        {b.is_demo && <span className="text-xs text-gray-300 ml-1">demo</span>}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex gap-1">
                          {b.status === "pending" && (
                            <>
                              <button
                                onClick={() => handleConfirm(b.id)}
                                className="text-xs bg-green-50 text-green-700 hover:bg-green-100 px-2 py-1 rounded transition-colors"
                              >
                                Confirmer
                              </button>
                              <button
                                onClick={() => handleCancel(b.id)}
                                className="text-xs bg-red-50 text-red-600 hover:bg-red-100 px-2 py-1 rounded transition-colors"
                              >
                                Annuler
                              </button>
                            </>
                          )}
                          <button
                            onClick={() => setSelected(b)}
                            className="text-xs text-navy-600 hover:text-navy-900 px-2 py-1 rounded transition-colors"
                          >
                            Details
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Detail modal */}
      {selected && (
        <div className="fixed inset-0 z-50 bg-black/30 flex items-center justify-center p-4" onClick={() => setSelected(null)}>
          <div className="bg-white rounded-2xl shadow-xl max-w-lg w-full max-h-[80vh] overflow-y-auto p-6" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-display font-bold text-navy-900">Reservation {selected.reference}</h2>
              <button onClick={() => setSelected(null)} className="text-gray-400 hover:text-gray-600">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-3 text-sm">
              <div className="grid grid-cols-2 gap-3">
                <div><p className="text-xs text-gray-500">Statut</p><p className="font-medium">{statusLabels[selected.status]?.label}</p></div>
                <div><p className="text-xs text-gray-500">Prix total</p><p className="font-bold text-navy-900">{selected.total_price?.toFixed(2)} EUR</p></div>
                <div><p className="text-xs text-gray-500">Depart</p><p>{selected.departure_date || "—"}</p></div>
                <div><p className="text-xs text-gray-500">Retour</p><p>{selected.return_date || "—"}</p></div>
                <div><p className="text-xs text-gray-500">Contact</p><p>{selected.contact_email || "—"}</p></div>
                <div><p className="text-xs text-gray-500">Telephone</p><p>{selected.contact_phone || "—"}</p></div>
              </div>

              {selected.flight && (
                <div className="bg-gray-50 rounded-lg p-3 mt-3">
                  <p className="text-xs font-medium text-gray-500 mb-1">Vol</p>
                  <p className="font-medium">{selected.flight.airline} {selected.flight.flight_number}</p>
                  <p className="text-xs text-gray-500">{selected.flight.departure_city} → {selected.flight.arrival_city}</p>
                </div>
              )}

              {selected.hotel && (
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs font-medium text-gray-500 mb-1">Hotel</p>
                  <p className="font-medium">{selected.hotel.name}</p>
                  <p className="text-xs text-gray-500">{selected.hotel.city} · {"★".repeat(selected.hotel.category)}</p>
                </div>
              )}

              {selected.traveler_details?.length > 0 && (
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs font-medium text-gray-500 mb-1">Voyageurs</p>
                  {selected.traveler_details.map((t: any, i: number) => (
                    <p key={i} className="text-sm">{t.name || "—"} {t.date_of_birth ? `(${t.date_of_birth})` : ""}</p>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
