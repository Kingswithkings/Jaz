import Link from "next/link";
import {
  MessageCircle,
  BookOpen,
  Palette,
  GraduationCap,
  Brain,
  Users,
  Image,
  User,
  Target,
  Route,
} from "lucide-react";
import AuthGuard from "@/components/AuthGuard";
import LogoutButton from "@/components/LogoutButton";

const items = [
  {
    title: "Talk to JAZ",
    href: "/child/chat",
    icon: MessageCircle,
  },
  {
    title: "Learning Feed",
    href: "/child/feed",
    icon: BookOpen,
  },
  {
    title: "Creativity Studio",
    href: "/child/creativity",
    icon: Palette,
  },
  {
    title: "Homework Helper",
    href: "/child/homework",
    icon: GraduationCap,
  },
  {
    title: "Quiz Time",
    href: "/child/quiz",
    icon: Brain,
  },
  {
    title: "Communities",
    href: "/child/communities",
    icon: Users,
  },
  {
    title: "Social Feed",
    href: "/child/social",
    icon: Image,
  },
  {
    title: "My Profile",
    href: "/child/profile",
    icon: User,
  },
  {
    title: "Learning Goals",
    href: "/child/goals",
    icon: Target,
  },
  {
    title: "AI Learning Path",
    href: "/child/learning-path",
    icon: Route,
  },
];

export default function ChildDashboard() {
  return (
    <AuthGuard>
      <main className="min-h-screen bg-purple-50 p-6">
        <section className="max-w-6xl mx-auto">
          <div className="flex justify-between gap-4 items-start mb-8">
            <div>
              <h1 className="text-3xl font-bold text-purple-700 mb-2">
                Welcome to JAZ
              </h1>

              <p className="text-gray-600">
                Learn, create, collaborate, and grow safely.
              </p>
            </div>

            <LogoutButton />
          </div>

        <div className="grid md:grid-cols-3 gap-6">
          {items.map((item) => {
            const Icon = item.icon;

            return (
              <Link
                key={item.title}
                href={item.href}
                className="bg-white rounded-2xl shadow p-6 hover:shadow-lg transition"
              >
                <Icon className="w-10 h-10 text-purple-700 mb-4" />
                <h2 className="text-xl font-semibold">{item.title}</h2>
              </Link>
            );
          })}
        </div>
        </section>
      </main>
    </AuthGuard>
  );
}
