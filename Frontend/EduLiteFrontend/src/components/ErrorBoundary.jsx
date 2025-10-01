import { useRouteError, Link } from "react-router-dom";
import { FaExclamationCircle, FaHome, FaRedo } from "react-icons/fa";
import Navbar from "./Navbar";
import Footer from "./Footer";
import { useAuth } from "../hooks/useAuth";

const ErrorBoundary = () => {
  const error = useRouteError();
  const { isLoggedIn, logout } = useAuth();

  // Check if it's a 404 error
  const is404 = error?.status === 404;

  return (
    <div className="flex flex-col min-h-screen">
      {/* Keep the navbar visible */}
      <Navbar isLoggedIn={isLoggedIn} onLogout={logout} />

      <main className="flex-grow flex items-center justify-center p-4 bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <div className="text-center max-w-2xl mx-auto">
          {/* Error Icon */}
          <div className="mb-8">
            <div className="w-32 h-32 mx-auto bg-gradient-to-br from-red-100 to-orange-100 dark:from-red-900 dark:to-orange-900 rounded-full flex items-center justify-center">
              <FaExclamationCircle className="text-5xl text-red-500 dark:text-red-400" />
            </div>
          </div>

          {/* Error Title */}
          <h1 className="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-orange-500 dark:from-red-400 dark:to-orange-400 mb-4">
            {is404 ? "404" : "Oops!"}
          </h1>

          {/* Error Message */}
          <h2 className="text-3xl font-light text-gray-900 dark:text-white mb-4">
            {is404 ? "Page Not Found" : "Something went wrong"}
          </h2>

          <p className="text-lg text-gray-600 dark:text-gray-300 mb-6 font-light">
            {is404
              ? "The page you're looking for doesn't exist."
              : error?.message || "An unexpected error occurred. Please try again."}
          </p>

          {/* Error Details (in development) */}
          {!is404 && error?.stack && import.meta.env.MODE === 'development' && (
            <details className="mb-6 text-left">
              <summary className="cursor-pointer text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
                Technical details
              </summary>
              <pre className="mt-2 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg text-xs overflow-x-auto text-gray-700 dark:text-gray-300">
                {error.stack}
              </pre>
            </details>
          )}

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/"
              className="inline-flex items-center gap-3 px-6 py-3 bg-blue-500 hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 text-white font-medium rounded-2xl transition-all duration-200 hover:scale-[1.02] shadow-lg"
            >
              <FaHome className="text-lg" />
              Go to Home
            </Link>

            <button
              onClick={() => window.location.reload()}
              className="inline-flex items-center gap-3 px-6 py-3 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-medium rounded-2xl transition-all duration-200 hover:scale-[1.02] shadow-lg"
            >
              <FaRedo className="text-lg" />
              Try Again
            </button>
          </div>
        </div>
      </main>

      {/* Keep the footer visible */}
      <Footer />
    </div>
  );
};

export default ErrorBoundary;
