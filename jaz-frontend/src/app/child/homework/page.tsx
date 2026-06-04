"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import Link from "next/link";
import { getChildId } from "@/lib/storage";

export default function HomeworkHelperPage() {
  const [subject, setSubject] = useState("Maths");
  const [question, setQuestion] = useState("");
  const [explanation, setExplanation] = useState("");
  const [loading, setLoading] = useState(false);

  async function askForHelp() {
    if (!question.trim()) {
      alert("Please type your homework question.");
      return;
    }

    const childId = getChildId();

    if (!childId) {
      alert("No child profile found. Please create a child profile first.");
      return;
    }

    setLoading(true);
    setExplanation("");

    try {
      const res = await api.post("/homework/help", {
        child_id: Number(childId),
        subject,
        question,
      });

      setExplanation(res.data.explanation);

      alert(`You earned ${res.data.stars_earned} Wisdom Stars ⭐`);
    } catch (error) {
      console.error(error);
      alert("JAZ could not help with this homework right now.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-blue-50">
      <header className="bg-white shadow px-6 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-purple-700">
            Homework Helper
          </h1>
          <p className="text-sm text-gray-500">
            JAZ helps you understand your homework step by step.
          </p>
        </div>

        <Link href="/child/dashboard" className="text-purple-700 font-semibold">
          Back
        </Link>
      </header>

      <section className="max-w-4xl mx-auto p-6">
        <div className="bg-white rounded-2xl shadow p-6 space-y-5">
          <div>
            <label className="block text-sm font-semibold mb-2">
              Subject
            </label>

            <select
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="w-full border rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option>Maths</option>
              <option>English</option>
              <option>Science</option>
              <option>History</option>
              <option>Geography</option>
              <option>Coding</option>
              <option>Bible Studies</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2">
              Homework Question
            </label>

            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Example: Can you help me understand 12 divided by 3?"
              rows={5}
              className="w-full border rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>

          <button
            onClick={askForHelp}
            disabled={loading}
            className="bg-purple-700 text-white px-6 py-3 rounded-xl font-semibold disabled:opacity-50"
          >
            {loading ? "JAZ is helping..." : "Ask JAZ for Help"}
          </button>
        </div>

        {explanation && (
          <div className="bg-white rounded-2xl shadow p-6 mt-6">
            <h2 className="text-xl font-bold text-purple-700 mb-3">
              JAZ Explanation
            </h2>

            <p className="text-gray-700 whitespace-pre-wrap">
              {explanation}
            </p>
          </div>
        )}
      </section>
    </main>
  );
}
