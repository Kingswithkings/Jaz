"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { getChildId } from "@/lib/storage";
import Link from "next/link";

type Goal = {
  id: number;
  title: string;
  description: string | null;
  category: string;
  target_stars: number;
  current_stars: number;
  status: string;
};

export default function LearningGoalsPage() {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("general");
  const [targetStars, setTargetStars] = useState(50);

  useEffect(() => {
    async function loadGoals() {
      const childId = getChildId();

      if (!childId) return;

      const res = await api.get(`/goals/${childId}`);
      setGoals(res.data.goals);
    }

    loadGoals();
  }, []);

  async function refreshGoals() {
    const childId = getChildId();

    if (!childId) return;

    const res = await api.get(`/goals/${childId}`);
    setGoals(res.data.goals);
  }

  async function createGoal() {
    const childId = getChildId();

    if (!childId) {
      alert("No child selected.");
      return;
    }

    if (!title.trim()) {
      alert("Please enter a learning goal.");
      return;
    }

    await api.post("/goals/", {
      child_id: Number(childId),
      title,
      description,
      category,
      target_stars: targetStars,
    });

    setTitle("");
    setDescription("");
    setCategory("general");
    setTargetStars(50);

    refreshGoals();
  }

  async function addProgress(goal: Goal) {
    const newStars = goal.current_stars + 10;

    await api.put(`/goals/${goal.id}`, {
      current_stars: newStars,
    });

    refreshGoals();
  }

  async function deleteGoal(goalId: number) {
    await api.delete(`/goals/${goalId}`);
    refreshGoals();
  }

  return (
    <main className="min-h-screen bg-purple-50">
      <header className="bg-white shadow px-6 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-purple-700">
            Learning Goals
          </h1>
          <p className="text-sm text-gray-500">
            Set targets and grow step by step.
          </p>
        </div>

        <Link href="/child/dashboard" className="text-purple-700 font-semibold">
          Back
        </Link>
      </header>

      <section className="max-w-5xl mx-auto p-6 grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl shadow p-6 space-y-4">
          <h2 className="text-xl font-bold text-purple-700">
            New Goal
          </h2>

          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Learn fractions"
            className="w-full border rounded-xl px-4 py-3"
          />

          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="I want to understand fractions better."
            rows={4}
            className="w-full border rounded-xl px-4 py-3"
          />

          <input
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            placeholder="maths, science, reading..."
            className="w-full border rounded-xl px-4 py-3"
          />

          <input
            type="number"
            value={targetStars}
            onChange={(e) => setTargetStars(Number(e.target.value))}
            className="w-full border rounded-xl px-4 py-3"
          />

          <button
            onClick={createGoal}
            className="bg-purple-700 text-white px-6 py-3 rounded-xl font-semibold"
          >
            Create Goal
          </button>
        </div>

        <div className="space-y-4">
          {goals.length === 0 && (
            <div className="bg-white rounded-2xl shadow p-6">
              <p className="text-gray-600">
                No learning goals yet.
              </p>
            </div>
          )}

          {goals.map((goal) => {
            const progress = Math.min(
              100,
              Math.round((goal.current_stars / goal.target_stars) * 100)
            );

            return (
              <div key={goal.id} className="bg-white rounded-2xl shadow p-6">
                <div className="flex justify-between">
                  <h3 className="text-lg font-bold text-purple-700">
                    {goal.title}
                  </h3>

                  <span className="text-sm bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full">
                    {goal.status}
                  </span>
                </div>

                <p className="text-gray-600 mt-2">
                  {goal.description}
                </p>

                <p className="text-sm text-gray-500 mt-2">
                  Category: {goal.category}
                </p>

                <div className="mt-4">
                  <div className="flex justify-between text-sm mb-1">
                    <span>{goal.current_stars} stars</span>
                    <span>{goal.target_stars} stars</span>
                  </div>

                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-purple-700 h-3 rounded-full"
                      style={{ width: `${progress}%` }}
                    />
                  </div>

                  <p className="text-sm text-gray-500 mt-1">
                    {progress}% completed
                  </p>
                </div>

                <div className="flex gap-3 mt-4">
                  <button
                    onClick={() => addProgress(goal)}
                    className="bg-yellow-400 text-gray-900 px-4 py-2 rounded-xl text-sm font-semibold"
                  >
                    Add Progress
                  </button>

                  <button
                    onClick={() => deleteGoal(goal.id)}
                    className="bg-red-500 text-white px-4 py-2 rounded-xl text-sm font-semibold"
                  >
                    Delete
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </section>
    </main>
  );
}
