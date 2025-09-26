import React, { useState, useEffect, useRef } from 'react';
import { Choice, ChoiceType, choicesService } from '../../services/choicesService';

interface LazySelectProps {
  label: string;
  name: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>) => void;
  placeholder?: string;
  disabled?: boolean;
  error?: string;
  choiceType: ChoiceType;
  required?: boolean;
  searchable?: boolean;
}

const LazySelect: React.FC<LazySelectProps> = ({
  label,
  name,
  value,
  onChange,
  placeholder = "Select an option...",
  disabled = false,
  error,
  choiceType,
  required = false,
  searchable = false
}) => {
  const [choices, setChoices] = useState<Choice[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [showTextInput, setShowTextInput] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [hasAttemptedLoad, setHasAttemptedLoad] = useState(false);
  const selectRef = useRef<HTMLSelectElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Check if we have offline choices available
  const hasOfflineChoices = choicesService.hasOfflineChoices(choiceType);

  // Load choices when component mounts if already cached
  useEffect(() => {
    if (hasOfflineChoices && !hasAttemptedLoad) {
      loadChoices();
    }
  }, [hasOfflineChoices]);

  const loadChoices = async () => {
    if (loading || choices.length > 0) return;

    setLoading(true);
    setLoadError(null);
    setHasAttemptedLoad(true);

    try {
      const data = await choicesService.getChoices(choiceType);
      setChoices(data);

      if (data.length === 0) {
        // If no choices loaded, show text input as fallback
        setShowTextInput(true);
        setLoadError(`No ${choiceType} options available. You can type manually.`);
      }
    } catch (error) {
      console.error(`Failed to load ${choiceType} choices:`, error);
      setLoadError(`Failed to load ${choiceType} options. You can type manually.`);
      setShowTextInput(true);
    } finally {
      setLoading(false);
    }
  };

  // Load choices on first interaction (focus/click)
  const handleInteraction = () => {
    if (!hasAttemptedLoad) {
      loadChoices();
    }
    setIsOpen(true);
  };

  // Filter choices for searchable selects
  const filteredChoices = searchable && searchTerm
    ? choices.filter(choice =>
        choice.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
        choice.value.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : choices;

  // Toggle between select and text input
  const toggleInputMode = () => {
    setShowTextInput(!showTextInput);
    if (!showTextInput) {
      // Switching to text input, focus it
      setTimeout(() => inputRef.current?.focus(), 0);
    }
  };

  // Get display value for current selection
  const getDisplayValue = () => {
    if (!value) return '';
    const choice = choices.find(c => c.value === value);
    return choice ? choice.label : value;
  };

  // Base classes for consistent styling with Input component
  const baseClasses = `
    w-full px-4 py-3
    bg-white/80 dark:bg-gray-800/40 backdrop-blur-xl
    border border-gray-200/50 dark:border-gray-700/30
    rounded-2xl
    shadow-lg shadow-gray-200/20 dark:shadow-gray-900/20
    text-gray-900 dark:text-white
    placeholder-gray-500 dark:placeholder-gray-400
    focus:outline-none focus:ring-2 focus:ring-blue-500/50 dark:focus:ring-blue-400/50
    focus:shadow-xl focus:shadow-blue-500/30 dark:focus:shadow-blue-400/30
    focus:scale-[1.02]
    transition-all duration-300 ease-out
    font-light
    ${disabled ? 'opacity-60 cursor-not-allowed' : ''}
    ${error ? 'border-red-500/50 focus:ring-red-500/50' : ''}
  `;

  return (
    <div className="space-y-2">
      {/* Label */}
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>

      <div className="relative">
        {/* Show text input if fallback mode or user chose text input */}
        {showTextInput ? (
          <div className="space-y-2">
            <input
              ref={inputRef}
              type="text"
              name={name}
              value={value}
              onChange={onChange}
              placeholder={placeholder}
              disabled={disabled}
              className={baseClasses}
              autoComplete="off"
            />

            {/* Toggle back to select if choices are available */}
            {choices.length > 0 && (
              <button
                type="button"
                onClick={toggleInputMode}
                className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
                disabled={disabled}
              >
                ← Switch to dropdown
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-2">
            <select
              ref={selectRef}
              name={name}
              value={value}
              onChange={onChange}
              onFocus={handleInteraction}
              onClick={handleInteraction}
              disabled={disabled || loading}
              className={`${baseClasses} ${loading ? 'cursor-wait' : 'cursor-pointer'}`}
            >
              <option value="">
                {loading ? 'Loading options...' : placeholder}
              </option>

              {filteredChoices.map((choice) => (
                <option key={choice.value} value={choice.value}>
                  {choice.label}
                </option>
              ))}
            </select>

            {/* Loading indicator */}
            {loading && (
              <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
              </div>
            )}

            {/* Toggle to text input */}
            <button
              type="button"
              onClick={toggleInputMode}
              className="text-xs text-gray-500 dark:text-gray-400 hover:underline"
              disabled={disabled}
            >
              Type manually instead →
            </button>
          </div>
        )}
      </div>

      {/* Error message */}
      {error && (
        <p className="text-red-500 text-sm mt-1">{error}</p>
      )}

      {/* Load error with retry option */}
      {loadError && !showTextInput && (
        <div className="text-amber-600 dark:text-amber-400 text-xs mt-1 space-y-1">
          <p>{loadError}</p>
          <button
            type="button"
            onClick={() => {
              setLoadError(null);
              setHasAttemptedLoad(false);
              loadChoices();
            }}
            className="underline hover:no-underline"
            disabled={loading}
          >
            Retry loading options
          </button>
        </div>
      )}

      {/* Offline indicator */}
      {hasOfflineChoices && !loading && choices.length > 0 && (
        <p className="text-xs text-green-600 dark:text-green-400 mt-1">
          ✓ Options cached offline
        </p>
      )}
    </div>
  );
};

export default LazySelect;
