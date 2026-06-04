"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import Link from "next/link";
import { getChildId, getParentId } from "@/lib/storage";
import ChildSelector from "@/components/ChildSelector";

export default function ParentSafetyPage() {
  const [dailyLimit, setDailyLimit] = useState(120);
  const [safeMode, setSafeMode] = useState("strict");
  const [internetMonitoring, setInternetMonitoring] = useState("yes");
  const [aiMonitoring, setAiMonitoring] = useState("yes");
  const [blockedCategories, setBlockedCategories] = useState(
    "adult,violence,gambling,drugs,stranger_chat"
  );
  const [allowedCategories, setAllowedCategories] = useState(
    "education,creativity,bible,science,maths,reading"
  );

  async function saveSettings() {
    const parentId = getParentId();
    const childId = getChildId();

    if (!parentId || !childId) {
      alert("No parent or child profile found. Please login and create a child profile first.");
      return;
    }

    const parentIdNumber = Number(parentId);
    const childIdNumber = Number(childId);

    if (Number.isNaN(parentIdNumber) || Number.isNaN(childIdNumber)) {
      alert("Invalid parent or child profile found. Please login again.");
      return;
    }

    try {
      await api.post("/safety/settings", {
        parent_id: parentIdNumber,
        child_id: childIdNumber,
        daily_screen_time_limit_minutes: dailyLimit,
        child_safe_mode: safeMode,
        internet_monitoring_enabled: internetMonitoring,
        ai_chat_monitoring_enabled: aiMonitoring,
        blocked_categories: blockedCategories,
        allowed_categories: allowedCategories,
      });

      alert("Safety settings saved.");
    } catch (error) {
      console.error(error);
      alert("Could not save safety settings.");
    }
  }

  return (
    <main className="min-h-screen bg-gray-50">
      <header className="bg-white shadow px-6 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-purple-700">
            Parent Safety Settings
          </h1>
          <p className="text-sm text-gray-500">
            Control screen time, safe mode, monitoring, and content categories.
          </p>
        </div>

        <Link href="/parent/dashboard" className="text-purple-700 font-semibold">
          Back
        </Link>
      </header>

      <section className="max-w-4xl mx-auto p-6">
        <ChildSelector />

        <Link
          href="/child/create"
          className="inline-block mb-6 bg-blue-500 text-white px-5 py-3 rounded-xl font-semibold"
        >
          Add Child
        </Link>

        <div className="bg-white rounded-2xl shadow p-6 space-y-6">
          <div>
            <label className="block font-semibold mb-2">
              Daily Screen-Time Limit
            </label>

            <input
              type="number"
              value={dailyLimit}
              onChange={(e) => setDailyLimit(Number(e.target.value))}
              className="w-full border rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-purple-500"
            />

            <p className="text-sm text-gray-500 mt-1">
              Time limit in minutes per day.
            </p>
          </div>

          <div>
            <label className="block font-semibold mb-2">
              Child Safe Mode
            </label>

            <select
              value={safeMode}
              onChange={(e) => setSafeMode(e.target.value)}
              className="w-full border rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="strict">Strict</option>
              <option value="balanced">Balanced</option>
            </select>
          </div>

          <div>
            <label className="block font-semibold mb-2">
              Internet Monitoring
            </label>

            <select
              value={internetMonitoring}
              onChange={(e) => setInternetMonitoring(e.target.value)}
              className="w-full border rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="yes">Enabled</option>
              <option value="no">Disabled</option>
            </select>
          </div>

          <div>
            <label className="block font-semibold mb-2">
              AI Chat Monitoring
            </label>

            <select
              value={aiMonitoring}
              onChange={(e) => setAiMonitoring(e.target.value)}
              className="w-full border rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="yes">Enabled</option>
              <option value="no">Disabled</option>
            </select>
          </div>

          <div>
            <label className="block font-semibold mb-2">
              Blocked Categories
            </label>

            <textarea
              value={blockedCategories}
              onChange={(e) => setBlockedCategories(e.target.value)}
              rows={3}
              className="w-full border rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>

          <div>
            <label className="block font-semibold mb-2">
              Allowed Categories
            </label>

            <textarea
              value={allowedCategories}
              onChange={(e) => setAllowedCategories(e.target.value)}
              rows={3}
              className="w-full border rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>

          <button
            onClick={saveSettings}
            className="bg-purple-700 text-white px-6 py-3 rounded-xl font-semibold"
          >
            Save Safety Settings
          </button>
        </div>
      </section>
    </main>
  );
}
