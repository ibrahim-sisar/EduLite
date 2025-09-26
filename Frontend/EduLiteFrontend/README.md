## TypeScript Support

EduLite frontend now supports TypeScript! We're gradually migrating from JavaScript to TypeScript to improve code quality, developer experience, and maintainability.

### TypeScript Status
- ✅ TypeScript configured and ready
- ✅ Components migrated: `Button.tsx`, `Input.tsx`
- 🚧 Gradual migration in progress
- ✅ JavaScript files still fully supported

### Available Scripts

```bash
npm run dev          # Start development server (works with both JS and TS)
npm run build        # Build for production (handles TS automatically)
npm run type-check   # Run TypeScript type checking
npm run lint         # Lint all files
npm run preview     # Preview production build
```

### TypeScript Configuration

Our `tsconfig.json` is configured for:
- React JSX support
- ES2020 target
- Strict type checking
- JavaScript interoperability (`allowJs: true`)
- Path aliases (`@/` maps to `./src/`)

## Project Architecture

### Folder Structure

```
src/
├── components/
│   ├── common/           # Reusable UI components
│   │   ├── Button.tsx    # TypeScript ✅
│   │   ├── Input.tsx     # TypeScript ✅
│   │   └── BackToTopButton.jsx
│   ├── DarkModeToggle.jsx
│   ├── LanguageSwitcher.jsx
│   ├── Navbar.jsx
│   └── Sidebar.jsx
├── pages/
│   ├── ButtonDemo.jsx    # Component demo pages
│   ├── Home.jsx
│   └── Notifications.jsx
├── assets/               # Static assets
├── i18n/                # Internationalization
├── App.jsx
└── main.jsx
```

### Component Architecture: `components/common`

The `components/common` directory houses our reusable UI components that follow strict coding standards and architectural patterns. These components are designed to be:

- **Reusable** - Can be used across multiple pages and contexts
- **Composable** - Accept props for customization while maintaining consistency
- **Accessible** - Include proper ARIA attributes and keyboard navigation
- **Well-documented** - Comprehensive JSDoc comments and PropTypes
- **Type-safe** - PropTypes validation for all props

#### Example: Button Component Structure

Our `Button.jsx` component exemplifies our coding standards:

```jsx
// File: src/components/common/Button.jsx
// Reusable Button component for EduLite application

import React from "react";
import PropTypes from "prop-types";

/**
 * Comprehensive JSDoc documentation explaining:
 * - Component purpose and usage
 * - All available props with types
 * - Usage examples
 */

// 1. Style Definitions (Separated for maintainability)
const baseStyles = "cursor-pointer inline-flex items-center...";
const typeStyles = { primary: "...", secondary: "...", danger: "..." };
const sizeStyles = { sm: "...", md: "...", lg: "..." };
const widthStyles = { auto: "...", full: "...", half: "..." };

// 2. Component Implementation
const Button = React.forwardRef(({
  children,
  onClick,
  type = "primary",
  size = "md",
  width = "auto",
  disabled = false,
  className = "",
  ...rest
}, ref) => {
  // Style composition logic
  const style = [baseStyles, typeStyles[type], sizeStyles[size], widthStyles[width], className]
    .filter(Boolean)
    .join(" ");

  return (
    <button
      ref={ref}
      type="button"
      className={style}
      onClick={onClick}
      disabled={disabled}
      aria-disabled={disabled}
      {...rest}
    >
      {children}
    </button>
  );
});

// 3. Component Metadata
Button.displayName = "Button";

// 4. PropTypes Validation
Button.propTypes = {
  children: PropTypes.node.isRequired,
  onClick: PropTypes.func,
  type: PropTypes.oneOf(["primary", "secondary", "danger"]),
  size: PropTypes.oneOf(["sm", "md", "lg"]),
  width: PropTypes.oneOf(Object.keys(widthStyles)),
  disabled: PropTypes.bool,
  className: PropTypes.string,
};

export default Button;
```

### TypeScript Migration Guide

When converting a component from JavaScript to TypeScript:

#### 1. Change file extension from `.jsx` to `.tsx`

