"use client";

import { useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { getChildId } from "@/lib/storage";

type ChatMessage = {
  role: "child" | "jaz";
  text: string;
};

export default function ChildChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "jaz",
      text: "Hi! I am JAZ. What would you like to learn, create, or talk about today?",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function sendMessage() {
    if (!input.trim()) return;

    const childId = getChildId();

    if (!childId) {
      alert("No child profile found. Please create a child profile first.");
      return;
    }

    const childMessage: ChatMessage = {
      role: "child",
      text: input,
    };

    setMessages((prev) => [...prev, childMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await api.post("/ai/chat", {
        child_id: Number(childId),
        message: input,
      });

      const jazMessage: ChatMessage = {
        role: "jaz",
        text: res.data.response,
      };

      setMessages((prev) => [...prev, jazMessage]);
    } catch (error) {
      console.error(error);

      setMessages((prev) => [
        ...prev,
        {
          role: "jaz",
          text: "Sorry, I could not reply right now. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-purple-50 flex flex-col">
      <header className="bg-white shadow px-6 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-purple-700">Talk to JAZ</h1>
          <p className="text-sm text-gray-500">Your safe learning companion</p>
        </div>

        <Link href="/child/dashboard" className="text-purple-700 font-semibold">
          Back
        </Link>
      </header>

      <section className="flex-1 max-w-4xl w-full mx-auto p-6 overflow-y-auto">
        <div className="space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${
                message.role === "child" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[75%] rounded-2xl px-5 py-3 shadow ${
                  message.role === "child"
                    ? "bg-purple-700 text-white"
                    : "bg-white text-gray-800"
                }`}
              >
                <p>{message.text}</p>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-white text-gray-500 rounded-2xl px-5 py-3 shadow">
                JAZ is thinking...
              </div>
            </div>
          )}
        </div>
      </section>

      <footer className="bg-white border-t p-4">
        <div className="max-w-4xl mx-auto flex gap-3">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") sendMessage();
            }}
            placeholder="Ask JAZ something..."
            className="flex-1 border rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-purple-500"
          />

          <button
            onClick={sendMessage}
            disabled={loading}
            className="bg-purple-700 text-white px-6 py-3 rounded-xl font-semibold disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </footer>
    </main>
  );
}
