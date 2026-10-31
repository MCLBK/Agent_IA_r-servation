const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    if (typeof window !== "undefined") {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    throw new Error("Non autorise");
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Erreur ${res.status}`);
  }

  return res.json();
}

export const api = {
  // Auth
  login: (email: string, password: string) =>
    request<any>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  me: () => request<any>("/auth/me"),

  // Chat (public)
  chat: (message: string, sessionId?: string, agencySlug = "demo") =>
    request<any>("/chat", {
      method: "POST",
      body: JSON.stringify({ message, session_id: sessionId, agency_slug: agencySlug }),
    }),
  getAgencyPublic: (slug: string) => request<any>(`/chat/agency/${slug}`),

  // Dashboard
  getStats: () => request<any>("/dashboard/stats"),

  // Catalog
  getDestinations: () => request<any[]>("/catalog/destinations"),
  createDestination: (data: any) =>
    request<any>("/catalog/destinations", { method: "POST", body: JSON.stringify(data) }),
  updateDestination: (id: number, data: any) =>
    request<any>(`/catalog/destinations/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteDestination: (id: number) =>
    request<any>(`/catalog/destinations/${id}`, { method: "DELETE" }),

  getFlights: (destId?: number) =>
    request<any[]>(`/catalog/flights${destId ? `?destination_id=${destId}` : ""}`),
  createFlight: (data: any) =>
    request<any>("/catalog/flights", { method: "POST", body: JSON.stringify(data) }),
  deleteFlight: (id: number) =>
    request<any>(`/catalog/flights/${id}`, { method: "DELETE" }),

  getHotels: (destId?: number) =>
    request<any[]>(`/catalog/hotels${destId ? `?destination_id=${destId}` : ""}`),
  createHotel: (data: any) =>
    request<any>("/catalog/hotels", { method: "POST", body: JSON.stringify(data) }),
  deleteHotel: (id: number) =>
    request<any>(`/catalog/hotels/${id}`, { method: "DELETE" }),

  getPackages: () => request<any[]>("/catalog/packages"),

  // Bookings
  getBookings: (status?: string) =>
    request<any[]>(`/bookings${status ? `?status=${status}` : ""}`),
  getBooking: (id: number) => request<any>(`/bookings/${id}`),
  confirmBooking: (id: number) =>
    request<any>(`/bookings/${id}/confirm`, { method: "POST" }),
  cancelBooking: (id: number, reason = "") =>
    request<any>(`/bookings/${id}/cancel?reason=${encodeURIComponent(reason)}`, { method: "POST" }),

  // Conversations
  getConversations: (status?: string, needsHuman?: boolean) => {
    const params = new URLSearchParams();
    if (status) params.set("status", status);
    if (needsHuman !== undefined) params.set("needs_human", String(needsHuman));
    const qs = params.toString();
    return request<any[]>(`/conversations${qs ? `?${qs}` : ""}`);
  },
  getConversation: (id: number) => request<any>(`/conversations/${id}`),
  assignConversation: (id: number) =>
    request<any>(`/conversations/${id}/assign`, { method: "POST" }),

  // Travelers
  getTravelers: () => request<any[]>("/travelers"),
  getTraveler: (id: number) => request<any>(`/travelers/${id}`),
};
