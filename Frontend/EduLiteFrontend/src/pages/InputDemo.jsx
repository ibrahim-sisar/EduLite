import React, { useState } from "react";
import { Link } from "react-router-dom";
import Input from "../components/common/Input";
import {
  FaCode,
  FaEye,
  FaShieldAlt,
  FaCheckCircle,
  FaBook,
  FaExternalLinkAlt,
  FaRocket,
} from "react-icons/fa";

const InputDemo = () => {
  // Separate state for each input
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [phone, setPhone] = useState("");
  const [emailError, setEmailError] = useState("");
  const [phoneError, setPhoneError] = useState("");

  const handleEmailChange = (e) => {
    const value = e.target.value;
    setEmail(value);
    setEmailError(
      value && !value.includes("@") ? "Please enter a valid email address" : ""
    );
  };

  const handlePhoneChange = (e) => {
    const value = e.target.value;
    setPhone(value);
    // Basic phone validation - you can customize this
    const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
    setPhoneError(
      value && !phoneRegex.test(value.replace(/\D/g, ""))
        ? "Please enter a valid phone number"
        : ""
    );
  };

  return (
    <div className="text-gray-800 dark:text-gray-100 bg-white dark:bg-gray-900 min-h-screen">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center px-4 sm:px-6 md:px-16 overflow-hidden pt-20">
        {/* Background Elements */}
        <div className="absolute inset-0 overflow-hidden">
          {/* Gradient Orbs */}
          <div className="absolute top-1/4 -left-40 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
          <div
            className="absolute bottom-1/4 -right-40 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse"
            style={{ animationDelay: "2s" }}
          ></div>
        </div>

        <div className="max-w-4xl mx-auto w-full relative z-10">
          <div className="text-center mb-16">
            {/* Icon */}
            <div className="mb-8">
              <div className="inline-flex items-center justify-center w-20 h-20 md:w-24 md:h-24 rounded-3xl bg-gradient-to-r from-blue-500 to-purple-500 shadow-2xl mt-12 mb-4">
                <FaCode className="text-white text-4xl md:text-5xl" />
              </div>
            </div>

            {/* Main Headline */}
            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-light text-gray-900 dark:text-white mb-6 tracking-tight leading-tight">
              Input Component
            </h1>

            {/* Subtitle */}
            <p className="text-lg sm:text-xl md:text-2xl text-gray-500 dark:text-gray-400 font-light leading-relaxed max-w-3xl mx-auto mb-8">
              A comprehensive showcase of our reusable Input component with all
              its props and states.
            </p>

            {/* Documentation Link - Better positioned */}
            <div className="mb-12">
              <Link
                to="/input-component-doc"
                className="inline-flex items-center gap-3 bg-white/80 dark:bg-black/40 backdrop-blur-xl text-gray-700 dark:text-gray-200 px-6 py-3 rounded-2xl text-base font-medium hover:bg-white/90 dark:hover:bg-black/50 transition-all duration-300 hover:scale-105 border border-gray-200/50 dark:border-gray-700/30 shadow-lg"
              >
                <FaBook className="text-blue-500" />
                View Full Documentation
                <FaExternalLinkAlt className="text-sm opacity-60" />
              </Link>
            </div>
          </div>

          {/* Demo Cards Container */}
          <div className="space-y-8">
            {/* Basic Usage Section */}
            <div className="bg-white/80 dark:bg-black/40 backdrop-blur-xl rounded-3xl p-8 md:p-12 border border-gray-200/50 dark:border-gray-700/30 shadow-lg">
              <div className="flex items-center gap-4 mb-8">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900/30 dark:to-purple-900/30 rounded-2xl flex items-center justify-center">
                  <FaCheckCircle className="text-blue-500 text-xl" />
                </div>
                <h2 className="text-2xl md:text-3xl font-light text-gray-900 dark:text-white">
                  Basic Usage
                </h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-2">
                  <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-4">
                    Username Input
                  </h3>
                  <Input
                    type="text"
                    name="username"
                    label="Username"
                    placeholder="Enter your username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-4">
                    Full Name Input
                  </h3>
                  <Input
                    type="text"
                    name="fullName"
                    label="Full Name"
                    placeholder="John Doe"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                  />
                </div>
              </div>
            </div>

            {/* Input Types Section */}
            <div className="bg-white/80 dark:bg-black/40 backdrop-blur-xl rounded-3xl p-8 md:p-12 border border-gray-200/50 dark:border-gray-700/30 shadow-lg">
              <div className="flex items-center gap-4 mb-8">
                <div className="w-12 h-12 bg-gradient-to-br from-green-100 to-teal-100 dark:from-green-900/30 dark:to-teal-900/30 rounded-2xl flex items-center justify-center">
                  <FaEye className="text-green-500 text-xl" />
                </div>
                <h2 className="text-2xl md:text-3xl font-light text-gray-900 dark:text-white">
                  Different Input Types
                </h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-2">
                  <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-4">
                    Email Input
                  </h3>
                  <Input
                    type="email"
                    name="email"
                    label="Email Address"
                    placeholder="user@example.com"
                    value={email}
                    onChange={handleEmailChange}
                    error={emailError}
                  />
                </div>

                <div className="space-y-2">
                  <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-4">
                    Password Input
                  </h3>
                  <Input
                    type="password"
                    name="password"
                    label="Password"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </div>
              </div>
            </div>

            {/* Special States Section */}
            <div className="bg-white/80 dark:bg-black/40 backdrop-blur-xl rounded-3xl p-8 md:p-12 border border-gray-200/50 dark:border-gray-700/30 shadow-lg">
              <div className="flex items-center gap-4 mb-8">
                <div className="w-12 h-12 bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30 rounded-2xl flex items-center justify-center">
                  <FaShieldAlt className="text-purple-500 text-xl" />
                </div>
                <h2 className="text-2xl md:text-3xl font-light text-gray-900 dark:text-white">
                  Special States
                </h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-2">
                  <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-4">
                    Disabled Input
                  </h3>
                  <Input
                    type="text"
                    name="disabled"
                    label="Disabled Field"
                    placeholder="This field is disabled"
                    value="Cannot edit this field"
                    onChange={() => {}}
                    disabled
                  />
                </div>

                <div className="space-y-2">
                  <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-4">
                    Phone Number
                  </h3>
                  <Input
                    type="tel"
                    name="phone"
                    label="Phone Number"
                    placeholder="(555) 123-4567"
                    value={phone}
                    onChange={handlePhoneChange}
                    error={phoneError}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Documentation Section */}
      <section className="relative px-6 md:px-12 py-16 md:py-24 bg-white dark:bg-gray-800">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <div className="mb-8">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-green-500 to-teal-500 rounded-3xl mb-6 shadow-2xl">
                <FaBook className="text-white text-3xl" />
              </div>
            </div>
            <h2 className="text-4xl sm:text-5xl md:text-6xl font-light text-gray-900 dark:text-white mb-6 tracking-tight">
              Quick Reference
            </h2>
            <p className="text-lg sm:text-xl text-gray-500 dark:text-gray-400 font-light leading-relaxed">
              Essential props and guidelines for the Input component
            </p>
          </div>

          {/* Props Documentation */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-16">
            {/* Required Props */}
            <div className="bg-white/80 dark:bg-black/40 backdrop-blur-xl rounded-3xl p-8 border border-gray-200/50 dark:border-gray-700/30 shadow-lg">
              <h3 className="text-2xl font-light text-gray-900 dark:text-white mb-6">
                Required Props
              </h3>
              <div className="space-y-4">
                <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
                  <code className="text-blue-600 dark:text-blue-400 font-mono text-sm">
                    type
                  </code>
                  <p className="text-gray-600 dark:text-gray-300 text-sm mt-1">
                    Input type: 'text', 'email', 'password', 'tel', etc.
                  </p>
                </div>
                <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
                  <code className="text-blue-600 dark:text-blue-400 font-mono text-sm">
                    name
                  </code>
                  <p className="text-gray-600 dark:text-gray-300 text-sm mt-1">
                    Unique name for the input field
                  </p>
                </div>
                <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
                  <code className="text-blue-600 dark:text-blue-400 font-mono text-sm">
                    value
                  </code>
                  <p className="text-gray-600 dark:text-gray-300 text-sm mt-1">
                    Current input value (controlled component)
                  </p>
                </div>
                <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
                  <code className="text-blue-600 dark:text-blue-400 font-mono text-sm">
                    onChange
                  </code>
                  <p className="text-gray-600 dark:text-gray-300 text-sm mt-1">
                    Function to handle value changes
                  </p>
                </div>
              </div>
            </div>

            {/* Optional Props */}
            <div className="bg-white/80 dark:bg-black/40 backdrop-blur-xl rounded-3xl p-8 border border-gray-200/50 dark:border-gray-700/30 shadow-lg">
              <h3 className="text-2xl font-light text-gray-900 dark:text-white mb-6">
                Optional Props
              </h3>
              <div className="space-y-4">
                <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
                  <code className="text-purple-600 dark:text-purple-400 font-mono text-sm">
                    label
                  </code>
                  <p className="text-gray-600 dark:text-gray-300 text-sm mt-1">
                    Label text displayed above the input
                  </p>
                </div>
                <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
                  <code className="text-purple-600 dark:text-purple-400 font-mono text-sm">
                    placeholder
                  </code>
                  <p className="text-gray-600 dark:text-gray-300 text-sm mt-1">
                    Placeholder text inside the input
                  </p>
                </div>
                <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
                  <code className="text-purple-600 dark:text-purple-400 font-mono text-sm">
                    error
                  </code>
                  <p className="text-gray-600 dark:text-gray-300 text-sm mt-1">
                    Error message to display below input
                  </p>
                </div>
                <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
                  <code className="text-purple-600 dark:text-purple-400 font-mono text-sm">
                    disabled
                  </code>
                  <p className="text-gray-600 dark:text-gray-300 text-sm mt-1">
                    Boolean to disable the input
                  </p>
                </div>
                <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
                  <code className="text-purple-600 dark:text-purple-400 font-mono text-sm">
                    required
                  </code>
                  <p className="text-gray-600 dark:text-gray-300 text-sm mt-1">
                    Boolean to mark field as required
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Usage Guidelines */}
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-3xl p-8 md:p-12 border border-blue-200/50 dark:border-blue-700/30">
            <h3 className="text-3xl font-light text-gray-900 dark:text-white mb-8">
              Usage Guidelines
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <h4 className="text-xl font-medium text-gray-800 dark:text-gray-200 mb-4">
                  ✅ Do's
                </h4>
                <ul className="space-y-3 text-gray-600 dark:text-gray-300">
                  <li>
                    • Always use controlled components with value and onChange
                  </li>
                  <li>• Provide meaningful labels for accessibility</li>
                  <li>• Use appropriate input types (email, tel, password)</li>
                  <li>• Implement proper validation with error messages</li>
                  <li>• Use React.forwardRef for form library compatibility</li>
                </ul>
              </div>
              <div>
                <h4 className="text-xl font-medium text-gray-800 dark:text-gray-200 mb-4">
                  ❌ Don'ts
                </h4>
                <ul className="space-y-3 text-gray-600 dark:text-gray-300">
                  <li>• Don't use without proper state management</li>
                  <li>• Don't forget to handle validation errors</li>
                  <li>• Don't use generic 'text' for specialized inputs</li>
                  <li>• Don't skip accessibility attributes</li>
                  <li>• Don't override core styling without good reason</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Code Example Section */}
      <section className="relative px-6 md:px-12 py-16 md:py-24 bg-gray-50 dark:bg-gray-900">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl sm:text-5xl md:text-6xl font-light text-gray-900 dark:text-white mb-6 tracking-tight">
              Usage Examples
            </h2>
            <p className="text-lg sm:text-xl text-gray-500 dark:text-gray-400 font-light leading-relaxed">
              Copy and use these examples in your forms
            </p>
          </div>

          {/* Code Examples */}
          <div className="bg-gray-900 dark:bg-black rounded-3xl p-8 md:p-12 overflow-hidden shadow-2xl">
            <h3 className="text-xl font-semibold mb-6 text-white">
              Code Examples
            </h3>
            <pre className="text-green-400 text-sm md:text-base overflow-x-auto leading-relaxed">
              {`// Basic usage
<Input
  type="email"
  name="email"
  label="Email Address"
  placeholder="Enter your email"
  value={email}
  onChange={handleEmailChange}
/>

// With validation error
<Input
  type="password"
  name="password"
  label="Password"
  error={passwordError}
  value={password}
  onChange={handlePasswordChange}
/>

// Disabled state
<Input
  label="Read Only Field"
  value="Cannot edit"
  disabled
/>`}
            </pre>
          </div>
        </div>
      </section>

      {/* Bottom CTA Section - Generalized */}
      <section className="relative px-6 md:px-12 py-16 md:py-24">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-3xl p-12 md:p-16 text-white shadow-2xl">
            <div className="mb-6">
              <FaRocket className="text-5xl mx-auto mb-4 opacity-90" />
            </div>
            <h3 className="text-3xl md:text-4xl font-light mb-6">
              Ready to Build Amazing Forms?
            </h3>
            <p className="text-lg md:text-xl mb-8 opacity-90 leading-relaxed max-w-2xl mx-auto">
              Use this versatile Input component in login forms, signup pages,
              contact forms, surveys, and any application that requires user
              input.
            </p>

            {/* Use Cases */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8 text-sm">
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-3">
                <div className="text-lg mb-1">🔐</div>
                <div>Login Forms</div>
              </div>
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-3">
                <div className="text-lg mb-1">📝</div>
                <div>Signup Pages</div>
              </div>
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-3">
                <div className="text-lg mb-1">📬</div>
                <div>Contact Forms</div>
              </div>
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-3">
                <div className="text-lg mb-1">📋</div>
                <div>Data Entry</div>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="bg-white text-blue-600 px-8 py-4 rounded-2xl text-lg font-medium hover:bg-gray-100 transition-all duration-300 hover:scale-105 shadow-lg">
                View Source Code
              </button>
              <Link
                to="/input-component-doc"
                className="bg-gray-800 bg-opacity-20 backdrop-blur-sm text-white px-8 py-4 rounded-2xl text-lg font-medium hover:bg-opacity-30 transition-all duration-300 hover:scale-105 border border-white border-opacity-20 text-center"
              >
                Full Documentation
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default InputDemo;
