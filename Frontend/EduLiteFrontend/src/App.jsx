// src/App.jsx
import { createBrowserRouter, RouterProvider, Outlet } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { AuthProvider } from "./contexts/AuthContext";
import { useAuth } from "./hooks/useAuth";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Home from "./pages/Home";
import BackToTopButton from "./components/common/BackToTopButton";
import ButtonDemo from "./pages/ButtonDemo";
import AboutPage from "./pages/AboutPage";
import LoginPage from "./pages/LoginPage";
import ScrollToTop from "./components/common/ScrollToTop";

import InputDemo from "./pages/InputDemo";
import InputComponentDoc from "./components/common/InputComponentDoc";
import SignUpPage from "./pages/SignupPage";
import ProfilePage from "./pages/ProfilePage";
import SlideshowListPage from "./pages/SlideshowListPage";
import CourseListPage from "./pages/CourseListPage";
import SlideshowDetailPage from "./pages/SlideshowDetailPage";
import SlideshowViewPage from "./pages/SlideshowViewPage";
import SlideshowEditorPage from "./pages/SlideshowEditorPage";
import ProtectedRoute from "./components/ProtectedRoute";
import NotFoundPage from "./pages/NotFoundPage";
import ErrorBoundary from "./components/ErrorBoundary";

// RootLayout component that wraps all routes
const RootLayout = () => {
  const { isLoggedIn, logout, loading } = useAuth();

  // Show loading spinner while checking auth status
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400 font-light">
            Loading...
          </p>
        </div>
      </div>
    );
  }

  return (
    <>
      <ScrollToTop />
      <div className="flex flex-col min-h-screen">
        {/* Pass auth props to your existing Navbar */}
        <Navbar isLoggedIn={isLoggedIn} onLogout={logout} />

        <main className="flex-grow">
          <Outlet />
        </main>

        <Footer />
        <BackToTopButton />

        {/* Toast notifications for login/logout feedback */}
        <Toaster
          position="bottom-left"
          toastOptions={{
            duration: 4000,
            style: {
              background: "rgba(255, 255, 255, 0.9)",
              backdropFilter: "blur(10px)",
              border: "1px solid rgba(255, 255, 255, 0.2)",
              borderRadius: "16px",
              color: "#374151",
            },
          }}
        />
      </div>
    </>
  );
};

// Create the router with all routes
const router = createBrowserRouter([
  {
    path: "/",
    element: <RootLayout />,
    errorElement: <ErrorBoundary />,
    children: [
      {
        index: true,
        element: <Home />,
      },
      {
        path: "about",
        element: <AboutPage />,
      },
      {
        path: "button-demo",
        element: <ButtonDemo />,
      },
      {
        path: "login",
        element: <LoginPage />,
      },
      {
        path: "signup",
        element: <SignUpPage />,
      },
      {
        path: "profile",
        element: (
          <ProtectedRoute>
            <ProfilePage />
          </ProtectedRoute>
        ),
      },
      {
        path: "courses",
        element: (
          <ProtectedRoute>
            <CourseListPage />
          </ProtectedRoute>
        ),
      },
      {
        path: "courses/me",
        element: (
          <ProtectedRoute>
            <CourseListPage view="me" />
          </ProtectedRoute>
        ),
      },
      {
        path: "courses/public",
        element: (
          <ProtectedRoute>
            <CourseListPage view="public" />
          </ProtectedRoute>
        ),
      },
      {
        path: "slideshows",
        element: (
          <ProtectedRoute>
            <SlideshowListPage />
          </ProtectedRoute>
        ),
      },
      {
        path: "slideshows/me",
        element: (
          <ProtectedRoute>
            <SlideshowListPage view="me" />
          </ProtectedRoute>
        ),
      },
      {
        path: "slideshows/public",
        element: (
          <ProtectedRoute>
            <SlideshowListPage view="public" />
          </ProtectedRoute>
        ),
      },

      {
        path: "input-demo",
        element: <InputDemo />,
      },
      {
        path: "input-component-doc",
        element: <InputComponentDoc />,
      },
      {
        path: "slideshows/new",
        element: (
          <ProtectedRoute>
            <SlideshowEditorPage />
          </ProtectedRoute>
        ),
      },
      {
        path: "slideshows/:id",
        element: (
          <ProtectedRoute>
            <SlideshowDetailPage />
          </ProtectedRoute>
        ),
      },
      {
        path: "slideshows/:id/edit",
        element: (
          <ProtectedRoute>
            <SlideshowEditorPage />
          </ProtectedRoute>
        ),
      },
      {
        path: "*",
        element: <NotFoundPage />,
      },
    ],
  },
  {
    path: "/slideshows/:id/present",
    element: (
      <ProtectedRoute>
        <SlideshowViewPage />
      </ProtectedRoute>
    ),
  },
]);

function App() {
  return (
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  );
}

export default App;
