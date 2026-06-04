"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { getChildId } from "@/lib/storage";

type LearningPost = {
  id: number;
  title: string;
  content: string;
  category: string;
  stars_reward: number;
};

export default function LearningFeedPage() {
  const [posts, setPosts] = useState<LearningPost[]>([]);

  useEffect(() => {
    async function loadFeed() {
      const childId = getChildId();

      if (!childId) {
        setPosts([]);
        return;
      }

      try {
        const res = await api.get(`/feed/${childId}`);
        setPosts(res.data.feed || []);
      } catch (error) {
        console.error(error);
      }
    }

    loadFeed();
  }, []);

  async function completePost(postId: number) {
    const childId = getChildId();

    if (!childId) {
      alert("No child profile found. Please create a child profile first.");
      return;
    }

    try {
      const res = await api.post(`/feed/${childId}/complete/${postId}`);
      alert(`Learning completed. You earned ${res.data.stars_earned} Wisdom Stars.`);
    } catch (error) {
      console.error(error);
      alert("Could not complete this learning post.");
    }
  }

  return (
    <main className="min-h-screen bg-green-50">
      <header className="bg-white shadow px-6 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-purple-700">Learning Feed</h1>
          <p className="text-sm text-gray-500">
            Explore learning activities matched to your age.
          </p>
        </div>

        <Link href="/child/dashboard" className="text-purple-700 font-semibold">
          Back
        </Link>
      </header>

      <section className="max-w-4xl mx-auto p-6 space-y-4">
        {posts.length === 0 && (
          <div className="bg-white rounded-2xl shadow p-6 text-center">
            <p className="text-gray-600">No learning posts available yet.</p>
          </div>
        )}

        {posts.map((post) => (
          <article key={post.id} className="bg-white rounded-2xl shadow p-6">
            <p className="text-sm text-purple-700 font-semibold mb-2">
              {post.category}
            </p>
            <h2 className="text-2xl font-bold text-gray-800 mb-3">
              {post.title}
            </h2>
            <p className="text-gray-600 whitespace-pre-wrap mb-5">
              {post.content}
            </p>
            <button
              onClick={() => completePost(post.id)}
              className="bg-purple-700 text-white px-5 py-3 rounded-xl font-semibold"
            >
              Complete for {post.stars_reward} Stars
            </button>
          </article>
        ))}
      </section>
    </main>
  );
}
