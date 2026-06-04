"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function RegisterPage() {
  const router = useRouter();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function register() {
    const res = await api.post("/auth/register", {
      full_name: fullName,
      email,
      password,
    });

    localStorage.setItem("jaz_token", res.data.token);
    localStorage.setItem("jaz_parent_id", String(res.data.parent_id));

    router.push("/child/create");
  }

  return (
    <main className="min-h-screen bg-purple-50 flex items-center justify-center p-6">
      <div className="bg-white rounded-2xl shadow p-8 w-full max-w-md">
        <h1 className="text-3xl font-bold text-purple-700 mb-2">
          Create Parent Account
        </h1>

        <p className="text-gray-600 mb-6">
          Register to create and monitor your child profile.
        </p>

        <input
          placeholder="Full name"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          className="w-full border rounded-xl px-4 py-3 mb-3"
        />

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
          onClick={register}
          className="w-full bg-purple-700 text-white py-3 rounded-xl font-semibold"
        >
          Register
        </button>

        <p className="text-sm text-gray-600 mt-4">
          Already have an account?{" "}
          <Link href="/auth/login" className="text-purple-700 font-semibold">
            Login
          </Link>
        </p>
      </div>
    </main>
  );
}