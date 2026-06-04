import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-yellow-50 via-white to-purple-50 flex items-center justify-center px-6">
      <section className="max-w-4xl text-center">
        <h1 className="text-5xl font-bold text-purple-700 mb-4">JAZ</h1>

        <p className="text-xl text-gray-700 mb-2">
          Building Joyful and Wise Generations
        </p>

        <p className="text-gray-600 mb-8">
          A safe AI-powered learning, creativity, and child-care platform for
          children and parents.
        </p>

        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <Link
            href="/auth/register"
            className="bg-purple-700 text-white px-6 py-3 rounded-xl font-semibold"
          >
            Get Started
          </Link>

          <Link
            href="/auth/login"
            className="bg-yellow-400 text-gray-900 px-6 py-3 rounded-xl font-semibold"
          >
            Parent Login
          </Link>
        </div>
      </section>
    </main>
  );
}
