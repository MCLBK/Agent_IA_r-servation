"use client";

import { useEffect, useState } from "react";
import { getUser } from "@/lib/auth";

export default function SettingsPage() {
  const [user, setUser] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<"profile" | "agent" | "security">("profile");

  useEffect(() => {
    setUser(getUser());
  }, []);

  if (!user) return null;

  const tabs = [
    { key: "profile" as const, label: "Profil agence" },
    { key: "agent" as const, label: "Agent IA" },
    { key: "security" as const, label: "Securite" },
  ];

  return (
    <div>
      <div className="mb-6">
        <h1 className="font-display text-xl font-bold text-navy-900">Parametres</h1>
        <p className="text-sm text-gray-500 mt-0.5">Configuration de votre espace</p>
      </div>

      <div className="flex gap-1 mb-6 bg-gray-100 rounded-lg p-1 w-fit">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setActiveTab(t.key)}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
              activeTab === t.key
                ? "bg-white text-navy-900 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {activeTab === "profile" && (
        <div className="space-y-4 max-w-2xl">
          <div className="bg-white rounded-xl border border-gray-100 p-6">
            <h2 className="font-semibold text-navy-900 text-sm mb-4">Informations de l&apos;agence</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">Nom de l&apos;agence</label>
                <input
                  type="text"
                  defaultValue={user.agency_name || ""}
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-navy-200 focus:border-navy-300"
                  readOnly
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">Slug</label>
                <input
                  type="text"
                  defaultValue="demo"
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm bg-gray-50 text-gray-500"
                  readOnly
                />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-gray-100 p-6">
            <h2 className="font-semibold text-navy-900 text-sm mb-4">Mon compte</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">Prenom</label>
                <input
                  type="text"
                  defaultValue={user.first_name || ""}
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-navy-200 focus:border-navy-300"
                  readOnly
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">Nom</label>
                <input
                  type="text"
                  defaultValue={user.last_name || ""}
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-navy-200 focus:border-navy-300"
                  readOnly
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">Email</label>
                <input
                  type="email"
                  defaultValue={user.email || ""}
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm bg-gray-50 text-gray-500"
                  readOnly
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">Role</label>
                <input
                  type="text"
                  defaultValue={user.role === "admin" ? "Administrateur" : "Agent"}
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm bg-gray-50 text-gray-500"
                  readOnly
                />
              </div>
            </div>
          </div>

          <div className="bg-navy-50 rounded-xl border border-navy-100 p-4">
            <p className="text-xs text-navy-600">
              La modification des informations sera disponible dans une prochaine version.
              Contactez votre administrateur pour toute modification.
            </p>
          </div>
        </div>
      )}

      {activeTab === "agent" && (
        <div className="space-y-4 max-w-2xl">
          <div className="bg-white rounded-xl border border-gray-100 p-6">
            <h2 className="font-semibold text-navy-900 text-sm mb-4">Configuration de l&apos;agent IA</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">Nom de l&apos;agent</label>
                <input
                  type="text"
                  defaultValue="Leila"
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-navy-200 focus:border-navy-300"
                  readOnly
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">Message d&apos;accueil</label>
                <textarea
                  defaultValue="Bonjour ! Je suis Leila, votre assistante voyage. Comment puis-je vous aider a planifier votre prochain voyage ?"
                  rows={3}
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-navy-200 focus:border-navy-300 resize-none"
                  readOnly
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">Fournisseur IA</label>
                <div className="flex items-center gap-3">
                  <span className="text-sm text-gray-700 bg-gray-50 border border-gray-200 rounded-lg px-3 py-2">
                    Mode Demo (regles)
                  </span>
                  <span className="text-xs text-gray-400">ou Ollama (local)</span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-gray-100 p-6">
            <h2 className="font-semibold text-navy-900 text-sm mb-4">Comportement</h2>
            <div className="space-y-3">
              <label className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-700">Escalade automatique</p>
                  <p className="text-xs text-gray-400">Transfert vers un conseiller pour les cas complexes</p>
                </div>
                <div className="w-10 h-5 bg-green-500 rounded-full relative cursor-not-allowed">
                  <div className="w-4 h-4 bg-white rounded-full absolute right-0.5 top-0.5 shadow-sm" />
                </div>
              </label>
              <label className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-700">Double verification des prix</p>
                  <p className="text-xs text-gray-400">Reverification avant confirmation de reservation</p>
                </div>
                <div className="w-10 h-5 bg-green-500 rounded-full relative cursor-not-allowed">
                  <div className="w-4 h-4 bg-white rounded-full absolute right-0.5 top-0.5 shadow-sm" />
                </div>
              </label>
              <label className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-700">Collecte RGPD</p>
                  <p className="text-xs text-gray-400">Demande de consentement obligatoire</p>
                </div>
                <div className="w-10 h-5 bg-green-500 rounded-full relative cursor-not-allowed">
                  <div className="w-4 h-4 bg-white rounded-full absolute right-0.5 top-0.5 shadow-sm" />
                </div>
              </label>
            </div>
          </div>
        </div>
      )}

      {activeTab === "security" && (
        <div className="space-y-4 max-w-2xl">
          <div className="bg-white rounded-xl border border-gray-100 p-6">
            <h2 className="font-semibold text-navy-900 text-sm mb-4">Regles de securite actives</h2>
            <div className="space-y-2">
              {[
                { label: "Isolation multi-tenant", desc: "Donnees isolees par agence", active: true },
                { label: "Pas de donnees bancaires", desc: "Jamais collectees dans le chat", active: true },
                { label: "Pas de passeport (v1)", desc: "Non collecte dans la conversation", active: true },
                { label: "Anti prompt-injection", desc: "Instructions systeme protegees", active: true },
                { label: "Double verification prix", desc: "Avant presentation et confirmation", active: true },
                { label: "Audit trail", desc: "Journalisation des actions", active: true },
              ].map((rule, i) => (
                <div key={i} className="flex items-center gap-3 py-2 border-b border-gray-50 last:border-0">
                  <div className={`w-2 h-2 rounded-full ${rule.active ? "bg-green-500" : "bg-gray-300"}`} />
                  <div>
                    <p className="text-sm text-gray-700">{rule.label}</p>
                    <p className="text-xs text-gray-400">{rule.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-xl border border-gray-100 p-6">
            <h2 className="font-semibold text-navy-900 text-sm mb-4">Conformite RGPD</h2>
            <div className="space-y-2 text-sm text-gray-600">
              <p>- Consentement explicite demande avant collecte</p>
              <p>- Droit a l&apos;oubli implementable</p>
              <p>- Donnees stockees localement (SQLite)</p>
              <p>- Aucune donnee transmise a des tiers</p>
              <p>- Pas de tracking publicitaire</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
