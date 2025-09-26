import React, { useState, useEffect, useRef } from 'react';
import { Choice, ChoiceType, choicesService } from '../../services/choicesService';
import { HiChevronDown, HiSearch, HiCheck } from 'react-icons/hi';

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
  searchable = true // Default to searchable for better UX
}) => {
  const [choices, setChoices] = useState<Choice[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [showTextInput, setShowTextInput] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [highlightedIndex, setHighlightedIndex] = useState(0);

  const dropdownRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Load choices immediately on mount (should already be cached from ProfilePage)
  useEffect(() => {
    loadChoices();
  }, []);

  // Handle click outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSearchTerm('');
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  // Focus search input when dropdown opens
  useEffect(() => {
    if (isOpen && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isOpen]);

  const loadChoices = async () => {
    if (loading || choices.length > 0) return;

    setLoading(true);
    setLoadError(null);

    try {
      const data = await choicesService.getChoices(choiceType);
      if (data.length === 0) {
        setShowTextInput(true);
        setLoadError(`No ${choiceType} options available.`);
      } else {
        setChoices(data);
      }
    } catch (error) {
      console.error(`Failed to load ${choiceType} choices:`, error);
      setLoadError(`Failed to load ${choiceType} options.`);
      setShowTextInput(true);
    } finally {
      setLoading(false);
    }
  };

  // Filter choices based on search term
  const filteredChoices = searchTerm
    ? choices.filter(choice =>
        choice.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
        choice.value.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : choices;

  // Get display value for current selection
  const getDisplayValue = () => {
    if (!value) return '';
    const choice = choices.find(c => c.value === value);
    return choice ? choice.label : value;
  };

  // Handle selection
  const handleSelect = (selectedValue: string) => {
    // Create a synthetic event to match the expected onChange signature
    const syntheticEvent = {
      target: {
        name,
        value: selectedValue
      }
    } as React.ChangeEvent<HTMLSelectElement>;

    onChange(syntheticEvent);
    setIsOpen(false);
    setSearchTerm('');
  };

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) {
      if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown') {
        e.preventDefault();
        setIsOpen(true);
      }
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex(prev =>
          prev < filteredChoices.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex(prev => prev > 0 ? prev - 1 : 0);
        break;
      case 'Enter':
        e.preventDefault();
        if (filteredChoices[highlightedIndex]) {
          handleSelect(filteredChoices[highlightedIndex].value);
        }
        break;
      case 'Escape':
        e.preventDefault();
        setIsOpen(false);
        setSearchTerm('');
        break;
    }
  };

  // Base classes for consistent styling
  const triggerClasses = `
    w-full px-4 py-3 pr-10
    bg-white dark:bg-gray-800
    border border-gray-300 dark:border-gray-600
    rounded-xl
    shadow-sm
    text-gray-700 dark:text-gray-200
    placeholder-gray-500 dark:placeholder-gray-400
    focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400
    focus:border-blue-500 dark:focus:border-blue-400
    transition-all duration-200
    font-medium text-left
    ${disabled ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer hover:border-gray-400 dark:hover:border-gray-500'}
    ${error ? 'border-red-500 focus:ring-red-500' : ''}
  `;

  // Show text input fallback if loading failed
  if (showTextInput) {
    return (
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
        <input
          ref={inputRef}
          type="text"
          name={name}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          disabled={disabled}
          className={triggerClasses}
          autoComplete="off"
        />
        {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
        {loadError && (
          <div className="text-amber-600 dark:text-amber-400 text-xs mt-1">
            <p>{loadError}</p>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {/* Label */}
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>

      {/* Custom Dropdown */}
      <div className="relative" ref={dropdownRef}>
        {/* Trigger Button */}
        <button
          type="button"
          onClick={() => !disabled && !loading && setIsOpen(!isOpen)}
          onKeyDown={handleKeyDown}
          disabled={disabled || loading}
          className={triggerClasses}
        >
          <span className={getDisplayValue() ? '' : 'text-gray-500 dark:text-gray-400'}>
            {loading ? 'Loading options...' : (getDisplayValue() || placeholder)}
          </span>
          <HiChevronDown
            className={`absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 dark:text-gray-400 transition-transform duration-200 ${
              isOpen ? 'rotate-180' : ''
            }`}
          />
        </button>

        {/* Dropdown Panel */}
        {isOpen && !loading && choices.length > 0 && (
          <div className="
            absolute z-50 mt-2 w-full
            transform transition-all duration-200 ease-out origin-top
          ">
            <div className="
              bg-white dark:bg-gray-800
              rounded-xl
              shadow-xl
              border border-gray-200 dark:border-gray-600
              overflow-hidden
            ">
              {/* Search Bar */}
              {searchable && choices.length > 5 && (
                <div className="p-3 border-b border-gray-200 dark:border-gray-700">
                  <div className="relative">
                    <HiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 text-sm" />
                    <input
                      ref={searchInputRef}
                      type="text"
                      value={searchTerm}
                      onChange={(e) => {
                        setSearchTerm(e.target.value);
                        setHighlightedIndex(0);
                      }}
                      placeholder="Search..."
                      className="
                        w-full pl-9 pr-3 py-2
                        bg-gray-50 dark:bg-gray-900
                        text-gray-700 dark:text-gray-200
                        border border-gray-200 dark:border-gray-600
                        rounded-lg text-sm
                        placeholder-gray-500 dark:placeholder-gray-400
                        focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400
                        focus:border-blue-500 dark:focus:border-blue-400
                        transition-all duration-200
                      "
                      onKeyDown={handleKeyDown}
                    />
                  </div>
                </div>
              )}

              {/* Options List */}
              <div className="max-h-64 overflow-y-auto">
                {filteredChoices.length > 0 ? (
                  filteredChoices.map((choice, index) => (
                    <button
                      key={choice.value}
                      type="button"
                      onClick={() => handleSelect(choice.value)}
                      onMouseEnter={() => setHighlightedIndex(index)}
                      className={`
                        w-full px-4 py-3 text-left
                        flex items-center justify-between
                        transition-colors duration-150
                        text-gray-700 dark:text-gray-200
                        cursor-pointer
                        ${value === choice.value
                          ? 'bg-blue-500 text-white hover:bg-blue-600'
                          : highlightedIndex === index
                          ? 'bg-gray-100 dark:bg-gray-700'
                          : 'hover:bg-gray-50 dark:hover:bg-gray-700/50'
                        }
                      `}
                    >
                      <span className="font-medium">{choice.label}</span>
                      {value === choice.value && (
                        <HiCheck className="text-white text-lg" />
                      )}
                    </button>
                  ))
                ) : (
                  <div className="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
                    No options found for "{searchTerm}"
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Loading indicator */}
        {loading && (
          <div className="absolute right-12 top-1/2 transform -translate-y-1/2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
          </div>
        )}
      </div>

      {/* Error message */}
      {error && (
        <p className="text-red-500 text-sm mt-1">{error}</p>
      )}

      {/* Load error with retry */}
      {loadError && !showTextInput && (
        <div className="text-amber-600 dark:text-amber-400 text-xs mt-1 space-y-1">
          <p>{loadError}</p>
          <button
            type="button"
            onClick={() => {
              setLoadError(null);
              loadChoices();
            }}
            className="underline hover:no-underline"
            disabled={loading}
          >
            Retry loading options
          </button>
        </div>
      )}
    </div>
  );
};

export default LazySelect;
