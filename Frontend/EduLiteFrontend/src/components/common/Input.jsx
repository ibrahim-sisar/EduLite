import React from "react";
import PropTypes from "prop-types";

/**
 * A reusable Input component designed to match the established Apple-style
 * design system with glass-morphism effects, proper dark mode support,
 * and consistent styling across the application.
 */
const Input = React.forwardRef(
  (
    {
      type = "text",
      name,
      placeholder = "",
      value,
      onChange,
      label,
      error,
      disabled = false,
      required = false,
      className = "",
      compact = false, // Add compact prop
      ...props
    },
    ref
  ) => {
    return (
      <div className={`${compact ? "mb-3" : "mb-6"} ${className}`}>
        {/* Label with Apple-style typography */}
        {label && (
          <label
            htmlFor={name}
            className={`block ${
              compact ? "mb-2" : "mb-3"
            } text-lg font-light tracking-tight transition-colors duration-200 ${
              error
                ? "text-red-600 dark:text-red-400"
                : "text-gray-700 dark:text-gray-200"
            }`}
          >
            {label}
            {required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}

        {/* Input with Apple-style glass-morphism design */}
        <div className="relative">
          <input
            ref={ref}
            id={name}
            type={type}
            name={name}
            placeholder={placeholder}
            value={value}
            onChange={onChange}
            disabled={disabled}
            required={required}
            {...props}
            className={`
              w-full px-6 ${compact ? "py-3" : "py-4"} text-lg font-light
              bg-white/80 dark:bg-gray-800/40
              backdrop-blur-xl
              border border-gray-200/50 dark:border-gray-700/30
              rounded-2xl
              shadow-lg shadow-gray-200/20 dark:shadow-gray-900/20
              transition-all duration-300 ease-out
              placeholder-gray-400 dark:placeholder-gray-500
              text-gray-900 dark:text-white

              focus:outline-none
              focus:ring-2 focus:ring-blue-500/50 dark:focus:ring-blue-400/50
              focus:border-blue-500/50 dark:focus:border-blue-400/50
              focus:bg-white dark:focus:bg-gray-800/60
              focus:shadow-xl focus:shadow-blue-500/10 dark:focus:shadow-blue-400/10
              focus:scale-[1.02]

              hover:border-gray-300/70 dark:hover:border-gray-600/50
              hover:shadow-xl hover:shadow-gray-200/30 dark:hover:shadow-gray-900/30
              hover:bg-white dark:hover:bg-gray-800/50

              ${
                disabled
                  ? "opacity-60 cursor-not-allowed bg-gray-100/50 dark:bg-gray-800/20"
                  : ""
              }

              ${
                error
                  ? "border-red-500/50 dark:border-red-400/50 bg-red-50/50 dark:bg-red-900/10 focus:ring-red-500/50 dark:focus:ring-red-400/50 focus:border-red-500/50 dark:focus:border-red-400/50"
                  : ""
              }
            `}
          />

          {/* Glass overlay effect for focus state */}
          <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-blue-500/5 to-purple-500/5 opacity-0 pointer-events-none transition-opacity duration-300 peer-focus:opacity-100"></div>
        </div>

        {/* Error message with Apple-style typography */}
        {error && (
          <p
            className={`${
              compact ? "mt-2" : "mt-3"
            } text-base font-light text-red-600 dark:text-red-400 tracking-tight animate-pulse`}
          >
            {error}
          </p>
        )}
      </div>
    );
  }
);

// CRITICAL: Add these lines at the end of your Input.jsx file
Input.displayName = "Input";

Input.propTypes = {
  /** The input type (text, email, password, etc.) */
  type: PropTypes.string,

  /** The name attribute for the input */
  name: PropTypes.string.isRequired,

  /** Placeholder text */
  placeholder: PropTypes.string,

  /** Current input value */
  value: PropTypes.string.isRequired,

  /** Change handler function */
  onChange: PropTypes.func.isRequired,

  /** Optional label text displayed above the input */
  label: PropTypes.string,

  /** Error message to display below the input */
  error: PropTypes.string,

  /** Whether the input is disabled */
  disabled: PropTypes.bool,

  /** Whether the input is required */
  required: PropTypes.bool,

  /** Additional CSS classes */
  className: PropTypes.string,

  /** Whether to use compact spacing for forms */
  compact: PropTypes.bool,
};


export default Input;
