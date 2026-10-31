"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type Tab = "destinations" | "flights" | "hotels";

export default function CatalogPage() {
  const [tab, setTab] = useState<Tab>("destinations");
  const [destinations, setDestinations] = useState<any[]>([]);
  const [flights, setFlights] = useState<any[]>([]);
  const [hotels, setHotels] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [d, f, h] = await Promise.all([
        api.getDestinations(),
        api.getFlights(),
        api.getHotels(),
      ]);
      setDestinations(d);
      setFlights(f);
      setHotels(h);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const tabs: { key: Tab; label: string; count: number }[] = [
    { key: "destinations", label: "Destinations", count: destinations.length },
    { key: "flights", label: "Vols", count: flights.length },
    { key: "hotels", label: "Hotels", count: hotels.length },
  ];

  return (
    <div>
      <div className="mb-6">
        <h1 className="font-display text-xl font-bold text-navy-900">Catalogue</h1>
        <p className="text-sm text-gray-500 mt-0.5">Gerez vos destinations, vols et hotels</p>
      </div>

      <div className="flex gap-1 mb-4 bg-gray-100 rounded-lg p-1 w-fit">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
              tab === t.key
                ? "bg-white text-navy-900 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            {t.label} <span className="text-xs text-gray-400 ml-1">{t.count}</span>
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-40">
          <div className="w-6 h-6 border-2 border-navy-900 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <>
          {tab === "destinations" && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {destinations.map((d) => (
                <div key={d.id} className="bg-white rounded-xl border border-gray-100 overflow-hidden">
                  {d.image_url && (
                    <div className="h-36 bg-gray-100 overflow-hidden">
                      <img src={d.image_url} alt={d.name} className="w-full h-full object-cover"
                        onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }} />
                    </div>
                  )}
                  <div className="p-4">
                    <div className="flex items-center justify-between mb-1">
                      <h3 className="font-semibold text-navy-900">{d.name}</h3>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        d.is_active ? "bg-green-50 text-green-700" : "bg-gray-100 text-gray-500"
                      }`}>
                        {d.is_active ? "Actif" : "Inactif"}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 mb-2">{d.country} · {d.destination_type}</p>
                    <p className="text-sm text-gray-600 line-clamp-2">{d.description}</p>
                    {d.highlights?.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {d.highlights.slice(0, 3).map((h: string, i: number) => (
                          <span key={i} className="text-xs bg-navy-50 text-navy-600 px-2 py-0.5 rounded-full">{h}</span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {tab === "flights" && (
            <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-gray-50 text-left">
                      <th className="px-4 py-3 text-xs font-medium text-gray-500">Compagnie</th>
                      <th className="px-4 py-3 text-xs font-medium text-gray-500">Trajet</th>
                      <th className="px-4 py-3 text-xs font-medium text-gray-500">Horaires</th>
                      <th className="px-4 py-3 text-xs font-medium text-gray-500">Duree</th>
                      <th className="px-4 py-3 text-xs font-medium text-gray-500">Escales</th>
                      <th className="px-4 py-3 text-xs font-medium text-gray-500">Prix/adulte</th>
                      <th className="px-4 py-3 text-xs font-medium text-gray-500">Places</th>
                    </tr>
                  </thead>
                  <tbody>
                    {flights.map((f) => (
                      <tr key={f.id} className="border-t border-gray-50 hover:bg-gray-50">
                        <td className="px-4 py-3">
                          <p className="font-medium text-gray-800">{f.airline}</p>
                          <p className="text-xs text-gray-400">{f.flight_number}</p>
                        </td>
                        <td className="px-4 py-3">
                          <p className="text-gray-700">{f.departure_city} → {f.arrival_city}</p>
                          <p className="text-xs text-gray-400">{f.destination_name}</p>
                        </td>
                        <td className="px-4 py-3 text-gray-700">{f.departure_time} → {f.arrival_time}</td>
                        <td className="px-4 py-3 text-gray-600">
                          {Math.floor(f.duration_minutes / 60)}h{String(f.duration_minutes % 60).padStart(2, "0")}
                        </td>
                        <td className="px-4 py-3">
                          <span className={`text-xs px-1.5 py-0.5 rounded ${
                            f.stops === 0 ? "bg-green-50 text-green-700" : "bg-yellow-50 text-yellow-700"
                          }`}>
                            {f.stops === 0 ? "Direct" : `${f.stops}`}
                          </span>
                        </td>
                        <td className="px-4 py-3 font-semibold text-navy-900">{f.price_per_adult} EUR</td>
                        <td className="px-4 py-3">
                          <span className={`text-xs px-1.5 py-0.5 rounded ${
                            f.available_seats > 10 ? "bg-green-50 text-green-700" :
                            f.available_seats > 0 ? "bg-orange-50 text-orange-700" :
                            "bg-red-50 text-red-600"
                          }`}>
                            {f.available_seats}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {tab === "hotels" && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {hotels.map((h) => (
                <div key={h.id} className="bg-white rounded-xl border border-gray-100 overflow-hidden">
                  {h.image_url && (
                    <div className="h-32 bg-gray-100 overflow-hidden">
                      <img src={h.image_url} alt={h.name} className="w-full h-full object-cover"
                        onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }} />
                    </div>
                  )}
                  <div className="p-4">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold text-navy-900 text-sm">{h.name}</h3>
                      <span className="text-gold-400 text-xs">{"★".repeat(h.category)}</span>
                    </div>
                    <p className="text-xs text-gray-500 mb-2">{h.city} · {h.destination_name} · {h.meal_plan}</p>
                    {h.amenities?.length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-2">
                        {h.amenities.slice(0, 4).map((a: string, i: number) => (
                          <span key={i} className="text-xs bg-gray-50 text-gray-500 px-1.5 py-0.5 rounded">{a}</span>
                        ))}
                      </div>
                    )}
                    <p className="font-bold text-navy-900">{h.price_per_night} EUR <span className="text-xs font-normal text-gray-400">/nuit</span></p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
