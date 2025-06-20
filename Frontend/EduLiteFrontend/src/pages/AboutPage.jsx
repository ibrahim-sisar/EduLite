import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import {
  FaHeart,
  FaGlobe,
  FaUsers,
  FaLightbulb,
  FaArrowLeft,
  FaRocket,
  FaComments,
  FaBookOpen,
  FaShieldAlt,
  FaGraduationCap,
  FaCode,
  FaHandsHelping,
} from "react-icons/fa";

const AboutPage = () => {
  const { t } = useTranslation();

  return (
    <div className="text-gray-800 dark:text-gray-100 bg-white dark:bg-gray-900 min-h-screen overflow-hidden">
      {/* Animated Hero Section */}
      <section
        className="relative h-screen pt-12 flex items-center justify-center px-6 md:px-16 overflow-hidden"
        style={{ height: "calc(100vh - 80px)" }}
      >
        {/* Animated Background Elements */}
        <div className="absolute inset-0 opacity-10 dark:opacity-5">
          <div className="absolute top-20 left-10 w-72 h-72 bg-blue-500 rounded-full blur-3xl animate-pulse"></div>
          <div
            className="absolute bottom-20 right-10 w-96 h-96 bg-purple-500 rounded-full blur-3xl animate-pulse"
            style={{ animationDelay: "1s" }}
          ></div>
          <div
            className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-green-500 rounded-full blur-3xl animate-pulse"
            style={{ animationDelay: "2s" }}
          ></div>
        </div>

        {/* Floating Educational Icons */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div
            className="absolute top-32 left-20 text-blue-500 opacity-20 animate-bounce"
            style={{ animationDelay: "0s" }}
          >
            <FaGraduationCap className="text-4xl" />
          </div>
          <div
            className="absolute top-48 right-32 text-purple-500 opacity-20 animate-bounce"
            style={{ animationDelay: "1s" }}
          >
            <FaBookOpen className="text-3xl" />
          </div>
          <div
            className="absolute bottom-32 left-32 text-green-500 opacity-20 animate-bounce"
            style={{ animationDelay: "2s" }}
          >
            <FaCode className="text-3xl" />
          </div>
          <div
            className="absolute bottom-48 right-20 text-orange-500 opacity-20 animate-bounce"
            style={{ animationDelay: "1.5s" }}
          >
            <FaHandsHelping className="text-4xl" />
          </div>
        </div>

        <div className="relative max-w-6xl mx-auto text-center z-10">
          <div className="mb-4">
            <div className="inline-block p-3 sm:p-4 md:p-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded-3xl shadow-2xl mb-4">
              <FaGraduationCap className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl text-white"  />
            </div>
          </div>

          <h1 className="text-6xl md:text-8xl font-black mb-8 bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 bg-clip-text text-transparent leading-tight animate-fade-in">
            {t("about.title")}
          </h1>

          <p className="text-2xl md:text-3xl text-gray-600 dark:text-gray-300 leading-relaxed max-w-4xl mx-auto font-light mb-12">
            {t("about.subtitle")}
          </p>

          <div className="flex justify-center gap-8 text-gray-400 dark:text-gray-500">
            <div className="text-center">
              <FaUsers className="text-3xl mx-auto mb-2" />
              <span className="block text-sm">{t("about.heroFeature1")}</span>
            </div>
            <div className="text-center">
              <FaGlobe className="text-3xl mx-auto mb-2" />
              <span className="block text-sm">{t("about.heroFeature2")}</span>
            </div>
            <div className="text-center">
              <FaRocket className="text-3xl mx-auto mb-2" />
              <span className="block text-sm">{t("about.heroFeature3")}</span>
            </div>
          </div>
        </div>

        {/* Scroll Indicator - Desktop Only */}
        <div className="absolute bottom-12 left-1/2 transform -translate-x-1/2 animate-bounce hidden md:block">
          <div className="w-6 h-10 border-2 border-gray-400 dark:border-gray-600 rounded-full flex justify-center">
            <div className="w-1 h-3 bg-gray-400 dark:bg-gray-600 rounded-full mt-2 animate-pulse"></div>
          </div>
        </div>
      </section>

      {/* The Story Section - Minimalistic */}
      <section className="relative px-6 md:px-16 py-24 bg-gradient-to-b from-white to-blue-50/30 dark:bg-gradient-to-b dark:from-gray-900 dark:to-blue-900/10">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-3xl mb-8 shadow-2xl">
              <FaLightbulb className="text-white text-3xl" />
            </div>
            <h2 className="text-5xl md:text-6xl font-bold mb-6 text-gray-900 dark:text-gray-100">
              {t("about.storyTitle")}
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400 max-w-xl mx-auto">
              {t("about.storySubtitle")}
            </p>
          </div>

          <div className="space-y-12">
            {/* Story Header */}
            <div className="text-center">
              <h3 className="text-4xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                {t("about.storyCardTitle")}
              </h3>
              <p className="text-xl text-gray-600 dark:text-gray-400 leading-relaxed">
                {t("about.storyCardSubtitle")}
              </p>
            </div>

            {/* Timeline */}
            <div className="space-y-8">
              {/* 2020 */}
              <div className="flex gap-6 group">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-red-100 dark:bg-red-900/30 border-2 border-red-200 dark:border-red-800 rounded-xl flex items-center justify-center">
                    <span className="text-red-600 dark:text-red-400 font-bold text-sm">
                      2020
                    </span>
                  </div>
                </div>
                <div className="flex-grow pt-2">
                  <h4 className="text-2xl font-bold mb-4 text-gray-900 dark:text-gray-100">
                    {t("about.pandemic.title")}
                  </h4>
                  <p className="text-lg text-gray-600 dark:text-gray-300 leading-relaxed">
                    {t("about.pandemic.description")}
                  </p>
                </div>
              </div>

              {/* Connector */}
              <div className="flex justify-start ml-6">
                <div className="w-px h-6 bg-gray-300 dark:bg-gray-600"></div>
              </div>

              {/* 2023 */}
              <div className="flex gap-6 group">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 border-2 border-blue-200 dark:border-blue-800 rounded-xl flex items-center justify-center">
                    <span className="text-blue-600 dark:text-blue-400 font-bold text-sm">
                      2023
                    </span>
                  </div>
                </div>
                <div className="flex-grow pt-2">
                  <h4 className="text-2xl font-bold mb-4 text-gray-900 dark:text-gray-100">
                    {t("about.gaza.title")}
                  </h4>
                  <p className="text-lg text-gray-600 dark:text-gray-300 leading-relaxed mb-6">
                    {t("about.gaza.description")}
                  </p>

                  <div className="bg-amber-50 dark:bg-amber-900/20 border-l-4 border-amber-400 dark:border-amber-500 rounded-r-lg p-4">
                    <p className="text-xl italic text-amber-800 dark:text-amber-200 font-medium leading-relaxed">
                      "{t("about.visionQuote")}"
                    </p>
                  </div>
                </div>
              </div>

              {/* Connector */}
              <div className="flex justify-start ml-6">
                <div className="w-px h-6 bg-gray-300 dark:bg-gray-600"></div>
              </div>

              {/* Solution */}
              <div className="flex gap-6 group">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 border-2 border-green-200 dark:border-green-800 rounded-xl flex items-center justify-center">
                    <FaRocket className="text-green-600 dark:text-green-400 text-lg" />
                  </div>
                </div>
                <div className="flex-grow pt-2">
                  <h4 className="text-2xl font-bold mb-4 text-gray-900 dark:text-gray-100">
                    {t("about.solution.title")}
                  </h4>
                  <p className="text-lg text-gray-600 dark:text-gray-300 leading-relaxed">
                    {t("about.solution.description")}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="px-4 sm:px-6 md:px-16 py-20 sm:py-24">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-center mb-16 sm:mb-20">
            {t("about.missionTitle")}
          </h2>

          <div className="grid gap-10 md:grid-cols-2">
            {/* Mission 1 */}
            <div className="group">
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-2xl p-6 sm:p-8 md:p-10 shadow-xl hover:shadow-2xl transition-all duration-500 hover:-translate-y-2 border border-blue-200 dark:border-blue-800">
                <div className="flex items-center gap-4 sm:gap-6 mb-6">
                  <div className="w-14 h-14 sm:w-16 sm:h-16 md:w-20 md:h-20 bg-gradient-to-r from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg">
                    <FaUsers className="text-white text-2xl sm:text-3xl" />
                  </div>
                  <h3 className="text-xl sm:text-2xl md:text-3xl font-bold">
                    {t("about.mission1Title")}
                  </h3>
                </div>
                <p className="text-base sm:text-lg text-gray-600 dark:text-gray-300 leading-relaxed">
                  {t("about.mission1Description")}
                </p>
              </div>
            </div>

            {/* Mission 2 */}
            <div className="group">
              <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-2xl p-6 sm:p-8 md:p-10 shadow-xl hover:shadow-2xl transition-all duration-500 hover:-translate-y-2 border border-green-200 dark:border-green-800">
                <div className="flex items-center gap-4 sm:gap-6 mb-6">
                  <div className="w-14 h-14 sm:w-16 sm:h-16 md:w-20 md:h-20 bg-gradient-to-r from-green-500 to-green-600 rounded-2xl flex items-center justify-center shadow-lg">
                    <FaGlobe className="text-white text-2xl sm:text-3xl" />
                  </div>
                  <h3 className="text-xl sm:text-2xl md:text-3xl font-bold">
                    {t("about.mission2Title")}
                  </h3>
                </div>
                <p className="text-base sm:text-lg text-gray-600 dark:text-gray-300 leading-relaxed">
                  {t("about.mission2Description")}
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-gradient-to-b from-gray-50 to-white dark:from-gray-800 dark:to-gray-900 px-6 md:px-16 py-24">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-5xl md:text-6xl font-bold text-center mb-20">
            {t("about.specialTitle")}
          </h2>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="group hover:scale-105 transition-all duration-300 h-full">
              <div className="bg-gradient-to-br from-orange-50 to-red-50 dark:from-orange-900/20 dark:to-red-900/20 p-6 rounded-2xl border border-orange-200 dark:border-orange-800 hover:shadow-xl transition-all duration-300 h-full flex flex-col">
                <div className="flex items-center gap-4 mb-4">
                  <FaRocket className="text-3xl text-orange-500" />
                  <h3 className="text-xl font-bold">
                    {t("about.feature1Title")}
                  </h3>
                </div>
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed flex-grow">
                  {t("about.feature1Description")}
                </p>
              </div>
            </div>

            <div className="group hover:scale-105 transition-all duration-300 h-full">
              <div className="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 p-6 rounded-2xl border border-blue-200 dark:border-blue-800 hover:shadow-xl transition-all duration-300 h-full flex flex-col">
                <div className="flex items-center gap-4 mb-4">
                  <FaComments className="text-3xl text-blue-500" />
                  <h3 className="text-xl font-bold">
                    {t("about.feature2Title")}
                  </h3>
                </div>
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed flex-grow">
                  {t("about.feature2Description")}
                </p>
              </div>
            </div>

            <div className="group hover:scale-105 transition-all duration-300 h-full">
              <div className="bg-gradient-to-br from-green-50 to-teal-50 dark:from-green-900/20 dark:to-teal-900/20 p-6 rounded-2xl border border-green-200 dark:border-green-800 hover:shadow-xl transition-all duration-300 h-full flex flex-col">
                <div className="flex items-center gap-4 mb-4">
                  <FaBookOpen className="text-3xl text-green-500" />
                  <h3 className="text-xl font-bold">
                    {t("about.feature3Title")}
                  </h3>
                </div>
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed flex-grow">
                  {t("about.feature3Description")}
                </p>
              </div>
            </div>

            <div className="group hover:scale-105 transition-all duration-300 h-full">
              <div className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 p-6 rounded-2xl border border-purple-200 dark:border-purple-800 hover:shadow-xl transition-all duration-300 h-full flex flex-col">
                <div className="flex items-center gap-4 mb-4">
                  <FaShieldAlt className="text-3xl text-purple-500" />
                  <h3 className="text-xl font-bold">
                    {t("about.feature4Title")}
                  </h3>
                </div>
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed flex-grow">
                  {t("about.feature4Description")}
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Community Section */}
      <section className="relative px-6 md:px-16 py-24 overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-red-500 rounded-full blur-3xl animate-pulse"></div>
          <div
            className="absolute bottom-0 right-1/4 w-96 h-96 bg-pink-500 rounded-full blur-3xl animate-pulse"
            style={{ animationDelay: "1s" }}
          ></div>
        </div>

        <div className="relative max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-red-500 to-pink-500 rounded-3xl mb-12 shadow-2xl">
            <FaHeart className="text-white text-3xl" />
          </div>

          <h2 className="text-5xl md:text-6xl font-bold mb-12">
            {t("about.communityTitle")}
          </h2>

          <div className="space-y-12">
            <div className="bg-white dark:bg-gray-800 rounded-3xl p-10 md:p-16 shadow-2xl border border-gray-100 dark:border-gray-700">
              <p className="text-2xl md:text-3xl text-gray-700 dark:text-gray-300 leading-relaxed font-medium mb-12">
                {t("about.communityDescription")}
              </p>

              <p className="text-xl md:text-2xl text-gray-500 dark:text-gray-400 leading-relaxed font-light italic">
                {t("about.communityOrigin")}
              </p>
            </div>

            <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-3xl p-12 md:p-16 text-white shadow-2xl">
              <h3 className="text-4xl font-bold mb-8">
                {t("about.joinTitle")}
              </h3>
              <p className="text-xl md:text-2xl mb-12 opacity-90 leading-relaxed">
                {t("about.joinDescription")}
              </p>
              <div className="flex flex-col sm:flex-row gap-6 justify-center">
                <a
                  href="https://github.com/ibrahim-sisar/EduLite"
                  target="_blank"
                  rel="noreferrer"
                  className="bg-white text-blue-600 px-10 py-5 rounded-2xl text-lg font-bold hover:bg-gray-100 transition-all duration-300 hover:scale-105 shadow-lg"
                >
                  {t("about.contributeButton")}
                </a>
                <Link
                  to="/"
                  className="bg-gray-800 bg-opacity-20 backdrop-blur-sm text-white px-10 py-5 rounded-2xl text-lg font-bold hover:bg-opacity-30 transition-all duration-300 hover:scale-105 border border-white border-opacity-20"
                >
                  {t("about.backToHomeButton")}
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer Quote */}
      <section className="bg-gradient-to-r from-gray-900 to-gray-800 dark:from-gray-800 dark:to-gray-900 px-6 md:px-16 py-20">
        <div className="max-w-4xl mx-auto text-center">
          <blockquote className="text-3xl md:text-4xl italic text-white font-light leading-relaxed">
            "{t("about.finalQuote")}"
          </blockquote>
        </div>
      </section>
    </div>
  );
};

export default AboutPage;
