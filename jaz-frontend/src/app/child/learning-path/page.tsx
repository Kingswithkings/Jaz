"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { getChildId } from "@/lib/storage";
import Link from "next/link";

type LearningPath = {
  id: number;
  title: string;
  description: string;
  path_content: string;
  status: string;
};

export default function LearningPathPage() {
  const [focusArea, setFocusArea] = useState("");
  const [paths, setPaths] = useState<LearningPath[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadPaths() {
      const childId = getChildId();
      if (!childId) return;

      const res = await api.get(`/learning-path/${childId}`);
      setPaths(res.data.learning_paths);
    }

    loadPaths();
  }, []);

  async function refreshPaths() {
    const childId = getChildId();
    if (!childId) return;

    const res = await api.get(`/learning-path/${childId}`);
    setPaths(res.data.learning_paths);
  }

  async function generatePath() {
    const childId = getChildId();

    if (!childId) {
      alert("No child selected.");
      return;
    }

    setLoading(true);

    try {
      await api.post("/learning-path/generate", {
        child_id: Number(childId),
        focus_area: focusArea || null,
      });

      await refreshPaths();
      setFocusArea("");
      alert("Personalized learning path generated.");
    } catch (error) {
      console.error(error);
      alert("Could not generate learning path.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-blue-50">
      <header className="bg-white shadow px-6 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-purple-700">
            AI Learning Path
          </h1>
          <p className="text-sm text-gray-500">
            JAZ creates a personalized 7-day path from your goals and interests.
          </p>
        </div>

        <Link href="/child/dashboard" className="text-purple-700 font-semibold">
          Back
        </Link>
      </header>

      <section className="max-w-5xl mx-auto p-6">
        <div className="bg-white rounded-2xl shadow p-6 mb-6">
          <label className="block font-semibold mb-2">
            Focus Area
          </label>

          <input
            value={focusArea}
            onChange={(e) => setFocusArea(e.target.value)}
            placeholder="Maths, reading, science, Bible stories, coding..."
            className="w-full border rounded-xl px-4 py-3 mb-4"
          />

          <button
            onClick={generatePath}
            disabled={loading}
            className="bg-purple-700 text-white px-6 py-3 rounded-xl font-semibold disabled:opacity-50"
          >
            {loading ? "Generating..." : "Generate Learning Path"}
          </button>
        </div>

        <div className="space-y-6">
          {paths.length === 0 && (
            <div className="bg-white rounded-2xl shadow p-6">
              <p className="text-gray-600">
                No learning paths generated yet.
              </p>
            </div>
          )}

          {paths.map((path) => (
            <div key={path.id} className="bg-white rounded-2xl shadow p-6">
              <div className="flex justify-between mb-3">
                <h2 className="text-xl font-bold text-purple-700">
                  {path.title}
                </h2>

                <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm">
                  {path.status}
                </span>
              </div>

              <p className="text-gray-600 mb-4">
                {path.description}
              </p>

              <pre className="whitespace-pre-wrap bg-gray-50 rounded-xl p-4 text-sm text-gray-700">
                {path.path_content}
              </pre>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
