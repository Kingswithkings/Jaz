"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { getParentId, getChildId, setChildId } from "@/lib/storage";

type Child = {
  id: number;
  name: string;
  age: number;
  level: string;
  rating: number;
  wisdom_stars: number;
};

export default function ChildSelector() {
  const [children, setChildren] = useState<Child[]>([]);
  const [selectedChildId, setSelectedChildId] = useState("");

  useEffect(() => {
    const parentId = getParentId();

    if (!parentId) return;

    api
      .get(`/children/${parentId}`)
      .then((res) => {
        setChildren(res.data);

        const storedChildId = getChildId();

        if (storedChildId) {
          setSelectedChildId(storedChildId);
        } else if (res.data.length > 0) {
          setChildId(res.data[0].id);
          setSelectedChildId(String(res.data[0].id));
        }
      })
      .catch((err) => console.error(err));
  }, []);

  function handleChange(value: string) {
    setSelectedChildId(value);
    setChildId(value);
    window.location.reload();
  }

  return (
    <div className="bg-white rounded-xl shadow p-4 mb-6">
      <label className="block text-sm font-semibold mb-2">Select Child</label>

      <select
        value={selectedChildId}
        onChange={(e) => handleChange(e.target.value)}
        className="w-full border rounded-xl px-4 py-3"
      >
        {children.map((child) => (
          <option key={child.id} value={child.id}>
            {child.name} - Age {child.age}
          </option>
        ))}
      </select>
    </div>
  );
}
