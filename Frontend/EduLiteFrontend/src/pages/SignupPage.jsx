import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import toast from "react-hot-toast";
import Input from "../components/common/Input";
import { useAuth } from "../contexts/AuthContext";

const SignUpPage = () => {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    password2: "",
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));

    // Clear specific field error when user starts typing
    if (errors[e.target.name]) {
      setErrors((prev) => ({
        ...prev,
        [e.target.name]: "",
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.username.trim()) {
      newErrors.username = "Username is required";
    }

    if (!formData.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Please enter a valid email address";
    }

    if (!formData.password) {
      newErrors.password = "Password is required";
    } else if (formData.password.length < 8) {
      newErrors.password = "Password must be at least 8 characters long";
    }

    if (!formData.password2) {
      newErrors.password2 = "Please confirm your password";
    } else if (formData.password !== formData.password2) {
      newErrors.password2 = "Passwords do not match";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      toast.error("Please fix the errors below");
      return;
    }

    setLoading(true);

    try {
      // Register the user
      const registerResponse = await axios.post(
        "http://localhost:8000/api/register/",
        formData,
        {
          headers: {
            "Content-Type": "application/json",
          },
          timeout: 10000,
        }
      );

      if (process.env.NODE_ENV !== "production") {
        console.log("Registration successful");
      }

      toast.success("Account created successfully! 🎉");

      // Automatically log in the user after successful registration
      try {
        const loginResponse = await axios.post(
          "http://localhost:8000/api/token/",
          {
            username: formData.username,
            password: formData.password,
          },
          {
            headers: {
              "Content-Type": "application/json",
            },
            timeout: 10000,
          }
        );

        const { access, refresh } = loginResponse.data;
        login(access, refresh);

        toast.success("Welcome to EduLite! 🚀");
        navigate("/");
      } catch (loginErr) {
        // If auto-login fails, redirect to login page
        toast.success("Please log in with your new account");
        navigate("/login");
      }
    } catch (err) {
      if (process.env.NODE_ENV !== "production") {
        console.error(
          "Registration failed - Status:",
          err.response?.status || "Network Error"
        );
      }

      if (err.response?.data) {
        const backendErrors = err.response.data;
        const newErrors = {};

        // Map backend errors to form fields
        if (backendErrors.username) {
          newErrors.username = Array.isArray(backendErrors.username)
            ? backendErrors.username[0]
            : backendErrors.username;
        }
        if (backendErrors.email) {
          newErrors.email = Array.isArray(backendErrors.email)
            ? backendErrors.email[0]
            : backendErrors.email;
        }
        if (backendErrors.password) {
          newErrors.password = Array.isArray(backendErrors.password)
            ? backendErrors.password[0]
            : backendErrors.password;
        }
        if (backendErrors.non_field_errors) {
          newErrors.password2 = Array.isArray(backendErrors.non_field_errors)
            ? backendErrors.non_field_errors[0]
            : backendErrors.non_field_errors;
        }

        setErrors(newErrors);
        toast.error("Please fix the errors below");
      } else if (err.code === "ECONNABORTED") {
        toast.error("Request timeout. Is your backend running?");
      } else if (!err.response) {
        toast.error(
          "Cannot connect to server. Is your backend running on port 8000?"
        );
      } else {
        toast.error("Registration failed. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4 pt-24">
      <div className="w-full max-w-md">
        {/* Glass-morphism container */}
        <div className="bg-white/80 dark:bg-gray-800/40 backdrop-blur-xl border border-gray-200/50 dark:border-gray-700/30 rounded-3xl shadow-2xl shadow-gray-200/20 dark:shadow-gray-900/20 p-8">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-light text-gray-900 dark:text-white mb-2 tracking-tight">
              Join EduLite
            </h2>
            <p className="text-gray-500 dark:text-gray-400 font-light">
              Create your account to start learning
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-2">
            <Input
              label="Username"
              type="text"
              name="username"
              placeholder="Choose a username"
              value={formData.username}
              onChange={handleChange}
              required
              disabled={loading}
              error={errors.username}
              compact={true}
            />

            <Input
              label="Email"
              type="email"
              name="email"
              placeholder="Enter your email"
              value={formData.email}
              onChange={handleChange}
              required
              disabled={loading}
              error={errors.email}
              compact={true}
            />

            <Input
              label="Password"
              type="password"
              name="password"
              placeholder="Create a password (min. 8 characters)"
              value={formData.password}
              onChange={handleChange}
              required
              disabled={loading}
              error={errors.password}
              compact={true}
            />

            <Input
              label="Confirm Password"
              type="password"
              name="password2"
              placeholder="Confirm your password"
              value={formData.password2}
              onChange={handleChange}
              required
              disabled={loading}
              error={errors.password2}
              compact={true}
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
                  transition-all duration-300 ease-out

                  focus:outline-none
                  focus:ring-2 focus:ring-blue-500/50 dark:focus:ring-blue-400/50
                  focus:scale-[1.02]

                  hover:scale-[1.02]

                  ${loading ? "opacity-60 cursor-not-allowed" : ""}
                `}
              >
                {loading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                    Creating Account...
                  </div>
                ) : (
                  "Create Account"
                )}
              </button>
            </div>
          </form>

          {/* Login Link */}
          <div className="mt-8 pt-6 border-t border-gray-200/50 dark:border-gray-700/30 text-center">
            <p className="text-gray-600 dark:text-gray-400 font-light">
              Already have an account?{" "}
              <Link
                to="/login"
                className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium transition-colors duration-200 hover:underline"
              >
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignUpPage;
