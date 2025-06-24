// src/App.jsx
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import BackToTopButton from "./components/common/BackToTopButton";
import ButtonDemo from "./pages/ButtonDemo";
import AboutPage from "./pages/AboutPage";

function App() {
  return (
    <Router>
      <Navbar />
      <div className="pt-20 px-4">
        <Routes>
          <Route
            path="/"
            element={
              <h1 className="text-2xl font-bold">
                <Home />
              </h1>
            }
          />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/button-demo" element={<ButtonDemo />} />
        </Routes>
        <BackToTopButton />
      </div>
    </Router>
  );
}

export default App;
