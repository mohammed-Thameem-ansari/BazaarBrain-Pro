import Image from "next/image";

export default function HomePage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-6 bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="text-center max-w-2xl">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to BazaarBrain
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          AI-powered business assistant for shopkeepers using GPT + Gemini
        </p>
        <div className="space-y-4">
          <a
            href="/login"
            className="inline-block bg-blue-600 text-white px-8 py-3 rounded-xl font-semibold hover:bg-blue-700 transition-colors"
          >
            Get Started
          </a>
          <p className="text-sm text-gray-500">
            Upload receipts, run simulations, and get business insights
          </p>
        </div>
      </div>
    </main>
  );
}
