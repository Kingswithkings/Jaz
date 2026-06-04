"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import Link from "next/link";
import { getChildId } from "@/lib/storage";

type SocialPost = {
  id: number;
  child_id: number;
  title: string;
  content: string;
  media_url: string | null;
  category: string;
  status: string;
  stars_received: number;
};

const badges = [
  "Wisdom Star",
  "Kind Work",
  "Creative Mind",
  "Great Idea",
  "Good Learner",
];

export default function ChildSocialPage() {
  const [posts, setPosts] = useState<SocialPost[]>([]);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [category, setCategory] = useState("creative");

  useEffect(() => {
    async function loadFeed() {
      const childId = getChildId();

      if (!childId) {
        setPosts([]);
        return;
      }

      try {
        const res = await api.get(`/social/feed/${childId}`);
        setPosts(res.data.safe_social_feed || []);
      } catch (error) {
        console.error(error);
      }
    }

    loadFeed();
  }, []);

  async function refreshFeed() {
    const childId = getChildId();

    if (!childId) {
      setPosts([]);
      return;
    }

    try {
      const res = await api.get(`/social/feed/${childId}`);
      setPosts(res.data.safe_social_feed || []);
    } catch (error) {
      console.error(error);
    }
  }

  async function createPost() {
    if (!title.trim() || !content.trim()) {
      alert("Please add a title and something to share.");
      return;
    }

    const childId = getChildId();

    if (!childId) {
      alert("No child profile found. Please create a child profile first.");
      return;
    }

    try {
      const res = await api.post("/social/", {
        child_id: Number(childId),
        title,
        content,
        media_url: null,
        category,
      });

      if (res.data.status === "blocked") {
        alert("JAZ blocked this post because it may not be safe.");
      } else {
        alert("Post shared safely. You earned Wisdom Stars ⭐");
      }

      setTitle("");
      setContent("");
      refreshFeed();
    } catch (error) {
      console.error(error);
      alert("Could not share post.");
    }
  }

  async function giveBadge(postId: number, badge: string) {
    try {
      await api.post(`/social/${postId}/badge`, {
        badge,
      });

      alert(`You gave a ${badge} badge.`);
      refreshFeed();
    } catch (error) {
      console.error(error);
      alert("Could not give badge.");
    }
  }

  return (
    <main className="min-h-screen bg-yellow-50">
      <header className="bg-white shadow px-6 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-purple-700">
            JAZ Social Feed
          </h1>
          <p className="text-sm text-gray-500">
            Share creative work safely and encourage others.
          </p>
        </div>

        <Link href="/child/dashboard" className="text-purple-700 font-semibold">
          Back
        </Link>
      </header>

      <section className="max-w-3xl mx-auto p-6">
        <div className="bg-white rounded-2xl shadow p-6 mb-6">
          <h2 className="text-xl font-bold text-purple-700 mb-4">
            Share Something You Created
          </h2>

          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Title of your work"
            className="w-full border rounded-xl px-4 py-3 mb-3 outline-none focus:ring-2 focus:ring-purple-500"
          />

          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="w-full border rounded-xl px-4 py-3 mb-3 outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="creative">Creative</option>
            <option value="school_project">School Project</option>
            <option value="story">Story</option>
            <option value="poem">Poem</option>
            <option value="drawing">Drawing</option>
            <option value="bible_reflection">Bible Reflection</option>
          </select>

          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Write your story, poem, project, or idea..."
            rows={5}
            className="w-full border rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-purple-500"
          />

          <button
            onClick={createPost}
            className="mt-4 bg-purple-700 text-white px-6 py-3 rounded-xl font-semibold"
          >
            Share Safely
          </button>
        </div>

        <div className="space-y-6">
          {posts.length === 0 && (
            <div className="bg-white rounded-2xl shadow p-6 text-center">
              <p className="text-gray-600">
                No social posts yet. Share something creative first.
              </p>
            </div>
          )}

          {posts.map((post) => (
            <article
              key={post.id}
              className="bg-white rounded-2xl shadow overflow-hidden"
            >
              <div className="h-44 bg-gradient-to-br from-yellow-200 to-purple-200 flex items-center justify-center">
                <span className="text-5xl">🎨</span>
              </div>

              <div className="p-6">
                <div className="flex justify-between items-center mb-3">
                  <span className="bg-purple-100 text-purple-700 px-3 py-1 rounded-full text-sm">
                    {post.category}
                  </span>

                  <span className="text-yellow-600 font-semibold">
                    {post.stars_received} ⭐
                  </span>
                </div>

                <h2 className="text-2xl font-bold text-gray-800 mb-3">
                  {post.title}
                </h2>

                <p className="text-gray-600 whitespace-pre-wrap mb-5">
                  {post.content}
                </p>

                <div className="flex flex-wrap gap-2">
                  {badges.map((badge) => (
                    <button
                      key={badge}
                      onClick={() => giveBadge(post.id, badge)}
                      className="bg-yellow-100 text-yellow-800 px-3 py-2 rounded-full text-xs font-semibold"
                    >
                      {badge}
                    </button>
                  ))}
                </div>
              </div>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
