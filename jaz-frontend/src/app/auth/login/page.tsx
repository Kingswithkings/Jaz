"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function login() {
    const res = await api.post("/auth/login", {
      email,
      password,
    });

    localStorage.setItem("jaz_token", res.data.token);
    localStorage.setItem("jaz_parent_id", String(res.data.parent_id));

    router.push("/parent/dashboard");
  }

  return (
    <main className="min-h-screen bg-yellow-50 flex items-center justify-center p-6">
      <div className="bg-white rounded-2xl shadow p-8 w-full max-w-md">
        <h1 className="text-3xl font-bold text-purple-700 mb-2">
          Parent Login
        </h1>

        <p className="text-gray-600 mb-6">
          Login to manage your child learning and safety dashboard.
        </p>

        <input
          placeholder="Email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full border rounded-xl px-4 py-3 mb-3"
        />

        <input
          placeholder="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full border rounded-xl px-4 py-3 mb-4"
        />

        <button
          onClick={login}
          className="w-full bg-purple-700 text-white py-3 rounded-xl font-semibold"
        >
          Login
        </button>

        <p className="text-sm text-gray-600 mt-4">
          New to JAZ?{" "}
          <Link href="/auth/register" className="text-purple-700 font-semibold">
            Create account
          </Link>
        </p>
      </div>
    </main>
  );
}