"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";
import { getChildId, getParentId } from "@/lib/storage";

export default function CreateChildPage() {
  const router = useRouter();

  const [name, setName] = useState("");
  const [age, setAge] = useState(7);
  const [interests, setInterests] = useState("");

  async function createChild() {
    const childId = getChildId();
    const parentId = getParentId();

    if (!parentId) {
      router.push("/auth/login");
      return;
    }

    if (childId) {
      router.push("/child/dashboard");
      return;
    }

    const res = await api.post(`/children/?parent_id=${Number(parentId)}`, {
      name,
      age,
      interests,
      avatar: null,
    });

    localStorage.setItem("jaz_child_id", String(res.data.id));

    router.push("/child/dashboard");
  }

  return (
    <main className="min-h-screen bg-purple-50 flex items-center justify-center p-6">
      <div className="bg-white rounded-2xl shadow p-8 w-full max-w-md">
        <h1 className="text-3xl font-bold text-purple-700 mb-2">
          Create Child Profile
        </h1>

        <p className="text-gray-600 mb-6">
          Set up the child learning and care profile.
        </p>

        <input
          placeholder="Child name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full border rounded-xl px-4 py-3 mb-3"
        />

        <input
          type="number"
          placeholder="Age"
          value={age}
          onChange={(e) => setAge(Number(e.target.value))}
          className="w-full border rounded-xl px-4 py-3 mb-3"
        />

        <textarea
          placeholder="Interests: science, football, Bible stories..."
          value={interests}
          onChange={(e) => setInterests(e.target.value)}
          className="w-full border rounded-xl px-4 py-3 mb-4"
        />

        <button
          onClick={createChild}
          className="w-full bg-purple-700 text-white py-3 rounded-xl font-semibold"
        >
          Create Child Profile
        </button>
      </div>
    </main>
  );
}
