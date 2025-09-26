import React, { useState, useEffect, useRef, ChangeEvent } from "react";
import { useNavigate } from "react-router-dom";
import { FaUser, FaCamera, FaSignOutAlt, FaSave } from "react-icons/fa";
import toast from "react-hot-toast";
import { useAuth } from "../contexts/AuthContext";
import Input from "../components/common/Input";
import LazySelect from "../components/common/LazySelect";
import {
  getUserInfo,
  getUserProfile,
  updateUserProfile,
  uploadProfilePicture,
  type User,
  type UserProfile,
  type ProfileUpdateRequest
} from "../services/profileApi";

const ProfilePage: React.FC = () => {
  // State management following existing patterns from LoginPage/SignupPage
  const [userInfo, setUserInfo] = useState<User | null>(null);
  const [profileData, setProfileData] = useState<UserProfile | null>(null);
  const [formData, setFormData] = useState<ProfileUpdateRequest>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);

  // Refs for file upload
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Hooks
  const navigate = useNavigate();
  const { logout } = useAuth();

  // Load user data on component mount
  useEffect(() => {
    const loadUserData = async () => {
      try {
        setLoading(true);

        // Load user info and profile in parallel
        const [userInfoData, profileData] = await Promise.all([
          getUserInfo(),
          getUserProfile()
        ]);

        setUserInfo(userInfoData);
        setProfileData(profileData);

        // Initialize form data with current profile values
        setFormData({
          bio: profileData.bio,
          occupation: profileData.occupation,
          country: profileData.country,
          preferred_language: profileData.preferred_language,
          secondary_language: profileData.secondary_language,
          website_url: profileData.website_url
        });
      } catch (error) {
        console.error("Failed to load user data:", error);
        toast.error("Failed to load profile data");
      } finally {
        setLoading(false);
      }
    };

    loadUserData();
  }, []);

  // Handle form field changes (matching SignupPage pattern)
  const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value || null, // Convert empty strings to null for API
    }));

    // Clear specific field error when user starts typing (matching SignupPage)
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: "",
      }));
    }
  };

  // Form validation (matching SignupPage pattern)
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Website URL validation if provided
    if (formData.website_url && formData.website_url.trim()) {
      try {
        new URL(formData.website_url);
      } catch {
        newErrors.website_url = "Please enter a valid URL (e.g., https://example.com)";
      }
    }

    // Bio length validation
    if (formData.bio && formData.bio.length > 1000) {
      newErrors.bio = "Bio must be less than 1000 characters";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle profile form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      toast.error("Please fix the errors below");
      return;
    }

    setSaving(true);

    try {
      const updatedProfile = await updateUserProfile(formData);
      setProfileData(updatedProfile);
      toast.success("Profile updated successfully! 🎉");
    } catch (error: any) {
      console.error("Failed to update profile:", error);
      toast.error(error.message || "Failed to update profile");
    } finally {
      setSaving(false);
    }
  };

  // Handle profile picture upload
  const handlePictureUpload = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type and size
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      toast.error("Please select a JPG, PNG, or WEBP image");
      return;
    }

    if (file.size > 5 * 1024 * 1024) { // 5MB limit
      toast.error("Image must be less than 5MB");
      return;
    }

    setUploading(true);

    try {
      const updatedProfile = await uploadProfilePicture(file);
      setProfileData(updatedProfile);
      toast.success("Profile picture updated! 📸");
    } catch (error: any) {
      console.error("Failed to upload picture:", error);
      toast.error(error.message || "Failed to upload picture");
    } finally {
      setUploading(false);
    }
  };

  // Handle logout with navigation
  const handleLogout = () => {
    logout();
    navigate("/");
  };

  // Show loading spinner while fetching data (matching LoginPage pattern)
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4 pt-24">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400 font-light">
            Loading your profile...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4 pt-24">
      <div className="w-full max-w-2xl">
        {/* Glass-morphism container matching LoginPage exactly */}
        <div className="bg-white/80 dark:bg-gray-800/40 backdrop-blur-xl border border-gray-200/50 dark:border-gray-700/30 rounded-3xl shadow-2xl shadow-gray-200/20 dark:shadow-gray-900/20 p-8">

          {/* Header matching LoginPage typography */}
          <div className="text-center mb-8">
            <h2 className="text-3xl font-light text-gray-900 dark:text-white mb-2 tracking-tight">
              Your Profile
            </h2>
            <p className="text-gray-500 dark:text-gray-400 font-light">
              Manage your account information
            </p>
          </div>

          {/* Profile Picture Section */}
          <div className="flex flex-col items-center mb-8">
            <div className="relative">
              <div className="w-32 h-32 rounded-full bg-gradient-to-r from-blue-100 to-purple-100 dark:from-blue-900 dark:to-purple-900 flex items-center justify-center overflow-hidden border-4 border-white/50 dark:border-gray-700/50 shadow-xl">
                {profileData?.picture ? (
                  <img
                    src={profileData.picture}
                    alt="Profile"
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <FaUser className="text-4xl text-gray-400 dark:text-gray-500" />
                )}
              </div>

              {/* Camera upload button */}
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading}
                className="absolute bottom-0 right-0 bg-blue-500 hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 text-white p-3 rounded-full shadow-lg transition-all duration-200 hover:scale-110 disabled:opacity-50"
                title="Upload profile picture"
              >
                {uploading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                ) : (
                  <FaCamera className="text-sm" />
                )}
              </button>
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={handlePictureUpload}
              className="hidden"
            />

            <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
              Click the camera to upload a new photo
            </p>
          </div>

          {/* User Info Section (Non-editable) */}
          <div className="mb-8 p-4 bg-gray-50/50 dark:bg-gray-900/30 rounded-2xl">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Account Information
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Username
                </label>
                <p className="text-gray-900 dark:text-white font-light">
                  {userInfo?.username}
                </p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Email
                </label>
                <p className="text-gray-900 dark:text-white font-light">
                  {userInfo?.email}
                </p>
              </div>
            </div>
          </div>

          {/* Profile Form Section - Following LoginPage form patterns */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Bio Field */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Bio
              </label>
              <textarea
                name="bio"
                value={formData.bio || ""}
                onChange={handleChange}
                placeholder="Tell us about yourself..."
                disabled={saving}
                className="w-full px-4 py-3 bg-white/80 dark:bg-gray-800/40 backdrop-blur-xl border border-gray-200/50 dark:border-gray-700/30 rounded-2xl shadow-lg shadow-gray-200/20 dark:shadow-gray-900/20 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 dark:focus:ring-blue-400/50 focus:shadow-xl focus:shadow-blue-500/30 dark:focus:shadow-blue-400/30 focus:scale-[1.02] transition-all duration-300 ease-out font-light resize-none"
                rows={4}
                maxLength={1000}
              />
              {errors.bio && (
                <p className="text-red-500 text-sm mt-1">{errors.bio}</p>
              )}
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {(formData.bio || "").length}/1000 characters
              </p>
            </div>

            {/* Form Fields Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Occupation"
                name="occupation"
                value={formData.occupation || ""}
                onChange={handleChange}
                placeholder="e.g., Student, Teacher"
                disabled={saving}
                error={errors.occupation}
              />

              <Input
                label="Country"
                name="country"
                value={formData.country || ""}
                onChange={handleChange}
                placeholder="Country code (e.g., US, PS)"
                disabled={saving}
                error={errors.country}
              />

              <Input
                label="Primary Language"
                name="preferred_language"
                value={formData.preferred_language || ""}
                onChange={handleChange}
                placeholder="Language code (e.g., en, ar)"
                disabled={saving}
                error={errors.preferred_language}
              />

              <Input
                label="Secondary Language"
                name="secondary_language"
                value={formData.secondary_language || ""}
                onChange={handleChange}
                placeholder="Language code (e.g., en, ar)"
                disabled={saving}
                error={errors.secondary_language}
              />
            </div>

            <Input
              label="Website"
              name="website_url"
              type="url"
              value={formData.website_url || ""}
              onChange={handleChange}
              placeholder="https://your-website.com"
              disabled={saving}
              error={errors.website_url}
            />

            {/* Save Button - Matching LoginPage button style */}
            <div className="pt-4">
              <button
                type="submit"
                disabled={saving}
                className={`
                  w-full px-6 py-4 text-lg font-light
                  bg-blue-500/90 hover:bg-blue-600/90 dark:bg-blue-600/90 dark:hover:bg-blue-700/90
                  text-white
                  backdrop-blur-xl
                  border border-blue-500/20 dark:border-blue-600/20
                  rounded-2xl
                  shadow-lg shadow-blue-500/20 dark:shadow-blue-600/20
                  transition-all duration-300 ease-out

                  focus:outline-none
                  focus:ring-2 focus:ring-blue-500/50 dark:focus:ring-blue-400/50
                  focus:shadow-xl focus:shadow-blue-500/30 dark:focus:shadow-blue-400/30
                  focus:scale-[1.02]

                  hover:shadow-xl hover:shadow-blue-500/30 dark:hover:shadow-blue-600/30
                  hover:scale-[1.02]

                  ${saving ? "opacity-60 cursor-not-allowed" : ""}
                `}
              >
                {saving ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                    Saving Changes...
                  </div>
                ) : (
                  <div className="flex items-center justify-center">
                    <FaSave className="mr-3" />
                    Save Changes
                  </div>
                )}
              </button>
            </div>
          </form>

          {/* Logout Section - At bottom as specified in issue */}
          <div className="mt-8 pt-6 border-t border-gray-200/30 dark:border-gray-700/30">
            <button
              onClick={handleLogout}
              className="w-full px-6 py-4 text-lg font-light bg-red-500/90 hover:bg-red-600/90 dark:bg-red-600/90 dark:hover:bg-red-700/90 text-white backdrop-blur-xl border border-red-500/20 dark:border-red-600/20 rounded-2xl shadow-lg shadow-red-500/20 dark:shadow-red-600/20 transition-all duration-300 ease-out hover:shadow-xl hover:shadow-red-500/30 dark:hover:shadow-red-600/30 hover:scale-[1.02] focus:outline-none focus:ring-2 focus:ring-red-500/50 dark:focus:ring-red-400/50 focus:shadow-xl focus:shadow-red-500/30 dark:focus:shadow-red-400/30 focus:scale-[1.02]"
            >
              <div className="flex items-center justify-center">
                <FaSignOutAlt className="mr-3" />
                Sign Out
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
