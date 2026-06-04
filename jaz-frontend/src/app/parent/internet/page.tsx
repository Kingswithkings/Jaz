"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import Link from "next/link";
import { getChildId, getParentId } from "@/lib/storage";
import ChildSelector from "@/components/ChildSelector";

type InternetActivity = {
  id: number;
  website_or_app: string;
  url: string | null;
  category: string;
  duration_minutes: number;
  learning_value: string;
  summary: string | null;
  created_at: string;
};

export default function ParentInternetPage() {
  const [period, setPeriod] = useState<"daily" | "weekly">("daily");
  const [activities, setActivities] = useState<InternetActivity[]>([]);
  const [totalMinutes, setTotalMinutes] = useState(0);
  const [educationalMinutes, setEducationalMinutes] = useState(0);
  const [unsafeCount, setUnsafeCount] = useState(0);

  useEffect(() => {
    async function loadReport() {
      const parentId = getParentId();
      const childId = getChildId();

      if (!parentId || !childId) {
        alert("No parent or child profile found. Please login and create a child profile first.");
        return;
      }

      if (Number.isNaN(Number(parentId))) {
        alert("Invalid parent profile found. Please login again.");
        return;
      }

      try {
        const res = await api.get(`/internet/${childId}/${period}`);

        setActivities(res.data.activities || []);
        setTotalMinutes(res.data.total_minutes || 0);
        setEducationalMinutes(res.data.educational_minutes || 0);
        setUnsafeCount(res.data.unsafe_activity_count || 0);
      } catch (error) {
        console.error(error);
        alert("Could not load internet monitoring report.");
      }
    }

    loadReport();
  }, [period]);

  return (
    <main className="min-h-screen bg-gray-50">
      <header className="bg-white shadow px-6 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-purple-700">
            Internet Monitoring
          </h1>
          <p className="text-sm text-gray-500">
            See what your child has consumed online daily or weekly.
          </p>
        </div>

        <Link href="/parent/dashboard" className="text-purple-700 font-semibold">
          Back
        </Link>
      </header>

      <section className="max-w-6xl mx-auto p-6">
        <ChildSelector />

        <Link
          href="/child/create"
          className="inline-block mb-6 bg-blue-500 text-white px-5 py-3 rounded-xl font-semibold"
        >
          Add Child
        </Link>

        <div className="mb-6 flex gap-3">
          <button
            onClick={() => setPeriod("daily")}
            className={`px-5 py-3 rounded-xl font-semibold ${
              period === "daily"
                ? "bg-purple-700 text-white"
                : "bg-white text-gray-700"
            }`}
          >
            Daily
          </button>

          <button
            onClick={() => setPeriod("weekly")}
            className={`px-5 py-3 rounded-xl font-semibold ${
              period === "weekly"
                ? "bg-purple-700 text-white"
                : "bg-white text-gray-700"
            }`}
          >
            Weekly
          </button>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-2xl shadow p-6">
            <p className="text-gray-500">Total Internet Time</p>
            <h2 className="text-3xl font-bold text-purple-700">
              {totalMinutes} mins
            </h2>
          </div>

          <div className="bg-white rounded-2xl shadow p-6">
            <p className="text-gray-500">Educational Time</p>
            <h2 className="text-3xl font-bold text-green-600">
              {educationalMinutes} mins
            </h2>
          </div>

          <div className="bg-white rounded-2xl shadow p-6">
            <p className="text-gray-500">Unsafe Flags</p>
            <h2 className="text-3xl font-bold text-red-600">
              {unsafeCount}
            </h2>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow overflow-hidden">
          <div className="p-5 border-b">
            <h2 className="text-xl font-bold text-gray-800">
              Activity History
            </h2>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-purple-50">
                <tr>
                  <th className="text-left p-4">Website/App</th>
                  <th className="text-left p-4">Category</th>
                  <th className="text-left p-4">Time</th>
                  <th className="text-left p-4">Learning Value</th>
                  <th className="text-left p-4">Summary</th>
                </tr>
              </thead>

              <tbody>
                {activities.length === 0 && (
                  <tr>
                    <td colSpan={5} className="p-6 text-center text-gray-500">
                      No internet activity recorded.
                    </td>
                  </tr>
                )}

                {activities.map((activity) => (
                  <tr key={activity.id} className="border-t">
                    <td className="p-4 font-semibold">
                      {activity.website_or_app}
                      {activity.url && (
                        <p className="text-xs text-gray-500 break-all">
                          {activity.url}
                        </p>
                      )}
                    </td>

                    <td className="p-4">{activity.category}</td>

                    <td className="p-4">
                      {activity.duration_minutes} mins
                    </td>

                    <td className="p-4">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          activity.learning_value === "educational"
                            ? "bg-green-100 text-green-700"
                            : activity.learning_value === "unsafe"
                            ? "bg-red-100 text-red-700"
                            : "bg-gray-100 text-gray-700"
                        }`}
                      >
                        {activity.learning_value}
                      </span>
                    </td>

                    <td className="p-4 text-gray-600">
                      {activity.summary || "No summary"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </main>
  );
}