#### 2. Replace PropTypes with TypeScript interfaces:

**Before (JavaScript with PropTypes):**
```jsx
Button.propTypes = {
  children: PropTypes.node.isRequired,
  onClick: PropTypes.func,
  type: PropTypes.oneOf(["primary", "secondary", "danger"]),
  disabled: PropTypes.bool,
};
```

**After (TypeScript):**
```tsx
interface ButtonProps {
  children: ReactNode;
  onClick?: () => void;
  type?: "primary" | "secondary" | "danger";
  disabled?: boolean;
}
```

#### 3. Add proper typing to React.forwardRef:
```tsx
const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ children, onClick, ...props }, ref) => {
    // Component implementation
  }
);
```

#### 4. Remove PropTypes import and validation code

#### 5. Test with `npm run type-check` to ensure no type errors

### Coding Standards for Common Components

#### 1. File Structure Pattern
- **Header Comment**: File path and purpose
- **Imports**: React, PropTypes, and other dependencies
- **JSDoc Documentation**: Comprehensive component documentation
- **Style Definitions**: Separated style objects for maintainability
- **Component Implementation**: Using React.forwardRef for ref forwarding
- **Component Metadata**: displayName for debugging
- **PropTypes**: Runtime type validation
- **Export**: Default export

#### 2. Naming Conventions
- **Components**: PascalCase (`Button`, `BackToTopButton`)
- **Props**: camelCase (`onClick`, `isDisabled`)
- **Style Objects**: camelCase (`baseStyles`, `typeStyles`)
- **CSS Classes**: Follow Tailwind conventions

#### 3. Props Design
- **Default Values**: Always provide sensible defaults
- **Flexibility**: Accept `className` for customization
- **Accessibility**: Include ARIA attributes
- **Spread Props**: Use `...rest` for additional HTML attributes
- **Validation**: Comprehensive PropTypes for all props

#### 4. Style Architecture
- **Utility-First**: Use Tailwind CSS utilities
- **Composable Styles**: Separate style objects by concern
- **State Variations**: Handle hover, focus, disabled, active states
- **Responsive Design**: Include responsive utilities where appropriate

## Component Demo Pages: Living Documentation

We maintain comprehensive demo pages for all reusable components to serve as living documentation. These pages demonstrate all component variations, use cases, and provide interactive examples for developers.

### Demo Page Structure

Demo pages follow a consistent structure using our `ButtonDemo.jsx` as the template:

```jsx
// File: src/pages/ButtonDemo.jsx
// Living documentation and testing page for Button component

import React from "react";
import Button from "../components/common/Button";

const ButtonDemo = () => (
  <div className="p-8 space-y-6 bg-gray-50 min-h-screen">
    <h1 className="text-2xl font-bold mb-6">Button Component Demo</h1>

    {/* Organized sections for each prop/variation */}
    <div>
      <h2 className="text-xl font-semibold mb-3">Type Variations</h2>
      <div className="space-x-4">
        <Button onClick={() => alert("Primary clicked!")}>Primary (default)</Button>
        <Button type="secondary" onClick={() => alert("Secondary clicked!")}>Secondary</Button>
        <Button type="danger" onClick={() => alert("Danger clicked!")}>Danger</Button>
      </div>
    </div>

    {/* Additional sections for size, disabled states, customization, etc. */}
  </div>
);

export default ButtonDemo;
```

### Demo Page Best Practices

#### 1. Comprehensive Coverage
- **All Props**: Demonstrate every prop and its variations
- **Edge Cases**: Show disabled states, error conditions
- **Combinations**: Display props working together
- **Real-world Usage**: Include practical examples

#### 2. Interactive Elements
- **Click Handlers**: Use `alert()` or console.log for demonstration
- **Visual Feedback**: Show hover, focus, and active states
- **Form Integration**: Demonstrate form usage where applicable

#### 3. Documentation Structure
- **Clear Headings**: Organize sections by prop or use case
- **Explanatory Text**: Include descriptions and usage notes
- **Code Examples**: Show actual implementation snippets
- **Visual Grouping**: Use consistent spacing and layout
