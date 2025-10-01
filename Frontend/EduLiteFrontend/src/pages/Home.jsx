import { useAuth } from "../hooks/useAuth";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import {
  FaCheckCircle,
  FaRocket,
  FaUsers,
  FaGlobe,
  FaGraduationCap,
  FaBookOpen,
  FaComments,
  FaShieldAlt,
  FaLightbulb,
  FaCode,
  FaArrowRight,
  FaArrowLeft,
} from "react-icons/fa";

const Home = () => {
  const { isLoggedIn } = useAuth();
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === "ar";

  return (
    <div
      className={`text-gray-800 dark:text-gray-100 bg-white dark:bg-gray-900 ${
        isRTL ? "rtl" : "ltr"
      }`}
    >
      {/* Apple-Style Hero Section */}
      <section
        className="relative min-h-screen flex items-center justify-center px-4 sm:px-6 md:px-16 overflow-hidden pt-20"
        style={{ minHeight: "calc(100vh - 0px)" }}
      >
        {/* Background Elements */}
        <div className="absolute inset-0 overflow-hidden">
          {/* Gradient Orbs */}
          <div className="absolute top-1/4 -left-40 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
          <div
            className="absolute bottom-1/4 -right-40 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse"
            style={{ animationDelay: "2s" }}
          ></div>
          <div
            className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-green-500/5 rounded-full blur-3xl animate-pulse"
            style={{ animationDelay: "4s" }}
          ></div>
        </div>

        <div className="max-w-7xl mx-auto w-full relative z-10">
          <div className="text-center">
            {/* Main Headline - Fixed sizing for consistency */}
            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl xl:text-8xl font-light text-gray-900 dark:text-white mb-6 sm:mb-8 md:mb-10 tracking-tight leading-tight max-w-6xl mx-auto">
              {t("home.title")}
            </h1>

            {/* Subtitle - Reduced max size for better control */}
            <p className="text-lg sm:text-xl md:text-2xl lg:text-3xl text-gray-500 dark:text-gray-400 font-light leading-relaxed max-w-4xl mx-auto mb-10 sm:mb-12 md:mb-14 px-2">
              {t("home.intro")}
            </p>

            {/* CTA Buttons - Fixed RTL alignment */}
            <div className="flex flex-col sm:flex-row gap-4 sm:gap-6 justify-center items-center">
              {/* Only show Login button if user is NOT logged in */}
              {!isLoggedIn && (
                <Link
                  to="/login"
                  className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700 text-white px-12 py-4 rounded-full text-lg font-medium transition-all duration-300 hover:scale-105 shadow-lg hover:shadow-xl flex items-center justify-center group"
                >
                  {t("home.loginNow")}
                  {isRTL ? (
                    <FaArrowLeft
                      className={`${
                        isRTL ? "mr-3" : "ml-3"
                      } text-sm group-hover:${
                        isRTL ? "-translate-x-1" : "translate-x-1"
                      } transition-transform duration-300`}
                    />
                  ) : (
                    <FaArrowRight
                      className={`${
                        isRTL ? "mr-3" : "ml-3"
                      } text-sm group-hover:${
                        isRTL ? "-translate-x-1" : "translate-x-1"
                      } transition-transform duration-300`}
                    />
                  )}
                </Link>
              )}

              {/* Learn More button - always visible, but full width when login button is hidden */}
              <Link
                to="/about"
                className={`${
                  !isLoggedIn ? "w-full sm:w-auto" : "w-full sm:w-auto"
                } group relative overflow-hidden bg-gradient-to-r from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 hover:from-blue-100 hover:to-blue-200 dark:hover:from-blue-800/30 dark:hover:to-blue-700/30 text-blue-700 dark:text-blue-300 px-12 py-4 rounded-full text-lg font-medium transition-all duration-300 hover:scale-105 border border-blue-200/60 dark:border-blue-700/40 hover:border-blue-300 dark:hover:border-blue-600 backdrop-blur-sm`}
              >
                <span className="relative z-10 flex items-center justify-center gap-3">
                  {t("home.learnMore")}
                  {isRTL ? (
                    <FaArrowLeft className="text-sm group-hover:-translate-x-1 transition-transform duration-300" />
                  ) : (
                    <FaArrowRight className="text-sm group-hover:translate-x-1 transition-transform duration-300" />
                  )}
                </span>

                {/* Subtle animated background effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-full"></div>
              </Link>
            </div>

            {/* Floating Educational Icons - RTL aware positioning */}
            <div className="absolute inset-0 pointer-events-none">
              {/* Top Left/Right (swapped for RTL) */}
              <div
                className={`absolute top-1/4 ${
                  isRTL ? "right-8 lg:right-20" : "left-8 lg:left-20"
                } w-16 h-16 bg-white dark:bg-gray-800 rounded-full shadow-lg flex items-center justify-center opacity-60 animate-bounce`}
                style={{ animationDelay: "0s", animationDuration: "3s" }}
              >
                <FaGraduationCap className="text-blue-500 text-xl" />
              </div>

              {/* Top Right/Left (swapped for RTL) */}
              <div
                className={`absolute top-1/3 ${
                  isRTL ? "left-8 lg:left-20" : "right-8 lg:right-20"
                } w-12 h-12 bg-white dark:bg-gray-800 rounded-full shadow-lg flex items-center justify-center opacity-60 animate-bounce`}
                style={{ animationDelay: "1s", animationDuration: "4s" }}
              >
                <FaBookOpen className="text-green-500 text-lg" />
              </div>

              {/* Bottom Left/Right (swapped for RTL) */}
              <div
                className={`absolute bottom-1/3 ${
                  isRTL ? "right-16 lg:right-32" : "left-16 lg:left-32"
                } w-14 h-14 bg-white dark:bg-gray-800 rounded-full shadow-lg flex items-center justify-center opacity-60 animate-bounce`}
                style={{ animationDelay: "2s", animationDuration: "3.5s" }}
              >
                <FaRocket className="text-purple-500 text-lg" />
              </div>

              {/* Bottom Right/Left (swapped for RTL) */}
              <div
                className={`absolute bottom-1/4 ${
                  isRTL ? "left-16 lg:left-32" : "right-16 lg:right-32"
                } w-10 h-10 bg-white dark:bg-gray-800 rounded-full shadow-lg flex items-center justify-center opacity-60 animate-bounce`}
                style={{ animationDelay: "3s", animationDuration: "4.5s" }}
              >
                <FaComments className="text-orange-500 text-sm" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Apple-Style About Section */}
      <section className="relative px-6 md:px-12 py-16 md:py-24 dark:bg-gray-900">
        <div className="max-w-6xl mx-auto">
          {/* Minimalist Header */}
          <div className="text-center mb-16 md:mb-24">
            <div className="mb-8">
              <div className="inline-flex items-center justify-center w-32 h-32 md:w-36 md:h-36 rounded-3xl bg-gray-100 dark:bg-gray-800 border border-gray-200/50 dark:border-gray-700/30 shadow-lg dark:shadow-gray-900/20 mb-6 backdrop-blur-sm">
                <FaGraduationCap className="text-gray-600 dark:text-gray-400 text-6xl md:text-7xl fill-black dark:fill-white" />
              </div>
            </div>
            <h2 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-light text-gray-900 dark:text-white mb-8 tracking-tight">
              {t("home.aboutTitle")}
            </h2>
            <p className="text-xl sm:text-2xl md:text-3xl lg:text-4xl text-gray-500 dark:text-gray-400 font-light max-w-4xl mx-auto leading-relaxed mb-12">
              {t("home.about")}
            </p>

            {/* Dark Blue Button - Similar to the image */}
            <div className="inline-block">
              <Link
                to="/about"
                className="group inline-flex items-center gap-3 bg-blue-700 hover:bg-blue-800 dark:bg-blue-600 dark:hover:bg-blue-700 rounded-full px-8 py-4 transition-all duration-300 hover:scale-105 shadow-lg hover:shadow-xl backdrop-blur-sm"
              >
                <span className="text-white font-medium">
                  {t("home.readFullStory")}
                </span>
                {isRTL ? (
                  <FaArrowLeft className="text-white text-sm group-hover:-translate-x-1 transition-transform duration-300" />
                ) : (
                  <FaArrowRight className="text-white text-sm group-hover:translate-x-1 transition-transform duration-300" />
                )}
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Apple-Style Features Section */}
      <section className="relative px-6 md:px-12 py-16 md:py-24 bg-gray-50 dark:bg-gray-900">
        <div className="max-w-6xl mx-auto">
          {/* Features Header */}
          <div className="text-center mb-16">
            <h2 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-light text-gray-900 dark:text-white mb-6 tracking-tight">
              {t("home.featuresTitle")}
            </h2>
            <p className="text-lg sm:text-xl md:text-2xl text-gray-500 dark:text-gray-400 font-light max-w-4xl mx-auto leading-relaxed">
              {t("home.featuresSubtitle")}
            </p>
          </div>

          {/* Features Grid - Apple Card Style */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 md:gap-8 mb-16">
            {Object.entries(t("home.features", { returnObjects: true }))
              .slice(0, 4)
              .map(([key, value], index) => {
                const icons = [FaRocket, FaUsers, FaBookOpen, FaShieldAlt];
                const colors = [
                  {
                    bg: "from-orange-100 to-red-100 dark:from-orange-900/30 dark:to-red-900/30",
                    icon: "text-orange-500",
                  },
                  {
                    bg: "from-blue-100 to-purple-100 dark:from-blue-900/30 dark:to-purple-900/30",
                    icon: "text-blue-500",
                  },
                  {
                    bg: "from-green-100 to-teal-100 dark:from-green-900/30 dark:to-teal-900/30",
                    icon: "text-green-500",
                  },
                  {
                    bg: "from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30",
                    icon: "text-purple-500",
                  },
                ];

                const featureTitles = [
                  t("home.featureTitles.interactive"),
                  t("home.featureTitles.community"),
                  t("home.featureTitles.resources"),
                  t("home.featureTitles.security"),
                ];

                const featureDescriptions = [
                  t("home.featureDescriptions.interactive"),
                  t("home.featureDescriptions.community"),
                  t("home.featureDescriptions.resources"),
                  t("home.featureDescriptions.security"),
                ];

                const IconComponent = icons[index];
                const colorScheme = colors[index];

                return (
                  <div key={key} className="group">
                    <div className="bg-white dark:bg-black rounded-3xl overflow-hidden h-full border border-gray-100 dark:border-gray-800 hover:shadow-lg transition-all duration-500">
                      <div className="p-8 md:p-12">
                        {/* Icon Header */}
                        <div className="mb-6 md:mb-8">
                          <div
                            className={`inline-flex items-center justify-center w-16 h-16 md:w-20 md:h-20 bg-gradient-to-br ${colorScheme.bg} rounded-2xl mb-4 md:mb-6`}
                          >
                            <IconComponent
                              className={`${colorScheme.icon} text-2xl md:text-3xl`}
                            />
                          </div>
                          <h3 className="text-xl sm:text-2xl md:text-3xl font-light text-gray-900 dark:text-white mb-3 md:mb-4 leading-tight">
                            {featureTitles[index]}
                          </h3>
                        </div>

                        <p className="text-base md:text-lg text-gray-600 dark:text-gray-300 leading-relaxed font-light mb-6 md:mb-8">
                          {featureDescriptions[index]}
                        </p>

                        {/* Visual Element */}
                        <div
                          className={`relative h-32 md:h-40 bg-gradient-to-br ${colorScheme.bg
                            .replace("dark:from-", "dark:from-")
                            .replace(
                              "dark:to-",
                              "dark:to-"
                            )} rounded-2xl flex items-center justify-center`}
                        >
                          <div className="relative">
                            <div className="w-12 h-12 md:w-16 md:h-16 bg-white dark:bg-gray-800 rounded-xl shadow-lg flex items-center justify-center transform hover:scale-110 transition-transform duration-300">
                              <IconComponent
                                className={`${colorScheme.icon} text-lg md:text-2xl`}
                              />
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
          </div>

          {/* Bottom Statement */}
          <div className="text-center pt-12 md:pt-16 border-t border-gray-100 dark:border-gray-800">
            <div className="max-w-4xl mx-auto">
              <p className="text-lg sm:text-xl md:text-2xl font-light text-gray-800 dark:text-gray-200 leading-relaxed mb-6">
                "{t("home.technologyQuote")}"
              </p>
              <p className="text-base md:text-lg text-gray-500 dark:text-gray-400 font-light leading-relaxed">
                {t("home.technologyDescription")}
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Apple-Style Open Source Section */}
      <section className="relative px-6 md:px-12 py-32 bg-gray-50 dark:bg-gray-900">
        <div className="max-w-6xl mx-auto">
          <div className="text-center">
            {/* Icon */}
            <div className="mb-12">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-500 rounded-3xl mb-8 shadow-2xl">
                <FaCode className="text-white text-3xl" />
              </div>
            </div>

            {/* Content */}
            <h2 className="text-5xl md:text-6xl lg:text-7xl font-light text-gray-900 dark:text-white mb-8 tracking-tight">
              {t("home.openSourceTitle")}
            </h2>

            <div className="max-w-4xl mx-auto mb-20">
              <p className="text-xl md:text-2xl lg:text-3xl text-gray-500 dark:text-gray-400 font-light leading-relaxed">
                {t("home.openSourceText")}
              </p>
            </div>

            {/* Apple-style CTA Card - Fixed RTL alignment */}
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-3xl p-12 md:p-16 text-white shadow-2xl max-w-4xl mx-auto">
              <h3 className="text-3xl md:text-4xl font-bold mb-8">
                {t("home.joinCommunityTitle")}
              </h3>
              <p className="text-lg md:text-xl lg:text-2xl mb-12 opacity-90 leading-relaxed">
                {t("home.joinCommunityText")}
              </p>
              <div className="flex flex-col sm:flex-row gap-6 justify-center">
                <a
                  href="https://github.com/ibrahim-sisar/EduLite/blob/main/README.md"
                  target="_blank"
                  rel="noreferrer"
                  className="bg-white text-blue-600 px-10 py-5 rounded-2xl text-lg font-bold hover:bg-gray-100 transition-all duration-300 hover:scale-105 shadow-lg flex items-center justify-center group"
                >
                  {t("home.joinGithub")}
                  {isRTL ? (
                    <FaArrowLeft
                      className={`${
                        isRTL ? "mr-3" : "ml-3"
                      } text-sm group-hover:${
                        isRTL ? "-translate-x-1" : "translate-x-1"
                      } transition-transform duration-300`}
                    />
                  ) : (
                    <FaArrowRight
                      className={`${
                        isRTL ? "mr-3" : "ml-3"
                      } text-sm group-hover:${
                        isRTL ? "-translate-x-1" : "translate-x-1"
                      } transition-transform duration-300`}
                    />
                  )}
                </a>
                <Link
                  to="/about"
                  className="bg-gray-800 bg-opacity-20 backdrop-blur-sm text-white px-10 py-5 rounded-2xl text-lg font-bold hover:bg-opacity-30 transition-all duration-300 hover:scale-105 border border-white border-opacity-20"
                >
                  {t("home.learnMore")}
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
