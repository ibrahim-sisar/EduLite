import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import toast from "react-hot-toast";
import Input from "../components/common/Input";
import { Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext"; // Import auth context

const LoginPage = () => {
  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth(); // Get login function from context

  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setLoading(true);

    try {
      const response = await axios.post(
        "http://localhost:8000/api/token/",
        formData,
        {
          headers: {
            "Content-Type": "application/json",
          },
          timeout: 10000,
        }
      );

      const { access, refresh } = response.data;

      // Use the context login function
      login(access, refresh);

      toast.success("Login successful 🎉");
      navigate("/");
    } catch (err) {
      // Only log non-sensitive error information
      console.error(
        "Login failed - Status:",
        err.response?.status || "Network Error"
      );

      if (err.code === "ECONNABORTED") {
        setError("Request timeout. Is your backend running?");
      } else if (err.response?.status === 401) {
        setError("Invalid credentials. Please try again.");
      } else if (err.response?.status === 400) {
        setError("Bad request. Please check your input.");
      } else if (!err.response) {
        setError(
          "Cannot connect to server. Is your backend running on port 8000?"
        );
      } else {
        setError(`Login failed: ${err.response?.data?.detail || err.message}`);
      }

      toast.error("Login failed!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4 pt-24">
      <div className="w-full max-w-md">
        {/* Glass-morphism container matching your Input design */}
        <div className="bg-white/80 dark:bg-gray-800/40 backdrop-blur-xl border border-gray-200/50 dark:border-gray-700/30 rounded-3xl shadow-2xl shadow-gray-200/20 dark:shadow-gray-900/20 p-8">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-light text-gray-900 dark:text-white mb-2 tracking-tight">
              Welcome Back
            </h2>
            <p className="text-gray-500 dark:text-gray-400 font-light">
              Sign in to your account
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-2">
            <Input
              label="Username"
              type="text"
              name="username"
              placeholder="Enter your username"
              value={formData.username}
              onChange={handleChange}
              required
              disabled={loading}
            />

            <Input
              label="Password"
              type="password"
              name="password"
              placeholder="Enter your password"
              value={formData.password}
              onChange={handleChange}
              required
              disabled={loading}
              error={error} // Show error on password field
            />

            <div className="pt-4">
              <button
                type="submit"
                disabled={loading}
                className={`
                  w-full px-6 py-4 text-lg font-light
                  bg-blue-500/90 hover:bg-blue-600/90 dark:bg-blue-600/90 dark:hover:bg-blue-700/90
                  text-white
                  backdrop-blur-xl
                  border border-blue-500/20 dark:border-blue-600/20
                  rounded-2xl
                  shadow-lg shadow-blue-500/20 dark:shadow-blue-600/20
                  transition-all duration-300 ease-out

                  focus:outline-none
                  focus:ring-2 focus:ring-blue-500/50 dark:focus:ring-blue-400/50
                  focus:shadow-xl focus:shadow-blue-500/30 dark:focus:shadow-blue-400/30
                  focus:scale-[1.02]

                  hover:shadow-xl hover:shadow-blue-500/30 dark:hover:shadow-blue-600/30
                  hover:scale-[1.02]

                  ${loading ? "opacity-60 cursor-not-allowed" : ""}
                `}
              >
                {loading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                    Signing In...
                  </div>
                ) : (
                  "Sign In"
                )}
              </button>
            </div>
          </form>

          {/* Sign Up Link */}
          <div className="mt-6 text-center">
            <p className="text-gray-600 dark:text-gray-400 font-light">
              Don't have an account?{" "}
              <Link
                to="/signup"
                className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium transition-colors duration-200"
              >
                Sign up
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
