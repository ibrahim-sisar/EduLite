import React from 'react';
import { HiChevronDown } from 'react-icons/hi';

interface HardLoadSelectProps {
  label?: string;
  name: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  onBlur?: (e: React.FocusEvent<HTMLSelectElement>) => void;
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
  // Determine border color based on state
  const getBorderClass = () => {
    if (error) return 'border-red-500 dark:border-red-500/50';
    if (isTouched && hasChanged) return 'border-red-300 dark:border-red-500/50';
    return 'border-gray-200/50 dark:border-gray-700/30';
  };

  const selectClasses = `
    w-full px-3 py-2 pr-8
    bg-white/80 dark:bg-gray-800/40
    backdrop-blur-xl
    border ${getBorderClass()}
    rounded-xl
    text-gray-900 dark:text-white
    placeholder-gray-500 dark:placeholder-gray-400
    focus:outline-none focus:ring-2 focus:ring-blue-500/50 dark:focus:ring-blue-400/50
    transition-all duration-200
    appearance-none
    ${disabled ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'}
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
          onChange={onChange}
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
