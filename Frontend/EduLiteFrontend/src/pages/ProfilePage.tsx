import React, { useState, useEffect, useRef, ChangeEvent } from "react";
import { useNavigate, useBlocker } from "react-router-dom";
import { FaUser, FaCamera, FaSignOutAlt, FaSave, FaUserFriends, FaCog, FaStickyNote, FaComments, FaGraduationCap, FaLock } from "react-icons/fa";
import toast from "react-hot-toast";
import { useAuth } from "../contexts/AuthContext";
import Input from "../components/common/Input";
import LazySelect from "../components/common/LazySelect";
import UnsavedChangesModal from "../components/common/UnsavedChangesModal";
import { useUnsavedChanges, useFormDirtyState } from "../hooks/useUnsavedChanges";
import { choicesService } from "../services/choicesService";
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
  const [originalFormData, setOriginalFormData] = useState<ProfileUpdateRequest>({});
  const [formData, setFormData] = useState<ProfileUpdateRequest>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [activeTab, setActiveTab] = useState<'friends' | 'settings' | 'notes' | 'chats' | 'courses' | 'privacy'>('friends');
  const [showNavigationModal, setShowNavigationModal] = useState(false);
  const [touchedFields, setTouchedFields] = useState<Set<string>>(new Set());

  // Refs for file upload
  const fileInputRef = useRef<HTMLInputElement>(null);
  const blockerRef = useRef<any>(null);

  // Hooks
  const navigate = useNavigate();
  const { logout } = useAuth();

  // Track form dirty state
  const isDirty = useFormDirtyState(formData, originalFormData);

  // Add browser warning for unsaved changes
  useUnsavedChanges(isDirty, "You have unsaved changes that will be lost.");

  // Block navigation when there are unsaved changes
  const blocker = useBlocker(
    ({ currentLocation, nextLocation }) =>
      isDirty && currentLocation.pathname !== nextLocation.pathname
  );

  // Store blocker reference for modal callbacks
  blockerRef.current = blocker;

  // Handle blocked navigation with custom modal
  useEffect(() => {
    if (blocker.state === 'blocked') {
      setShowNavigationModal(true);
    }
  }, [blocker]);

  // Modal callbacks for navigation
  const handleConfirmNavigation = () => {
    setShowNavigationModal(false);
    if (blockerRef.current?.proceed) {
      blockerRef.current.proceed();
    }
  };

  const handleCancelNavigation = () => {
    setShowNavigationModal(false);
    if (blockerRef.current?.reset) {
      blockerRef.current.reset();
    }
  };

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
        const initialFormData = {
          bio: profileData.bio || '',
          occupation: profileData.occupation || '',
          country: profileData.country || '',
          preferred_language: profileData.preferred_language || '',
          secondary_language: profileData.secondary_language || '',
          website_url: profileData.website_url || ''
        };

        setFormData(initialFormData);
        setOriginalFormData(initialFormData);
      } catch (error) {
        console.error("Failed to load user data:", error);
        toast.error("Failed to load profile data");
      } finally {
        setLoading(false);
      }
    };

    loadUserData();
  }, []);

  // Pre-cache all choice types when component mounts
  useEffect(() => {
    const cacheAllChoices = async () => {
      try {
        // Load all choices in parallel for instant dropdown access
        await Promise.all([
          choicesService.getChoices('occupations'),
          choicesService.getChoices('countries'),
          choicesService.getChoices('languages')
        ]);
        console.log('All choices pre-cached successfully');
      } catch (error) {
        console.error('Failed to pre-cache some choices:', error);
        // Non-critical error - dropdowns will still work with lazy loading
      }
    };

    cacheAllChoices();
  }, []);

  // Handle field blur to track touched fields
  const handleBlur = (e: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement | HTMLButtonElement>) => {
    const { name } = e.target;
    setTouchedFields(prev => new Set(prev).add(name));
  };

  // Handle form field changes (matching SignupPage pattern)
  const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    let { name, value } = e.target;

    // Smart website URL handling
    if (name === 'website_url' && value) {
      // Block insecure http://
      if (value.toLowerCase().startsWith('http://')) {
        setErrors((prev) => ({
          ...prev,
          website_url: "Insecure HTTP not allowed. Please use HTTPS."
        }));
        return; // Don't update the value
      }

      // Auto-add https:// if it looks like a website
      // Check: has a dot, more than 3 chars, and no protocol
      if (value.includes('.') &&
          value.length > 3 &&
          !value.includes('://') &&
          !value.startsWith('https://')) {
        value = `https://${value}`;
      }
    }

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
      const url = formData.website_url.trim();

      // Block http:// for security
      if (url.toLowerCase().startsWith('http://')) {
        newErrors.website_url = "Insecure HTTP not allowed. Please use HTTPS.";
      } else {
        // Validate URL structure
        try {
          new URL(url);
          // Additional check to ensure it's https
          if (!url.toLowerCase().startsWith('https://')) {
            newErrors.website_url = "Please use HTTPS for secure connections";
          }
        } catch {
          newErrors.website_url = "Please enter a valid URL (e.g., https://example.com)";
        }
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

      // Reset original form data to match saved data
      setOriginalFormData(formData);

      toast.success("Profile updated successfully! 🎉");
      // Clear touched fields after successful save
      setTouchedFields(new Set());
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
    // Check for unsaved changes before logout
    if (isDirty) {
      // Use browser's native confirm dialog
      const confirmed = window.confirm("You have unsaved changes. Are you sure you want to logout without saving?");
      if (confirmed) {
        logout();
        navigate("/");
      }
    } else {
      logout();
      navigate("/");
    }
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 p-4 pt-24">
      <div className="w-full max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Profile Section - Takes 2/3 on desktop */}
          <div className="lg:col-span-2">
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
                onBlur={handleBlur}
                placeholder="Tell us about yourself..."
                disabled={saving}
                className={`w-full px-4 py-3 bg-white/80 dark:bg-gray-800/40 backdrop-blur-xl border ${
                  touchedFields.has('bio') && formData.bio !== originalFormData.bio
                    ? 'border-red-300 dark:border-red-500/50'
                    : 'border-gray-200/50 dark:border-gray-700/30'
                } rounded-2xl shadow-lg shadow-gray-200/20 dark:shadow-gray-900/20 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 dark:focus:ring-blue-400/50 focus:shadow-xl focus:shadow-blue-500/30 dark:focus:shadow-blue-400/30 focus:scale-[1.02] transition-all duration-300 ease-out font-light resize-none`}
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
              <LazySelect
                label="Occupation"
                name="occupation"
                value={formData.occupation || ""}
                onChange={handleChange}
                onBlur={handleBlur}
                placeholder="Select your occupation..."
                disabled={saving}
                error={errors.occupation}
                choiceType="occupations"
                className={
                  touchedFields.has('occupation') && formData.occupation !== originalFormData.occupation
                    ? 'border-red-300 dark:border-red-500/50'
                    : ''
                }
              />

              <LazySelect
                label="Country"
                name="country"
                value={formData.country || ""}
                onChange={handleChange}
                onBlur={handleBlur}
                placeholder="Select your country..."
                disabled={saving}
                error={errors.country}
                choiceType="countries"
                searchable={true}
                className={
                  touchedFields.has('country') && formData.country !== originalFormData.country
                    ? 'border-red-300 dark:border-red-500/50'
                    : ''
                }
              />

              <LazySelect
                label="Primary Language"
                name="preferred_language"
                value={formData.preferred_language || ""}
                onChange={handleChange}
                onBlur={handleBlur}
                placeholder="Select your primary language..."
                disabled={saving}
                error={errors.preferred_language}
                choiceType="languages"
                className={
                  touchedFields.has('preferred_language') && formData.preferred_language !== originalFormData.preferred_language
                    ? 'border-red-300 dark:border-red-500/50'
                    : ''
                }
              />

              <LazySelect
                label="Secondary Language"
                name="secondary_language"
                value={formData.secondary_language || ""}
                onChange={handleChange}
                onBlur={handleBlur}
                placeholder="Select your secondary language..."
                disabled={saving}
                error={errors.secondary_language}
                choiceType="languages"
                className={
                  touchedFields.has('secondary_language') && formData.secondary_language !== originalFormData.secondary_language
                    ? 'border-red-300 dark:border-red-500/50'
                    : ''
                }
              />
            </div>

            <Input
              label="Website"
              name="website_url"
              type="url"
              value={formData.website_url || ""}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder="example.com or https://example.com"
              disabled={saving}
              error={errors.website_url}
              className={
                touchedFields.has('website_url') && formData.website_url !== originalFormData.website_url
                  ? 'border-red-300 dark:border-red-500/50'
                  : ''
              }
            />

            {/* Save Button - Clean navbar style */}
            <div className="pt-4">
              <button
                type="submit"
                disabled={saving}
                className="w-full flex items-center justify-center gap-3 px-6 py-3 w-full flex items-center gap-4 px-4 py-3 rounded-xl bg-blue-500/10 hover:bg-blue-500/20 dark:bg-blue-500/10 dark:hover:bg-blue-500/20 transition group cursor-pointer text-white font-medium rounded-xl transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {saving ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span className="font-medium text-blue-600 dark:text-blue-400 group-hover:text-blue-700 dark:group-hover:text-blue-300">Saving Changes...</span>
                  </>
                ) : (
                  <>
                    <FaSave className="text-lg text-blue-600 dark:text-blue-400 group-hover:text-blue-700 dark:group-hover:text-blue-300" />
                    <span className="font-medium text-blue-600 dark:text-blue-400 group-hover:text-blue-700 dark:group-hover:text-blue-300">Save Changes</span>
                  </>
                )}
              </button>
            </div>
          </form>

              {/* Logout Section - Clean navbar style */}
              <div className="mt-8 pt-6 border-t border-gray-200/30 dark:border-gray-700/30">
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center justify-center gap-3 px-6 py-3 w-full flex items-center gap-4 px-4 py-3 rounded-xl bg-red-500/10 hover:bg-red-500/20 dark:bg-red-500/10 dark:hover:bg-red-500/20 transition group cursor-pointer text-white font-medium rounded-xl transition-all duration-200"
                >
                  <FaSignOutAlt className="text-lg text-red-600 dark:text-red-400 group-hover:text-red-700 dark:group-hover:text-red-300" />
                  <span className="font-medium text-red-600 dark:text-red-400 group-hover:text-red-700 dark:group-hover:text-red-300">Sign Out</span>
                </button>
              </div>
            </div>
          </div>

          {/* Sidebar Section - Takes 1/3 on desktop, full width on mobile */}
          <div className="lg:col-span-1">
            <div className="bg-white/80 dark:bg-gray-800/40 backdrop-blur-xl border border-gray-200/50 dark:border-gray-700/30 rounded-3xl shadow-2xl shadow-gray-200/20 dark:shadow-gray-900/20 p-6">

              {/* Tab Navigation */}
              <div className="flex flex-wrap gap-2 mb-6">
                <button
                  onClick={() => setActiveTab('friends')}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl transition-all duration-200 cursor-pointer ${
                    activeTab === 'friends'
                      ? 'bg-blue-500/20 text-blue-600 dark:text-blue-400'
                      : 'bg-gray-100/50 dark:bg-gray-700/30 text-gray-600 dark:text-gray-400 hover:bg-gray-200/50 dark:hover:bg-gray-600/30'
                  }`}
                >
                  <FaUserFriends className="text-lg" />
                  <span className="font-medium">Friends</span>
                </button>

                <button
                  onClick={() => setActiveTab('settings')}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl transition-all duration-200 cursor-pointer ${
                    activeTab === 'settings'
                      ? 'bg-blue-500/20 text-blue-600 dark:text-blue-400'
                      : 'bg-gray-100/50 dark:bg-gray-700/30 text-gray-600 dark:text-gray-400 hover:bg-gray-200/50 dark:hover:bg-gray-600/30'
                  }`}
                >
                  <FaCog className="text-lg" />
                  <span className="font-medium">Settings</span>
                </button>

                <button
                  onClick={() => setActiveTab('notes')}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl transition-all duration-200 cursor-pointer ${
                    activeTab === 'notes'
                      ? 'bg-blue-500/20 text-blue-600 dark:text-blue-400'
                      : 'bg-gray-100/50 dark:bg-gray-700/30 text-gray-600 dark:text-gray-400 hover:bg-gray-200/50 dark:hover:bg-gray-600/30'
                  }`}
                >
                  <FaStickyNote className="text-lg" />
                  <span className="font-medium">Notes</span>
                </button>

                <button
                  onClick={() => setActiveTab('chats')}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl transition-all duration-200 cursor-pointer ${
                    activeTab === 'chats'
                      ? 'bg-blue-500/20 text-blue-600 dark:text-blue-400'
                      : 'bg-gray-100/50 dark:bg-gray-700/30 text-gray-600 dark:text-gray-400 hover:bg-gray-200/50 dark:hover:bg-gray-600/30'
                  }`}
                >
                  <FaComments className="text-lg" />
                  <span className="font-medium">Chats</span>
                </button>

                <button
                  onClick={() => setActiveTab('courses')}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl transition-all duration-200 cursor-pointer ${
                    activeTab === 'courses'
                      ? 'bg-blue-500/20 text-blue-600 dark:text-blue-400'
                      : 'bg-gray-100/50 dark:bg-gray-700/30 text-gray-600 dark:text-gray-400 hover:bg-gray-200/50 dark:hover:bg-gray-600/30'
                  }`}
                >
                  <FaGraduationCap className="text-lg" />
                  <span className="font-medium">Courses</span>
                </button>

                <button
                  onClick={() => setActiveTab('privacy')}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl transition-all duration-200 cursor-pointer ${
                    activeTab === 'privacy'
                      ? 'bg-blue-500/20 text-blue-600 dark:text-blue-400'
                      : 'bg-gray-100/50 dark:bg-gray-700/30 text-gray-600 dark:text-gray-400 hover:bg-gray-200/50 dark:hover:bg-gray-600/30'
                  }`}
                >
                  <FaLock className="text-lg" />
                  <span className="font-medium">Privacy</span>
                </button>
              </div>

              {/* Content Area */}
              <div className="min-h-[300px] flex flex-col items-center justify-center text-center p-8">
                <div className="mb-4">
                  {activeTab === 'friends' && <FaUserFriends className="text-5xl text-gray-300 dark:text-gray-600 mx-auto" />}
                  {activeTab === 'settings' && <FaCog className="text-5xl text-gray-300 dark:text-gray-600 mx-auto" />}
                  {activeTab === 'notes' && <FaStickyNote className="text-5xl text-gray-300 dark:text-gray-600 mx-auto" />}
                  {activeTab === 'chats' && <FaComments className="text-5xl text-gray-300 dark:text-gray-600 mx-auto" />}
                  {activeTab === 'courses' && <FaGraduationCap className="text-5xl text-gray-300 dark:text-gray-600 mx-auto" />}
                  {activeTab === 'privacy' && <FaLock className="text-5xl text-gray-300 dark:text-gray-600 mx-auto" />}
                </div>

                <h3 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-2 capitalize">
                  {activeTab} in Profile
                </h3>

                <p className="text-lg text-gray-500 dark:text-gray-400 mb-4">
                  Coming Soon!
                </p>

                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Visit{' '}
                  <a
                    href="https://github.com/ibrahim-sisar/EduLite"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-500 hover:text-blue-600 dark:text-blue-400 dark:hover:text-blue-300 underline"
                  >
                    https://github.com/ibrahim-sisar/EduLite
                  </a>
                  {' '}if you want to contribute!
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Unsaved Changes Modal */}
      <UnsavedChangesModal
        isOpen={showNavigationModal}
        onConfirm={handleConfirmNavigation}
        onCancel={handleCancelNavigation}
        message="You have unsaved changes. Are you sure you want to leave?"
      />
    </div>
  );
};

export default ProfilePage;
