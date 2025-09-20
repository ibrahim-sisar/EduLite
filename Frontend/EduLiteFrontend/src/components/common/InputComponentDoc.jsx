import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  FaBook,
  FaCode,
  FaCheckCircle,
  FaExclamationTriangle,
  FaCopy,
  FaArrowLeft,
  FaLightbulb,
  FaShieldAlt,
  FaEye,
  FaMobile,
  FaBars,
  FaTimes,
} from "react-icons/fa";

const InputComponentDoc = () => {
  const [copiedCode, setCopiedCode] = useState("");
  const [activeSection, setActiveSection] = useState("overview");
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const copyToClipboard = (code, id) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(id);
    setTimeout(() => setCopiedCode(""), 2000);
  };

  // Track active section based on scroll position
  useEffect(() => {
    const handleScroll = () => {
      const sections = [
        "overview",
        "installation",
        "basic-usage",
        "props",
        "examples",
        "validation",
        "advanced-patterns",
        "best-practices",
        "accessibility",
      ];

      const scrollPosition = window.scrollY + 150;

      for (let i = sections.length - 1; i >= 0; i--) {
        const element = document.getElementById(sections[i]);
        if (element && element.offsetTop <= scrollPosition) {
          setActiveSection(sections[i]);
          break;
        }
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      const headerOffset = 120;
      const elementPosition = element.getBoundingClientRect().top;
      const offsetPosition =
        elementPosition + window.pageYOffset - headerOffset;

      window.scrollTo({
        top: offsetPosition,
        behavior: "smooth",
      });

      // Close sidebar on mobile after navigation
      setIsSidebarOpen(false);
    }
  };

  const codeExamples = {
    basic: `import React, { useState } from 'react';
import Input from '../components/common/Input';

function MyForm() {
  const [email, setEmail] = useState('');

  return (
    <Input
      type="email"
      name="email"
      label="Email Address"
      placeholder="Enter your email"
      value={email}
      onChange={(e) => setEmail(e.target.value)}
    />
  );
}`,

    validation: `const [email, setEmail] = useState('');
const [emailError, setEmailError] = useState('');

const handleEmailChange = (e) => {
  const value = e.target.value;
  setEmail(value);
  setEmailError(
    value && !value.includes('@')
      ? 'Please enter a valid email address'
      : ''
  );
};

<Input
  type="email"
  name="email"
  label="Email Address"
  placeholder="user@example.com"
  value={email}
  onChange={handleEmailChange}
  error={emailError}
/>`,

    phone: `const [phone, setPhone] = useState('');
const [phoneError, setPhoneError] = useState('');

const handlePhoneChange = (e) => {
  const value = e.target.value;
  const phoneRegex = /^[\\d\\s\\-\\(\\)]*$/;

  if (phoneRegex.test(value) || value === '') {
    setPhone(value);
    setPhoneError('');
  } else {
    setPhoneError('Only numbers and phone formatting characters allowed');
  }
};

<Input
  type="tel"
  name="phone"
  label="Phone Number"
  placeholder="(555) 123-4567"
  value={phone}
  onChange={handlePhoneChange}
  error={phoneError}
/>`,

    password: `const [password, setPassword] = useState('');
const [passwordError, setPasswordError] = useState('');

const validatePassword = (password) => {
  if (password.length < 8) return 'Password must be at least 8 characters';
  if (!/[A-Z]/.test(password)) return 'Must contain uppercase letter';
  if (!/[a-z]/.test(password)) return 'Must contain lowercase letter';
  if (!/\\d/.test(password)) return 'Must contain a number';
  return '';
};

const handlePasswordChange = (e) => {
  const value = e.target.value;
  setPassword(value);
  setPasswordError(validatePassword(value));
};

<Input
  type="password"
  name="password"
  label="Password"
  placeholder="Enter a strong password"
  value={password}
  onChange={handlePasswordChange}
  error={passwordError}
  required
/>`,

    search: `const [searchQuery, setSearchQuery] = useState('');
const [suggestions, setSuggestions] = useState([]);

const handleSearch = useCallback(
  debounce((query) => {
    if (query.length > 2) {
      // Simulate API call
      fetchSuggestions(query).then(setSuggestions);
    }
  }, 300),
  []
);

const handleSearchChange = (e) => {
  const value = e.target.value;
  setSearchQuery(value);
  handleSearch(value);
};

<Input
  type="search"
  name="search"
  label="Search Products"
  placeholder="Type to search..."
  value={searchQuery}
  onChange={handleSearchChange}
/>`,

    currency: `const [amount, setAmount] = useState('');
const [amountError, setAmountError] = useState('');

const formatCurrency = (value) => {
  // Remove all non-digit characters except decimal point
  const numericValue = value.replace(/[^\\d.]/g, '');
  const parts = numericValue.split('.');

  if (parts.length > 2) {
    return parts[0] + '.' + parts.slice(1).join('');
  }

  if (parts[1] && parts[1].length > 2) {
    return parts[0] + '.' + parts[1].slice(0, 2);
  }

  return numericValue;
};

const handleAmountChange = (e) => {
  const value = formatCurrency(e.target.value);
  setAmount(value);

  if (value && (isNaN(value) || parseFloat(value) <= 0)) {
    setAmountError('Please enter a valid amount');
  } else {
    setAmountError('');
  }
};

<Input
  type="text"
  name="amount"
  label="Amount ($)"
  placeholder="0.00"
  value={amount}
  onChange={handleAmountChange}
  error={amountError}
/>`,

    form: `import { useForm } from 'react-hook-form';

function ContactForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch
  } = useForm();

  const onSubmit = async (data) => {
    try {
      await submitForm(data);
      toast.success('Form submitted successfully!');
    } catch (error) {
      toast.error('Submission failed');
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <Input
        {...register('name', {
          required: 'Name is required',
          minLength: { value: 2, message: 'Name too short' }
        })}
        type="text"
        name="name"
        label="Full Name"
        error={errors.name?.message}
      />

      <Input
        {...register('email', {
          required: 'Email is required',
          pattern: {
            value: /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/,
            message: 'Invalid email format'
          }
        })}
        type="email"
        name="email"
        label="Email Address"
        error={errors.email?.message}
      />

      <button
        type="submit"
        disabled={isSubmitting}
        className="btn-primary"
      >
        {isSubmitting ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  );
}`,

    realTimeValidation: `const [formData, setFormData] = useState({
  email: '',
  password: '',
  confirmPassword: ''
});

const [errors, setErrors] = useState({});
const [touched, setTouched] = useState({});

const validationRules = {
  email: (value) => {
    if (!value) return 'Email is required';
    if (!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(value)) {
      return 'Please enter a valid email address';
    }
    return '';
  },

  password: (value) => {
    if (!value) return 'Password is required';
    if (value.length < 8) return 'Password must be at least 8 characters';
    if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)/.test(value)) {
      return 'Password must contain uppercase, lowercase, and number';
    }
    return '';
  },

  confirmPassword: (value) => {
    if (!value) return 'Please confirm your password';
    if (value !== formData.password) return 'Passwords do not match';
    return '';
  }
};

const validateField = (name, value) => {
  const error = validationRules[name] ? validationRules[name](value) : '';
  setErrors(prev => ({ ...prev, [name]: error }));
  return error;
};

const handleChange = (e) => {
  const { name, value } = e.target;
  setFormData(prev => ({ ...prev, [name]: value }));

  // Only validate if field has been touched
  if (touched[name]) {
    validateField(name, value);
  }

  // Special case: re-validate confirm password when password changes
  if (name === 'password' && touched.confirmPassword) {
    validateField('confirmPassword', formData.confirmPassword);
  }
};

const handleBlur = (e) => {
  const { name, value } = e.target;
  setTouched(prev => ({ ...prev, [name]: true }));
  validateField(name, value);
};

return (
  <div className="space-y-6">
    <Input
      type="email"
      name="email"
      label="Email Address"
      value={formData.email}
      onChange={handleChange}
      onBlur={handleBlur}
      error={touched.email ? errors.email : ''}
      placeholder="user@example.com"
    />

    <Input
      type="password"
      name="password"
      label="Password"
      value={formData.password}
      onChange={handleChange}
      onBlur={handleBlur}
      error={touched.password ? errors.password : ''}
      placeholder="Enter password"
    />

    <Input
      type="password"
      name="confirmPassword"
      label="Confirm Password"
      value={formData.confirmPassword}
      onChange={handleChange}
      onBlur={handleBlur}
      error={touched.confirmPassword ? errors.confirmPassword : ''}
      placeholder="Confirm password"
    />
  </div>
);`,

    asyncValidation: `const [username, setUsername] = useState('');
const [usernameStatus, setUsernameStatus] = useState({
  error: '',
  isChecking: false,
  isAvailable: null
});

// Debounced username validation
const checkUsernameAvailability = useCallback(
  debounce(async (username) => {
    if (username.length < 3) {
      setUsernameStatus({
        error: 'Username must be at least 3 characters',
        isChecking: false,
        isAvailable: null
      });
      return;
    }

    setUsernameStatus(prev => ({ ...prev, isChecking: true }));

    try {
      // Simulate API call
      const response = await fetch(\`/api/check-username/\${username}\`);
      const { available } = await response.json();

      setUsernameStatus({
        error: available ? '' : 'Username is already taken',
        isChecking: false,
        isAvailable: available
      });
    } catch (error) {
      setUsernameStatus({
        error: 'Could not verify username availability',
        isChecking: false,
        isAvailable: null
      });
    }
  }, 500),
  []
);

const handleUsernameChange = (e) => {
  const value = e.target.value;
  setUsername(value);

  // Reset status
  setUsernameStatus({
    error: '',
    isChecking: false,
    isAvailable: null
  });

  // Trigger async validation
  if (value.trim()) {
    checkUsernameAvailability(value);
  }
};

return (
  <div className="relative">
    <Input
      type="text"
      name="username"
      label="Username"
      value={username}
      onChange={handleUsernameChange}
      error={usernameStatus.error}
      placeholder="Enter username"
    />

    {/* Loading indicator */}
    {usernameStatus.isChecking && (
      <div className="absolute right-3 top-1/2 transform -translate-y-1/2 mt-3">
        <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    )}

    {/* Success indicator */}
    {usernameStatus.isAvailable && (
      <div className="absolute right-3 top-1/2 transform -translate-y-1/2 mt-3">
        <FaCheckCircle className="text-green-500" />
      </div>
    )}
  </div>
);`,
  };

  const navigationItems = [
    { id: "overview", label: "Overview" },
    { id: "installation", label: "Installation" },
    { id: "basic-usage", label: "Basic Usage" },
    { id: "props", label: "Props" },
    { id: "examples", label: "Examples" },
    { id: "validation", label: "Validation" },
    { id: "advanced-patterns", label: "Advanced Patterns" },
    { id: "best-practices", label: "Best Practices" },
    { id: "accessibility", label: "Accessibility" },
  ];

  const CodeBlock = ({ code, id, title }) => (
    <div className="bg-gray-900 dark:bg-black rounded-2xl overflow-hidden shadow-lg">
      <div className="flex items-center justify-between px-4 sm:px-6 py-4 bg-gray-800 dark:bg-gray-900 border-b border-gray-700">
        <h4 className="text-white font-medium text-sm sm:text-base truncate mr-4">
          {title}
        </h4>
        <button
          onClick={() => copyToClipboard(code, id)}
          className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs sm:text-sm rounded-lg transition-colors flex-shrink-0"
        >
          <FaCopy className="text-xs" />
          <span className="hidden sm:inline">
            {copiedCode === id ? "Copied!" : "Copy"}
          </span>
        </button>
      </div>
      <div className="overflow-x-auto">
        <pre className="p-4 sm:p-6 text-green-400 text-xs sm:text-sm leading-relaxed">
          <code>{code}</code>
        </pre>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-100 pt-16 sm:pt-20">
      {/* Page Header */}
      <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 sm:py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 sm:gap-4 min-w-0">
              <Link
                to="/input-demo"
                className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors text-sm sm:text-base"
              >
                <FaArrowLeft className="text-xs sm:text-sm" />
                <span className="hidden sm:inline">Back to Demo</span>
                <span className="sm:hidden">Back</span>
              </Link>
              <div className="w-px h-4 sm:h-6 bg-gray-300 dark:bg-gray-600"></div>
              <div className="flex items-center gap-2 sm:gap-3 min-w-0">
                <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg sm:rounded-xl flex items-center justify-center flex-shrink-0">
                  <FaBook className="text-white text-sm sm:text-lg" />
                </div>
                <h1 className="text-lg sm:text-2xl font-light text-gray-900 dark:text-white truncate">
                  <span className="hidden sm:inline">
                    Input Component Documentation
                  </span>
                  <span className="sm:hidden">Input Docs</span>
                </h1>
              </div>
            </div>

            {/* Mobile menu button */}
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="lg:hidden p-2 rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400"
            >
              {isSidebarOpen ? <FaTimes /> : <FaBars />}
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-12">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 lg:gap-8">
          {/* Mobile Sidebar Overlay */}
          {isSidebarOpen && (
            <div
              className="lg:hidden fixed inset-0 z-50 bg-black/50"
              onClick={() => setIsSidebarOpen(false)}
            />
          )}

          {/* Sidebar */}
          <div
            className={`lg:col-span-1 ${
              isSidebarOpen
                ? "fixed inset-y-0 left-0 z-50 w-80 lg:relative lg:w-auto"
                : "hidden lg:block"
            }`}
          >
            <div className="sticky top-24 sm:top-32 bg-white/80 dark:bg-black/40 backdrop-blur-xl rounded-2xl p-4 sm:p-6 border border-gray-200/50 dark:border-gray-700/30 h-fit max-h-[calc(100vh-8rem)] overflow-y-auto">
              <div className="flex items-center justify-between mb-4 lg:block">
                <h3 className="font-semibold text-gray-900 dark:text-white">
                  Contents
                </h3>
                <button
                  onClick={() => setIsSidebarOpen(false)}
                  className="lg:hidden p-1 rounded text-gray-600 dark:text-gray-400"
                >
                  <FaTimes />
                </button>
              </div>
              <nav className="space-y-1 sm:space-y-2">
                {navigationItems.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => scrollToSection(item.id)}
                    className={`block w-full text-left text-sm transition-colors py-2 px-3 rounded-lg ${
                      activeSection === item.id
                        ? "bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 font-medium"
                        : "text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-gray-50 dark:hover:bg-gray-800/50"
                    }`}
                  >
                    {item.label}
                  </button>
                ))}
              </nav>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3 space-y-8 sm:space-y-12">
            {/* Overview */}
            <section id="overview">
              <div className="mb-6 sm:mb-8">
                <div className="inline-flex items-center gap-2 sm:gap-3 mb-4">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl sm:rounded-2xl flex items-center justify-center">
                    <FaCode className="text-white text-lg sm:text-xl" />
                  </div>
                  <h2 className="text-2xl sm:text-3xl font-light text-gray-900 dark:text-white">
                    Overview
                  </h2>
                </div>
                <p className="text-base sm:text-lg text-gray-600 dark:text-gray-300 leading-relaxed">
                  The Input component is a reusable, Apple-style form input with
                  glass-morphism effects, dark mode support, and comprehensive
                  validation features. It follows the established design system
                  and provides a consistent user experience across the
                  application.
                </p>
              </div>

              {/* Key Features */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 mb-6 sm:mb-8">
                <div className="bg-white/80 dark:bg-black/40 backdrop-blur-xl rounded-2xl p-4 sm:p-6 border border-gray-200/50 dark:border-gray-700/30">
                  <FaShieldAlt className="text-blue-500 text-xl sm:text-2xl mb-3" />
                  <h3 className="font-semibold mb-2 text-sm sm:text-base">
                    Robust Validation
                  </h3>
                  <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                    Built-in validation with customizable error messages
                  </p>
                </div>
                <div className="bg-white/80 dark:bg-black/40 backdrop-blur-xl rounded-2xl p-4 sm:p-6 border border-gray-200/50 dark:border-gray-700/30">
                  <FaEye className="text-purple-500 text-xl sm:text-2xl mb-3" />
                  <h3 className="font-semibold mb-2 text-sm sm:text-base">
                    Modern Design
                  </h3>
                  <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                    Glass-morphism with dark mode support
                  </p>
                </div>
                <div className="bg-white/80 dark:bg-black/40 backdrop-blur-xl rounded-2xl p-4 sm:p-6 border border-gray-200/50 dark:border-gray-700/30 sm:col-span-2 lg:col-span-1">
                  <FaMobile className="text-green-500 text-xl sm:text-2xl mb-3" />
                  <h3 className="font-semibold mb-2 text-sm sm:text-base">
                    Fully Accessible
                  </h3>
                  <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                    ARIA compliant with keyboard navigation
                  </p>
                </div>
              </div>
            </section>

            {/* Installation */}
            <section id="installation">
              <h2 className="text-xl sm:text-2xl font-light text-gray-900 dark:text-white mb-4 sm:mb-6">
                Installation & Import
              </h2>
              <CodeBlock
                code="import Input from '../components/common/Input';"
                id="install"
                title="Import Statement"
              />
            </section>

            {/* Basic Usage */}
            <section id="basic-usage">
              <h2 className="text-xl sm:text-2xl font-light text-gray-900 dark:text-white mb-4 sm:mb-6">
                Basic Usage
              </h2>
              <CodeBlock
                code={codeExamples.basic}
                id="basic"
                title="Basic Implementation"
              />
            </section>

            {/* Props */}
            <section id="props">
              <h2 className="text-xl sm:text-2xl font-light text-gray-900 dark:text-white mb-4 sm:mb-6">
                Props
              </h2>

              <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 sm:gap-6">
                {/* Required Props */}
                <div className="bg-white/80 dark:bg-black/40 backdrop-blur-xl rounded-2xl p-4 sm:p-6 border border-gray-200/50 dark:border-gray-700/30">
                  <h3 className="text-lg sm:text-xl font-semibold mb-4 flex items-center gap-2">
                    <FaExclamationTriangle className="text-red-500 text-base sm:text-lg" />
                    <span className="text-sm sm:text-base">Required Props</span>
                  </h3>
                  <div className="space-y-3 sm:space-y-4">
                    {[
                      {
                        name: "type",
                        type: "string",
                        desc: "Input type ('text', 'email', 'password', 'tel', etc.)",
                      },
                      {
                        name: "name",
                        type: "string",
                        desc: "Unique name for the input field",
                      },
                      {
                        name: "value",
                        type: "string",
                        desc: "Current input value (controlled component)",
                      },
                      {
                        name: "onChange",
                        type: "function",
                        desc: "Function to handle value changes",
                      },
                    ].map((prop) => (
                      <div
                        key={prop.name}
                        className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg"
                      >
                        <div className="flex flex-wrap items-center gap-2 mb-1">
                          <code className="text-red-600 dark:text-red-400 font-mono text-xs sm:text-sm">
                            {prop.name}
                          </code>
                          <span className="text-xs bg-gray-200 dark:bg-gray-700 px-2 py-0.5 rounded">
                            {prop.type}
                          </span>
                        </div>
                        <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                          {prop.desc}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Optional Props */}
                <div className="bg-white/80 dark:bg-black/40 backdrop-blur-xl rounded-2xl p-4 sm:p-6 border border-gray-200/50 dark:border-gray-700/30">
                  <h3 className="text-lg sm:text-xl font-semibold mb-4 flex items-center gap-2">
                    <FaCheckCircle className="text-green-500 text-base sm:text-lg" />
                    <span className="text-sm sm:text-base">Optional Props</span>
                  </h3>
                  <div className="space-y-3 sm:space-y-4">
                    {[
                      {
                        name: "label",
                        type: "string",
                        desc: "Label text displayed above the input",
                      },
                      {
                        name: "placeholder",
                        type: "string",
                        desc: "Placeholder text inside the input",
                      },
                      {
                        name: "error",
                        type: "string",
                        desc: "Error message to display below input",
                      },
                      {
                        name: "disabled",
                        type: "boolean",
                        desc: "Whether the input is disabled",
                      },
                      {
                        name: "required",
                        type: "boolean",
                        desc: "Whether the field is required",
                      },
                    ].map((prop) => (
                      <div
                        key={prop.name}
                        className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg"
                      >
                        <div className="flex flex-wrap items-center gap-2 mb-1">
                          <code className="text-blue-600 dark:text-blue-400 font-mono text-xs sm:text-sm">
                            {prop.name}
                          </code>
                          <span className="text-xs bg-gray-200 dark:bg-gray-700 px-2 py-0.5 rounded">
                            {prop.type}
                          </span>
                        </div>
                        <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                          {prop.desc}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </section>

            {/* Examples */}
            <section id="examples">
              <h2 className="text-xl sm:text-2xl font-light text-gray-900 dark:text-white mb-4 sm:mb-6">
                Examples
              </h2>

              <div className="space-y-6 sm:space-y-8">
                <div>
                  <h3 className="text-lg sm:text-xl font-medium mb-3 sm:mb-4">
                    Email with Validation
                  </h3>
                  <CodeBlock
                    code={codeExamples.validation}
                    id="validation-example"
                    title="Email Validation Example"
                  />
                </div>

                <div>
                  <h3 className="text-lg sm:text-xl font-medium mb-3 sm:mb-4">
                    Phone Number Input
                  </h3>
                  <CodeBlock
                    code={codeExamples.phone}
                    id="phone"
                    title="Phone Number with Validation"
                  />
                </div>

                <div>
                  <h3 className="text-lg sm:text-xl font-medium mb-3 sm:mb-4">
                    Password with Strength Validation
                  </h3>
                  <CodeBlock
                    code={codeExamples.password}
                    id="password"
                    title="Password Strength Validation"
                  />
                </div>

                <div>
                  <h3 className="text-lg sm:text-xl font-medium mb-3 sm:mb-4">
                    Search Input with Debouncing
                  </h3>
                  <CodeBlock
                    code={codeExamples.search}
                    id="search"
                    title="Search with Debounced API Calls"
                  />
                </div>

                <div>
                  <h3 className="text-lg sm:text-xl font-medium mb-3 sm:mb-4">
                    Currency/Amount Input
                  </h3>
                  <CodeBlock
                    code={codeExamples.currency}
                    id="currency"
                    title="Currency Formatting Input"
                  />
                </div>

                <div>
                  <h3 className="text-lg sm:text-xl font-medium mb-3 sm:mb-4">
                    Complete Form with React Hook Form
                  </h3>
                  <CodeBlock
                    code={codeExamples.form}
                    id="form"
                    title="Full Form Implementation"
                  />
                </div>
              </div>
            </section>

            {/* Validation Section */}
            <section id="validation">
              <h2 className="text-xl sm:text-2xl font-light text-gray-900 dark:text-white mb-4 sm:mb-6">
                Validation Patterns
              </h2>
              <p className="text-gray-600 dark:text-gray-300 mb-6 sm:mb-8 text-sm sm:text-base">
                The Input component supports various validation patterns to
                ensure data integrity and provide users with immediate feedback.
              </p>

              <div className="space-y-6 sm:space-y-8">
                <div>
                  <h3 className="text-lg sm:text-xl font-medium mb-3 sm:mb-4">
                    Real-time Validation
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300 mb-3 sm:mb-4 text-sm sm:text-base">
                    Validate inputs as users type, with smart timing to avoid
                    being intrusive.
                  </p>
                  <CodeBlock
                    code={codeExamples.realTimeValidation}
                    id="realtime-validation"
                    title="Real-time Form Validation"
                  />
                </div>

                <div>
                  <h3 className="text-lg sm:text-xl font-medium mb-3 sm:mb-4">
                    Async Validation
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300 mb-3 sm:mb-4 text-sm sm:text-base">
                    Validate against external APIs with loading states and
                    debouncing.
                  </p>
                  <CodeBlock
                    code={codeExamples.asyncValidation}
                    id="async-validation"
                    title="Async Username Validation"
                  />
                </div>

                {/* Validation Types */}
                <div>
                  <h3 className="text-lg sm:text-xl font-medium mb-3 sm:mb-4">
                    Common Validation Types
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
                    <div className="bg-white/80 dark:bg-black/40 backdrop-blur-xl rounded-2xl p-4 sm:p-6 border border-gray-200/50 dark:border-gray-700/30">
                      <h4 className="font-semibold mb-3 text-blue-600 dark:text-blue-400 text-sm sm:text-base">
                        Email Validation
                      </h4>
                      <ul className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 space-y-1 sm:space-y-2">
                        <li>• Format validation with regex</li>
                        <li>• Domain existence checking</li>
                        <li>• Disposable email detection</li>
                        <li>• Real-time feedback</li>
                      </ul>
                    </div>

                    <div className="bg-white/80 dark:bg-black/40 backdrop-blur-xl rounded-2xl p-4 sm:p-6 border border-gray-200/50 dark:border-gray-700/30">
                      <h4 className="font-semibold mb-3 text-purple-600 dark:text-purple-400 text-sm sm:text-base">
                        Password Strength
                      </h4>
                      <ul className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 space-y-1 sm:space-y-2">
                        <li>• Minimum length requirements</li>
                        <li>• Character complexity rules</li>
                        <li>• Common password detection</li>
                        <li>• Visual strength indicator</li>
                      </ul>
                    </div>

                    <div className="bg-white/80 dark:bg-black/40 backdrop-blur-xl rounded-2xl p-4 sm:p-6 border border-gray-200/50 dark:border-gray-700/30">
                      <h4 className="font-semibold mb-3 text-green-600 dark:text-green-400 text-sm sm:text-base">
                        Phone Numbers
                      </h4>
                      <ul className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 space-y-1 sm:space-y-2">
                        <li>• International format support</li>
                        <li>• Auto-formatting as user types</li>
                        <li>• Country code validation</li>
                        <li>• Carrier information lookup</li>
                      </ul>
                    </div>

                    <div className="bg-white/80 dark:bg-black/40 backdrop-blur-xl rounded-2xl p-4 sm:p-6 border border-gray-200/50 dark:border-gray-700/30">
                      <h4 className="font-semibold mb-3 text-orange-600 dark:text-orange-400 text-sm sm:text-base">
                        Financial Data
                      </h4>
                      <ul className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 space-y-1 sm:space-y-2">
                        <li>• Currency formatting</li>
                        <li>• Decimal precision control</li>
                        <li>• Range validation</li>
                        <li>• Fraud detection patterns</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* Advanced Patterns */}
            <section id="advanced-patterns">
              <h2 className="text-xl sm:text-2xl font-light text-gray-900 dark:text-white mb-4 sm:mb-6">
                Advanced Patterns
              </h2>

              <div className="space-y-6 sm:space-y-8">
                <div>
                  <h3 className="text-lg sm:text-xl font-medium mb-3 sm:mb-4">
                    Input with Auto-formatting
                  </h3>
                  <CodeBlock
                    code={`const [cardNumber, setCardNumber] = useState('');

const formatCardNumber = (value) => {
  // Remove all non-digit characters
  const digits = value.replace(/\\D/g, '');

  // Add spaces every 4 digits
  const formatted = digits.replace(/(\\d{4})(?=\\d)/g, '$1 ');

  // Limit to 19 characters (16 digits + 3 spaces)
  return formatted.slice(0, 19);
};

const handleCardNumberChange = (e) => {
  const formatted = formatCardNumber(e.target.value);
  setCardNumber(formatted);
};

<Input
  type="text"
  name="cardNumber"
  label="Card Number"
  placeholder="1234 5678 9012 3456"
  value={cardNumber}
  onChange={handleCardNumberChange}
  maxLength="19"
/>`}
                    id="auto-format"
                    title="Auto-formatting Card Number"
                  />
                </div>

                <div>
                  <h3 className="text-lg sm:text-xl font-medium mb-3 sm:mb-4">
                    Conditional Validation
                  </h3>
                  <CodeBlock
                    code={`const [accountType, setAccountType] = useState('personal');
const [businessName, setBusinessName] = useState('');
const [businessError, setBusinessError] = useState('');

const validateBusinessName = (value) => {
  if (accountType === 'business' && !value.trim()) {
    return 'Business name is required for business accounts';
  }
  return '';
};

const handleBusinessNameChange = (e) => {
  const value = e.target.value;
  setBusinessName(value);
  setBusinessError(validateBusinessName(value));
};

// Re-validate when account type changes
useEffect(() => {
  setBusinessError(validateBusinessName(businessName));
}, [accountType, businessName]);

<Input
  type="text"
  name="businessName"
  label="Business Name"
  placeholder="Enter business name"
  value={businessName}
  onChange={handleBusinessNameChange}
  error={businessError}
  disabled={accountType === 'personal'}
/>`}
                    id="conditional"
                    title="Conditional Validation Based on Context"
                  />
                </div>

                <div>
                  <h3 className="text-lg sm:text-xl font-medium mb-3 sm:mb-4">
                    Input with Loading State
                  </h3>
                  <CodeBlock
                    code={`const [username, setUsername] = useState('');
const [usernameError, setUsernameError] = useState('');
const [isCheckingUsername, setIsCheckingUsername] = useState(false);

const checkUsernameAvailability = useCallback(
  debounce(async (username) => {
    if (username.length < 3) return;

    setIsCheckingUsername(true);
    try {
      const isAvailable = await api.checkUsername(username);
      setUsernameError(isAvailable ? '' : 'Username is already taken');
    } catch (error) {
      setUsernameError('Could not verify username availability');
    } finally {
      setIsCheckingUsername(false);
    }
  }, 500),
  []
);

const handleUsernameChange = (e) => {
  const value = e.target.value;
  setUsername(value);
  setUsernameError('');

  if (value.length >= 3) {
    checkUsernameAvailability(value);
  }
};

<div className="relative">
  <Input
    type="text"
    name="username"
    label="Username"
    placeholder="Enter username"
    value={username}
    onChange={handleUsernameChange}
    error={usernameError}
  />
  {isCheckingUsername && (
    <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
      <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
    </div>
  )}
</div>`}
                    id="loading-state"
                    title="Input with Async Validation Loading"
                  />
                </div>
              </div>
            </section>

            {/* Best Practices */}
            <section id="best-practices">
              <h2 className="text-xl sm:text-2xl font-light text-gray-900 dark:text-white mb-4 sm:mb-6">
                Best Practices
              </h2>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
                <div className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-2xl p-4 sm:p-6 border border-green-200/50 dark:border-green-700/30">
                  <h3 className="text-base sm:text-lg font-semibold mb-3 sm:mb-4 text-green-800 dark:text-green-300 flex items-center gap-2">
                    <FaCheckCircle className="text-sm sm:text-base" />
                    <span className="text-sm sm:text-base">Do's</span>
                  </h3>
                  <ul className="space-y-1 sm:space-y-2 text-xs sm:text-sm text-green-700 dark:text-green-300">
                    <li>
                      • Always use controlled components with value and onChange
                    </li>
                    <li>• Provide meaningful labels for accessibility</li>
                    <li>
                      • Use appropriate input types (email, tel, password)
                    </li>
                    <li>• Implement proper validation with error messages</li>
                    <li>
                      • Use React.forwardRef for form library compatibility
                    </li>
                  </ul>
                </div>

                <div className="bg-gradient-to-br from-red-50 to-pink-50 dark:from-red-900/20 dark:to-pink-900/20 rounded-2xl p-4 sm:p-6 border border-red-200/50 dark:border-red-700/30">
                  <h3 className="text-base sm:text-lg font-semibold mb-3 sm:mb-4 text-red-800 dark:text-red-300 flex items-center gap-2">
                    <FaExclamationTriangle className="text-sm sm:text-base" />
                    <span className="text-sm sm:text-base">Don'ts</span>
                  </h3>
                  <ul className="space-y-1 sm:space-y-2 text-xs sm:text-sm text-red-700 dark:text-red-300">
                    <li>• Don't use without proper state management</li>
                    <li>• Don't forget to handle validation errors</li>
                    <li>• Don't use generic 'text' for specialized inputs</li>
                    <li>• Don't skip accessibility attributes</li>
                    <li>• Don't override core styling without good reason</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* Accessibility */}
            <section id="accessibility">
              <h2 className="text-xl sm:text-2xl font-light text-gray-900 dark:text-white mb-4 sm:mb-6">
                Accessibility Features
              </h2>

              <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-2xl p-6 sm:p-8 border border-blue-200/50 dark:border-blue-700/30">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8">
                  <div>
                    <h3 className="text-base sm:text-lg font-semibold mb-3 sm:mb-4 flex items-center gap-2">
                      <FaLightbulb className="text-yellow-500 text-sm sm:text-base" />
                      <span className="text-sm sm:text-base">
                        Built-in Features
                      </span>
                    </h3>
                    <ul className="space-y-1 sm:space-y-2 text-xs sm:text-sm text-gray-700 dark:text-gray-300">
                      <li>• Semantic HTML with proper input elements</li>
                      <li>• Associated labels using htmlFor and id</li>
                      <li>• ARIA attributes for error states</li>
                      <li>• Keyboard navigation support</li>
                    </ul>
                  </div>
                  <div>
                    <h3 className="text-base sm:text-lg font-semibold mb-3 sm:mb-4">
                      Browser Support
                    </h3>
                    <ul className="space-y-1 sm:space-y-2 text-xs sm:text-sm text-gray-700 dark:text-gray-300">
                      <li>• Chrome 57+</li>
                      <li>• Firefox 52+</li>
                      <li>• Safari 10.1+</li>
                      <li>• Edge 16+</li>
                    </ul>
                  </div>
                </div>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InputComponentDoc;
