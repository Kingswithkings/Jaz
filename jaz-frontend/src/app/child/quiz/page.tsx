"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import Link from "next/link";
import { getChildId } from "@/lib/storage";

export default function QuizPage() {
  const [topic, setTopic] = useState("");
  const [difficulty, setDifficulty] = useState("easy");
  const [numberOfQuestions, setNumberOfQuestions] = useState(5);
  const [quizId, setQuizId] = useState<number | null>(null);
  const [questions, setQuestions] = useState("");
  const [score, setScore] = useState(0);
  const [loading, setLoading] = useState(false);

  async function generateQuiz() {
    if (!topic.trim()) {
      alert("Please enter a quiz topic.");
      return;
    }

    const childId = getChildId();

    if (!childId) {
      alert("No child profile found. Please create a child profile first.");
      return;
    }

    setLoading(true);
    setQuestions("");
    setQuizId(null);

    try {
      const res = await api.post("/quiz/generate", {
        child_id: Number(childId),
        topic,
        difficulty,
        number_of_questions: numberOfQuestions,
      });

      setQuizId(res.data.quiz_id);
      setQuestions(res.data.questions);
    } catch (error) {
      console.error(error);
      alert("JAZ could not generate the quiz.");
    } finally {
      setLoading(false);
    }
  }

  async function submitQuiz() {
    if (!quizId) {
      alert("Generate a quiz first.");
      return;
    }

    const childId = getChildId();

    if (!childId) {
      alert("No child profile found. Please create a child profile first.");
      return;
    }

    try {
      const res = await api.post("/quiz/submit", {
        child_id: Number(childId),
        quiz_id: quizId,
        score,
      });

      alert(
        `Quiz submitted! You earned ${res.data.stars_earned} Wisdom Stars ⭐`
      );
    } catch (error) {
      console.error(error);
      alert("Could not submit quiz.");
    }
  }

  return (
    <main className="min-h-screen bg-yellow-50">
      <header className="bg-white shadow px-6 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-purple-700">
            Quiz Time
          </h1>
          <p className="text-sm text-gray-500">
            Learn and earn Wisdom Stars with JAZ quizzes.
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
              Quiz Topic
            </label>

            <input
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Solar System, Fractions, Animals..."
              className="w-full border rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2">
              Difficulty
            </label>

            <select
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
              className="w-full border rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2">
              Number of Questions
            </label>

            <input
              type="number"
              value={numberOfQuestions}
              onChange={(e) => setNumberOfQuestions(Number(e.target.value))}
              min={1}
              max={10}
              className="w-full border rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>

          <button
            onClick={generateQuiz}
            disabled={loading}
            className="bg-purple-700 text-white px-6 py-3 rounded-xl font-semibold disabled:opacity-50"
          >
            {loading ? "Generating Quiz..." : "Generate Quiz"}
          </button>
        </div>

        {questions && (
          <div className="bg-white rounded-2xl shadow p-6 mt-6">
            <h2 className="text-xl font-bold text-purple-700 mb-3">
              Your Quiz
            </h2>

            <pre className="bg-gray-50 p-4 rounded-xl whitespace-pre-wrap text-sm">
              {questions}
            </pre>

            <div className="mt-5">
              <label className="block text-sm font-semibold mb-2">
                Your Score
              </label>

              <input
                type="number"
                value={score}
                onChange={(e) => setScore(Number(e.target.value))}
                min={0}
                max={numberOfQuestions}
                className="w-full border rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>

            <button
              onClick={submitQuiz}
              className="mt-4 bg-yellow-400 text-gray-900 px-6 py-3 rounded-xl font-semibold"
            >
              Submit Quiz
            </button>
          </div>
        )}
      </section>
    </main>
  );
}
