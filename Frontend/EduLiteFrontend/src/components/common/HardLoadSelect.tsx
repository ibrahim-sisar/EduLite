import React from 'react';
import { HiChevronDown } from 'react-icons/hi';

interface HardLoadSelectProps {
  label?: string;
  name: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  onBlur?: (e: React.FocusEvent<HTMLSelectElement | HTMLButtonElement>) => void;
  placeholder?: string;
  disabled?: boolean;
  error?: string;
  choices: Array<[string, string]>;
  required?: boolean;
  className?: string;
  showLabel?: boolean;
  hasChanged?: boolean;
  isTouched?: boolean;
}

const HardLoadSelect: React.FC<HardLoadSelectProps> = ({
  label,
  name,
  value,
  onChange,
  onBlur,
  placeholder = "Select an option...",
  disabled = false,
  error,
  choices,
  required = false,
  className = '',
  showLabel = true,
  hasChanged = false,
  isTouched = false
}) => {
  // Enhanced onChange handler that auto-triggers onBlur for better UX
  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onChange(e);
    // Automatically trigger onBlur to mark field as touched immediately after selection
    if (onBlur) {
      // Create a synthetic blur event with proper name property for unsaved changes tracking
      const syntheticEvent = {
        ...e,
        type: 'blur',
        target: {
          ...e.target,
          name: name  // Ensure name is available for handleBlur in ProfilePage
        }
      } as React.FocusEvent<HTMLSelectElement>;
      onBlur(syntheticEvent);
    }
  };
  // Determine border color based on state
  const getBorderClass = () => {
    if (error) return 'border-red-500 dark:border-red-500/50';
    if (isTouched && hasChanged) return 'border-red-300 dark:border-red-500/50';
    return 'border-gray-300 dark:border-gray-600';
  };

  const selectClasses = `
    w-full px-4 py-3 pr-10
    bg-white dark:bg-gray-800
    border ${getBorderClass()}
    rounded-xl
    shadow-sm
    text-gray-700 dark:text-gray-200
    placeholder-gray-500 dark:placeholder-gray-400
    focus:outline-none
    transition-all duration-200
    appearance-none
    font-medium
    ${disabled ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer hover:border-gray-400 dark:hover:border-gray-500'}
    ${className}
  `;

  return (
    <div className="space-y-1">
      {showLabel && label && (
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}

      <div className="relative">
        <select
          name={name}
          value={value || ''}
          onChange={handleChange}
          onBlur={onBlur}
          disabled={disabled}
          className={selectClasses}
        >
          {!value && placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}
          {choices.map(([choiceValue, choiceLabel]) => (
            <option key={choiceValue} value={choiceValue}>
              {choiceLabel}
            </option>
          ))}
        </select>

        <HiChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 pointer-events-none" />
      </div>

      {error && (
        <p className="text-red-500 text-sm mt-1">{error}</p>
      )}
    </div>
  );
};

export default HardLoadSelect;
