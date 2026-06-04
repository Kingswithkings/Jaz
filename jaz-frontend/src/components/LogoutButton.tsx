"use client";

import { useRouter } from "next/navigation";
import { logout } from "@/lib/storage";

export default function LogoutButton() {
  const router = useRouter();

  function handleLogout() {
    logout();
    router.push("/auth/login");
  }

  return (
    <button
      onClick={handleLogout}
      className="bg-red-500 text-white px-4 py-2 rounded-xl font-semibold"
    >
      Logout
    </button>
  );
}