"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import Link from "next/link";
import { getChildId } from "@/lib/storage";

const projectTypes = [
  "story",
  "poem",
  "drawing",
  "comic",
  "music",
  "bible_reflection",
  "school_project",
];

export default function CreativityStudioPage() {
  const [projectType, setProjectType] = useState("story");
  const [prompt, setPrompt] = useState("");
  const [title, setTitle] = useState("");
  const [aiOutput, setAiOutput] = useState("");
  const [loading, setLoading] = useState(false);

  async function generateIdea() {
    if (!prompt.trim()) {
      alert("Please write your creative idea first.");
      return;
    }

    const childId = getChildId();

    if (!childId) {
      alert("No child profile found. Please create a child profile first.");
      return;
    }

    setLoading(true);

    try {
      const res = await api.post("/creativity/generate", {
        child_id: Number(childId),
        project_type: projectType,
        prompt,
      });

      setAiOutput(res.data.ai_output);
    } catch (error) {
      console.error(error);
      alert("JAZ could not generate this right now.");
    } finally {
      setLoading(false);
    }
  }

  async function saveProject() {
    if (!title.trim() || !prompt.trim()) {
      alert("Please add a title and idea before saving.");
      return;
    }

    const childId = getChildId();

    if (!childId) {
      alert("No child profile found. Please create a child profile first.");
      return;
    }

    try {
      const res = await api.post("/creativity/projects", {
        child_id: Number(childId),
        title,
        project_type: projectType,
        prompt,
        child_notes: aiOutput,
      });

      alert(
        `Project saved! You earned ${res.data.stars_earned} Wisdom Stars ⭐`
      );

      setTitle("");
      setPrompt("");
      setAiOutput("");
    } catch (error) {
      console.error(error);
      alert("Could not save project.");
    }
  }

  return (
    <main className="min-h-screen bg-purple-50">
      <header className="bg-white shadow px-6 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-purple-700">
            Creativity Studio
          </h1>
          <p className="text-sm text-gray-500">
            Create stories, poems, comics, music ideas, and projects with JAZ.
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
              Project Title
            </label>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="The Brave Little Star"
              className="w-full border rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2">
              Project Type
            </label>
            <select
              value={projectType}
              onChange={(e) => setProjectType(e.target.value)}
              className="w-full border rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-purple-500"
            >
              {projectTypes.map((type) => (
                <option key={type} value={type}>
                  {type.replace("_", " ")}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2">
              Your Idea
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="I want to write a story about a brave little star..."
              rows={5}
              className="w-full border rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>

          <button
            onClick={generateIdea}
            disabled={loading}
            className="bg-purple-700 text-white px-6 py-3 rounded-xl font-semibold disabled:opacity-50"
          >
            {loading ? "JAZ is creating..." : "Create with JAZ"}
          </button>
        </div>

        {aiOutput && (
          <div className="bg-white rounded-2xl shadow p-6 mt-6">
            <h2 className="text-xl font-bold text-purple-700 mb-3">
              JAZ Creative Idea
            </h2>

            <p className="text-gray-700 whitespace-pre-wrap mb-5">
              {aiOutput}
            </p>

            <button
              onClick={saveProject}
              className="bg-yellow-400 text-gray-900 px-6 py-3 rounded-xl font-semibold"
            >
              Save Project
            </button>
          </div>
        )}
      </section>
    </main>
  );
}
