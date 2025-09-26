import { Link } from "react-router-dom";
import { FaHome, FaExclamationTriangle, FaArrowLeft, FaGithub } from "react-icons/fa";

const NotFoundPage = () => {
  return (
    <div className="min-h-[60vh] bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4 pt-24">
      <div className="text-center max-w-2xl mx-auto">
        {/* 404 Icon */}
        <div className="mb-8 relative">
          <div className="w-32 h-32 mx-auto bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900 dark:to-purple-900 rounded-full flex items-center justify-center">
            <FaExclamationTriangle className="text-5xl text-blue-500 dark:text-blue-400" />
          </div>
        </div>

        {/* Error Code */}
        <h1 className="text-8xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-purple-500 dark:from-blue-400 dark:to-purple-400 mb-4">
          404
        </h1>

        {/* Error Message */}
        <h2 className="text-3xl font-light text-gray-900 dark:text-white mb-4">
          Page Not Found
        </h2>

        <p className="text-lg text-gray-600 dark:text-gray-300 mb-8 font-light">
          Oops! The page you're looking for doesn't exist. It might have been moved or deleted.
        </p>

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
            onClick={() => window.history.back()}
            className="inline-flex items-center gap-3 px-6 py-3 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-medium rounded-2xl transition-all duration-200 hover:scale-[1.02] shadow-lg"
          >
            <FaArrowLeft className="text-lg" />
            Go Back
          </button>
        </div>

        {/* Helpful Links */}
        <div className="mt-12 pt-8 border-t border-gray-200 dark:border-gray-700">
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
            Here are some helpful links instead:
          </p>
          <div className="flex flex-wrap gap-4 justify-center">
            <Link
              to="/about"
              className="text-blue-500 hover:text-blue-600 dark:text-blue-400 dark:hover:text-blue-300 underline font-light"
            >
              About
            </Link>
            <Link
              to="/profile"
              className="text-blue-500 hover:text-blue-600 dark:text-blue-400 dark:hover:text-blue-300 underline font-light"
            >
              Profile
            </Link>
            <Link
              to="/login"
              className="text-blue-500 hover:text-blue-600 dark:text-blue-400 dark:hover:text-blue-300 underline font-light"
            >
              Login
            </Link>
            <Link
              to="/signup"
              className="text-blue-500 hover:text-blue-600 dark:text-blue-400 dark:hover:text-blue-300 underline font-light"
            >
              Sign Up
            </Link>
          </div>
        </div>

        {/* Contribute Section */}
        <div className="mt-8 pt-8 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-center gap-2 mb-3">
            <FaGithub className="text-xl text-gray-600 dark:text-gray-400" />
            <p className="text-base font-medium text-gray-700 dark:text-gray-300">
              Do you think this page should exist?
            </p>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Create an issue at{' '}
            <a
              href="https://github.com/ibrahim-sisar/EduLite/issues"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-500 hover:text-blue-600 dark:text-blue-400 dark:hover:text-blue-300 underline font-medium"
            >
              github.com/ibrahim-sisar/EduLite/issues
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default NotFoundPage;
