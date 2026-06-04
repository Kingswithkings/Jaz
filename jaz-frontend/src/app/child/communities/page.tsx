"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import Link from "next/link";
import { getChildId } from "@/lib/storage";

type Community = {
  id: number;
  name: string;
  description: string;
  category: string;
  age_min: number;
  age_max: number;
};

type CommunityPost = {
  id: number;
  community_id: number;
  child_id: number;
  content: string;
  status: string;
};

export default function CommunitiesPage() {
  const [communities, setCommunities] = useState<Community[]>([]);
  const [selectedCommunity, setSelectedCommunity] = useState<Community | null>(null);
  const [posts, setPosts] = useState<CommunityPost[]>([]);
  const [message, setMessage] = useState("");

  useEffect(() => {
    async function loadCommunities() {
      try {
        const res = await api.get("/communities/");
        setCommunities(res.data);
      } catch (error) {
        console.error(error);
      }
    }

    loadCommunities();
  }, []);

  async function joinCommunity(communityId: number) {
    const childId = getChildId();

    if (!childId) {
      alert("No child profile found. Please create a child profile first.");
      return;
    }

    try {
      const res = await api.post(`/communities/${communityId}/join`, {
        child_id: Number(childId),
      });

      alert(res.data.message);
    } catch (error) {
      console.error(error);
      alert("Could not join community.");
    }
  }

  async function openCommunity(community: Community) {
    setSelectedCommunity(community);

    try {
      const res = await api.get(`/communities/${community.id}/posts`);
      setPosts(res.data.posts);
    } catch (error) {
      console.error(error);
    }
  }

  async function createPost() {
    if (!selectedCommunity) return;

    if (!message.trim()) {
      alert("Please write something kind or educational.");
      return;
    }

    const childId = getChildId();

    if (!childId) {
      alert("No child profile found. Please create a child profile first.");
      return;
    }

    try {
      const res = await api.post(`/communities/${selectedCommunity.id}/posts`, {
        child_id: Number(childId),
        content: message,
      });

      if (res.data.status === "blocked") {
        alert("JAZ blocked this message because it may not be safe.");
      } else {
        alert("Post shared safely.");
      }

      setMessage("");
      openCommunity(selectedCommunity);
    } catch (error) {
      console.error(error);
      alert("Could not create post. Make sure you have joined the community.");
    }
  }

  return (
    <main className="min-h-screen bg-purple-50">
      <header className="bg-white shadow px-6 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-purple-700">
            JAZ Communities
          </h1>
          <p className="text-sm text-gray-500">
            Join safe learning groups and grow with other children.
          </p>
        </div>

        <Link href="/child/dashboard" className="text-purple-700 font-semibold">
          Back
        </Link>
      </header>

      <section className="max-w-6xl mx-auto p-6 grid md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-gray-800">
            Safe Communities
          </h2>

          {communities.length === 0 && (
            <div className="bg-white rounded-2xl shadow p-6">
              <p className="text-gray-600">
                No communities yet. Create communities from Swagger first.
              </p>
            </div>
          )}

          {communities.map((community) => (
            <div
              key={community.id}
              className="bg-white rounded-2xl shadow p-5"
            >
              <h3 className="text-lg font-bold text-purple-700">
                {community.name}
              </h3>

              <p className="text-gray-600 text-sm mt-1">
                {community.description}
              </p>

              <p className="text-xs text-gray-500 mt-2">
                Ages {community.age_min}–{community.age_max} • {community.category}
              </p>

              <div className="flex gap-3 mt-4">
                <button
                  onClick={() => joinCommunity(community.id)}
                  className="bg-yellow-400 text-gray-900 px-4 py-2 rounded-xl text-sm font-semibold"
                >
                  Join
                </button>

                <button
                  onClick={() => openCommunity(community)}
                  className="bg-purple-700 text-white px-4 py-2 rounded-xl text-sm font-semibold"
                >
                  Open
                </button>
              </div>
            </div>
          ))}
        </div>

        <div>
          {!selectedCommunity ? (
            <div className="bg-white rounded-2xl shadow p-6">
              <p className="text-gray-600">
                Select a community to view safe posts.
              </p>
            </div>
          ) : (
            <div className="bg-white rounded-2xl shadow p-6">
              <h2 className="text-xl font-bold text-purple-700">
                {selectedCommunity.name}
              </h2>

              <p className="text-gray-600 text-sm mb-5">
                {selectedCommunity.description}
              </p>

              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Share something kind, creative, or educational..."
                rows={4}
                className="w-full border rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-purple-500"
              />

              <button
                onClick={createPost}
                className="mt-3 bg-purple-700 text-white px-5 py-3 rounded-xl font-semibold"
              >
                Share Safely
              </button>

              <div className="mt-6 space-y-4">
                {posts.length === 0 && (
                  <p className="text-gray-500 text-sm">
                    No posts in this community yet.
                  </p>
                )}

                {posts.map((post) => (
                  <div
                    key={post.id}
                    className="bg-purple-50 rounded-xl p-4"
                  >
                    <p className="text-gray-700">{post.content}</p>
                    <p className="text-xs text-gray-500 mt-2">
                      Status: {post.status}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </section>
    </main>
  );
}
