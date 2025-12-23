import React, { useEffect, useRef, useState } from 'react';

export interface ContextMenuItem {
  /** Unique identifier for the menu item */
  id: string;
  /** Label text to display (optional for separators) */
  label?: string;
  /** Icon component from react-icons */
  icon?: React.ReactNode;
  /** Click handler */
  onClick?: () => void;
  /** Whether the item is disabled */
  disabled?: boolean;
  /** Danger variant (red text, for destructive actions) */
  danger?: boolean;
  /** Whether this is a separator (if true, other props are ignored) */
  separator?: boolean;
}

export interface ContextMenuProps {
  /** Whether the menu is open */
  isOpen: boolean;
  /** Callback when menu should close */
  onClose: () => void;
  /** Menu items to display */
  items: ContextMenuItem[];
  /** Position where the menu should appear (from click event) */
  position: { x: number; y: number };
  /** Optional className for additional styling */
  className?: string;
}

/**
 * Reusable context menu component with smart positioning, keyboard navigation,
 * and click-outside detection.
 *
 * @example
 * ```tsx
 * const [menuOpen, setMenuOpen] = useState(false);
 * const [menuPosition, setMenuPosition] = useState({ x: 0, y: 0 });
 *
 * const handleContextMenu = (e: React.MouseEvent) => {
 *   e.preventDefault();
 *   setMenuPosition({ x: e.clientX, y: e.clientY });
 *   setMenuOpen(true);
 * };
 *
 * <div onContextMenu={handleContextMenu}>
 *   Right-click me
 * </div>
 * <ContextMenu
 *   isOpen={menuOpen}
 *   onClose={() => setMenuOpen(false)}
 *   position={menuPosition}
 *   items={[
 *     { id: 'edit', label: 'Edit', icon: <HiPencil />, onClick: () => {} },
 *     { id: 'sep', separator: true },
 *     { id: 'delete', label: 'Delete', icon: <HiTrash />, danger: true, onClick: () => {} }
 *   ]}
 * />
 * ```
 */
const ContextMenu: React.FC<ContextMenuProps> = ({
  isOpen,
  onClose,
  items,
  position,
  className = '',
}) => {
  const menuRef = useRef<HTMLDivElement>(null);
  const [adjustedPosition, setAdjustedPosition] = useState(position);
  const [focusedIndex, setFocusedIndex] = useState<number>(-1);

  // Calculate smart positioning to prevent viewport overflow
  useEffect(() => {
    if (!isOpen || !menuRef.current) return;

    const menu = menuRef.current;
    const menuRect = menu.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    let { x, y } = position;

    // Flip horizontally if overflowing right edge
    if (x + menuRect.width > viewportWidth) {
      x = viewportWidth - menuRect.width - 8; // 8px padding from edge
    }

    // Flip vertically if overflowing bottom edge
    if (y + menuRect.height > viewportHeight) {
      y = viewportHeight - menuRect.height - 8; // 8px padding from edge
    }

    // Ensure we don't go off the left/top edges
    x = Math.max(8, x);
    y = Math.max(8, y);

    setAdjustedPosition({ x, y });
  }, [isOpen, position]);

  // Click-outside detection
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        onClose();
      }
    };

    if (isOpen) {
      // Small delay to prevent immediate closing from the same click that opened it
      setTimeout(() => {
        document.addEventListener('mousedown', handleClickOutside);
      }, 0);

      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [isOpen, onClose]);

  // Keyboard navigation
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      // Filter out separators and disabled items for navigation
      const navigableItems = items
        .map((item, index) => ({ item, index }))
        .filter(({ item }) => !item.separator && !item.disabled);

      const currentNavIndex = navigableItems.findIndex(({ index }) => index === focusedIndex);

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          if (navigableItems.length === 0) return;
          const nextIndex = currentNavIndex < navigableItems.length - 1 ? currentNavIndex + 1 : 0;
          setFocusedIndex(navigableItems[nextIndex].index);
          break;

        case 'ArrowUp':
          e.preventDefault();
          if (navigableItems.length === 0) return;
          const prevIndex = currentNavIndex > 0 ? currentNavIndex - 1 : navigableItems.length - 1;
          setFocusedIndex(navigableItems[prevIndex].index);
          break;

        case 'Enter':
          e.preventDefault();
          if (focusedIndex >= 0 && focusedIndex < items.length) {
            const item = items[focusedIndex];
            if (!item.disabled && !item.separator && item.onClick) {
              item.onClick();
              onClose();
            }
          }
          break;

        case 'Escape':
          e.preventDefault();
          onClose();
          break;

        default:
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, items, focusedIndex, onClose]);

  // Reset focused index when menu opens
  useEffect(() => {
    if (isOpen) {
      setFocusedIndex(-1);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      ref={menuRef}
      className={`fixed z-50 min-w-[180px] rounded-lg shadow-lg border bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 py-1 animate-scale-fade ${className}`}
      style={{
        left: `${adjustedPosition.x}px`,
        top: `${adjustedPosition.y}px`,
      }}
    >
      {items.map((item, index) => {
        if (item.separator) {
          return (
            <div
              key={item.id}
              className="my-1 border-t border-gray-200 dark:border-gray-700"
            />
          );
        }

        const isFocused = index === focusedIndex;
        const baseClasses = 'flex items-center gap-3 px-4 py-2 text-sm transition-colors';
        const interactiveClasses = item.disabled
          ? 'text-gray-400 dark:text-gray-500 cursor-not-allowed'
          : item.danger
          ? 'text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 cursor-pointer'
          : 'text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer';
        const focusClasses = isFocused && !item.disabled
          ? 'bg-gray-100 dark:bg-gray-700'
          : '';

        return (
          <button
            key={item.id}
            className={`${baseClasses} ${interactiveClasses} ${focusClasses} w-full text-left`}
            onClick={() => {
              if (!item.disabled && item.onClick) {
                item.onClick();
                onClose();
              }
            }}
            disabled={item.disabled}
            onMouseEnter={() => setFocusedIndex(index)}
            onMouseLeave={() => setFocusedIndex(-1)}
          >
            {item.icon && (
              <span className="text-lg flex-shrink-0">{item.icon}</span>
            )}
            <span className="flex-1">{item.label}</span>
          </button>
        );
      })}
    </div>
  );
};

export default ContextMenu;
