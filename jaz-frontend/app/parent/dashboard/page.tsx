"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { getParentId } from "@/lib/storage";
import AuthGuard from "@/components/AuthGuard";
import LogoutButton from "@/components/LogoutButton";
import ChildSelector from "@/components/ChildSelector";

type ChildSummary = {
  child_id: number;
  name: string;
  age: number;
  level: string;
  rating: number;
  wisdom_stars: number;
  total_learning_activities: number;
  total_ai_conversations: number;
  total_internet_minutes: number;
  educational_minutes: number;
  unsafe_activity_count: number;
  learning_score: number;
};

export default function ParentDashboard() {
  const [children, setChildren] = useState<ChildSummary[]>([]);

  useEffect(() => {
    const parentId = getParentId();

    if (!parentId) {
      alert("No parent account found. Please login first.");
      return;
    }

    api
      .get(`/parents/${parentId}/summary`)
      .then((res) => setChildren(res.data.children))
      .catch((err) => console.error(err));
  }, []);

  async function generateReport(
    childId: number,
    reportType: "daily" | "weekly",
  ) {
    const parentId = getParentId();

    if (!parentId) {
      alert("No parent account found. Please login first.");
      return;
    }

    const res = await api.post("/parents/reports/generate", {
      parent_id: Number(parentId),
      child_id: childId,
      report_type: reportType,
      send_email: true,
    });

    alert(`Report generated and email sent: ${res.data.email_sent}`);
    window.open(
      `${process.env.NEXT_PUBLIC_API_URL}${res.data.download_url}`,
      "_blank",
    );
  }

  return (
    <AuthGuard>
      <main className="min-h-screen bg-gray-50 p-6">
        <section className="max-w-6xl mx-auto">
          <div className="flex justify-between gap-4 items-start mb-8">
            <div>
              <h1 className="text-3xl font-bold text-purple-700 mb-2">
                Parent Dashboard
              </h1>

              <p className="text-gray-600">
                Monitor learning, safety, internet activity, and child growth.
              </p>
            </div>

            <LogoutButton />
          </div>

          <ChildSelector />

        <div className="flex flex-wrap gap-3 mb-6">
          <Link
            href="/child/create"
            className="bg-blue-500 text-white px-5 py-3 rounded-xl font-semibold"
          >
            Add Child
          </Link>

          <Link
            href="/parent/internet"
            className="bg-yellow-400 text-gray-900 px-5 py-3 rounded-xl font-semibold"
          >
            Internet Monitoring
          </Link>

          <Link
            href="/parent/safety"
            className="bg-purple-700 text-white px-5 py-3 rounded-xl font-semibold"
          >
            Safety Settings
          </Link>

          <Link
            href="/parent/reports"
            className="bg-green-500 text-white px-5 py-3 rounded-xl font-semibold"
          >
            Parent Reports
          </Link>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {children.map((child) => (
            <div key={child.child_id} className="bg-white rounded-2xl shadow p-6">
              <h2 className="text-2xl font-bold">{child.name}</h2>
              <p className="text-gray-600">Age: {child.age}</p>

              <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                <div className="bg-purple-50 p-4 rounded-xl">
                  <p>Level</p>
                  <strong>{child.level}</strong>
                </div>

                <div className="bg-yellow-50 p-4 rounded-xl">
                  <p>Rating</p>
                  <strong>{"*".repeat(child.rating)}</strong>
                </div>

                <div className="bg-green-50 p-4 rounded-xl">
                  <p>Wisdom Stars</p>
                  <strong>{child.wisdom_stars}</strong>
                </div>

                <div className="bg-blue-50 p-4 rounded-xl">
                  <p>Learning Score</p>
                  <strong>{child.learning_score}%</strong>
                </div>

                <div className="bg-gray-50 p-4 rounded-xl">
                  <p>Internet Time</p>
                  <strong>{child.total_internet_minutes} mins</strong>
                </div>

                <div className="bg-red-50 p-4 rounded-xl">
                  <p>Unsafe Flags</p>
                  <strong>{child.unsafe_activity_count}</strong>
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => generateReport(child.child_id, "daily")}
                  className="bg-purple-700 text-white px-4 py-2 rounded-xl"
                >
                  Daily Report
                </button>

                <button
                  onClick={() => generateReport(child.child_id, "weekly")}
                  className="bg-yellow-400 text-gray-900 px-4 py-2 rounded-xl"
                >
                  Weekly Report
                </button>
              </div>
            </div>
          ))}
        </div>
        </section>
      </main>
    </AuthGuard>
  );
}
