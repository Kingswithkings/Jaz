"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { getChildId } from "@/lib/storage";
import Link from "next/link";

export default function ChildProfilePage() {
  const [name, setName] = useState("");
  const [age, setAge] = useState(7);
  const [interests, setInterests] = useState("");
  const [avatar, setAvatar] = useState("");

  useEffect(() => {
    async function loadProfile() {
      const childId = getChildId();

      if (!childId) {
        alert("No child selected.");
        return;
      }

      const res = await api.get(`/children/profile/${childId}`);

      setName(res.data.name);
      setAge(res.data.age);
      setInterests(res.data.interests || "");
      setAvatar(res.data.avatar || "");
    }

    loadProfile();
  }, []);

  async function updateProfile() {
    const childId = getChildId();

    if (!childId) {
      alert("No child selected.");
      return;
    }

    await api.put(`/children/${childId}`, {
      name,
      age,
      interests,
      avatar,
    });

    alert("Child profile updated.");
  }

  return (
    <main className="min-h-screen bg-purple-50">
      <header className="bg-white shadow px-6 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-purple-700">
            Child Profile
          </h1>
          <p className="text-sm text-gray-500">
            Edit child profile, avatar, age, and interests.
          </p>
        </div>

        <Link href="/child/dashboard" className="text-purple-700 font-semibold">
          Back
        </Link>
      </header>

      <section className="max-w-3xl mx-auto p-6">
        <div className="bg-white rounded-2xl shadow p-6 space-y-5">
          <div>
            <label className="block font-semibold mb-2">Child Name</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full border rounded-xl px-4 py-3"
            />
          </div>

          <div>
            <label className="block font-semibold mb-2">Age</label>
            <input
              type="number"
              value={age}
              onChange={(e) => setAge(Number(e.target.value))}
              className="w-full border rounded-xl px-4 py-3"
            />
          </div>

          <div>
            <label className="block font-semibold mb-2">Interests</label>
            <textarea
              value={interests}
              onChange={(e) => setInterests(e.target.value)}
              rows={4}
              placeholder="Science, football, Bible stories, coding..."
              className="w-full border rounded-xl px-4 py-3"
            />
          </div>

          <div>
            <label className="block font-semibold mb-2">Avatar URL</label>
            <input
              value={avatar}
              onChange={(e) => setAvatar(e.target.value)}
              placeholder="https://..."
              className="w-full border rounded-xl px-4 py-3"
            />
          </div>

          <button
            onClick={updateProfile}
            className="bg-purple-700 text-white px-6 py-3 rounded-xl font-semibold"
          >
            Save Profile
          </button>
        </div>
      </section>
    </main>
  );
}
