import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../contexts/AuthContext';
import { I18nextProvider } from 'react-i18next';
import i18n from '../i18n';

/**
 * Custom render function that wraps components with necessary providers
 * for testing. This includes Router, Auth, and i18n contexts.
 *
 * @example
 * import { renderWithProviders } from '@/test/utils';
 *
 * test('renders component', () => {
 *   renderWithProviders(<MyComponent />);
 *   // assertions...
 * });
 */
interface AllTheProvidersProps {
  children: React.ReactNode;
}

const AllTheProviders: React.FC<AllTheProvidersProps> = ({ children }) => {
  return (
    <BrowserRouter>
      <I18nextProvider i18n={i18n}>
        <AuthProvider>
          {children}
        </AuthProvider>
      </I18nextProvider>
    </BrowserRouter>
  );
};

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options });

// Re-export everything from React Testing Library
export * from '@testing-library/react';
export { customRender as renderWithProviders };
