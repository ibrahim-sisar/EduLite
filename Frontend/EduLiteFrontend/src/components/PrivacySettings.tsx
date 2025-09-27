import React, { useState, useEffect } from "react";
import { FaLock, FaEye, FaUserShield, FaEnvelope, FaUserPlus, FaComments } from "react-icons/fa";
import toast from "react-hot-toast";
import HardLoadSelect from "./common/HardLoadSelect";
import {
  getPrivacySettings,
  updatePrivacySettings,
  getPrivacyChoices,
  type PrivacySettings as PrivacySettingsType,
  type PrivacyChoices
} from "../services/profileApi";

const PrivacySettings: React.FC = () => {
  const [settings, setSettings] = useState<PrivacySettingsType | null>(null);
  const [originalSettings, setOriginalSettings] = useState<PrivacySettingsType | null>(null);
  const [choices, setChoices] = useState<PrivacyChoices | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [touchedFields, setTouchedFields] = useState<Set<string>>(new Set());

  useEffect(() => {
    const loadPrivacyData = async () => {
      try {
        setLoading(true);
        const [settingsData, choicesData] = await Promise.all([
          getPrivacySettings(),
          getPrivacyChoices()
        ]);
        setSettings(settingsData);
        setOriginalSettings(settingsData);
        setChoices(choicesData);
      } catch (error) {
        console.error("Failed to load privacy settings:", error);
        toast.error("Failed to load privacy settings");
      } finally {
        setLoading(false);
      }
    };

    loadPrivacyData();
  }, []);

  const handleSelectChange = (field: keyof PrivacySettingsType, value: string) => {
    if (settings) {
      setSettings({
        ...settings,
        [field]: value
      });
    }
  };

  const handleBlur = (field: string) => {
    setTouchedFields(prev => new Set(prev).add(field));
  };

  const handleToggleChange = (field: keyof PrivacySettingsType) => {
    if (settings) {
      setSettings({
        ...settings,
        [field]: !settings[field]
      });
      // Mark field as touched when toggled
      setTouchedFields(prev => new Set(prev).add(field));
    }
  };

  const hasChanges = JSON.stringify(settings) !== JSON.stringify(originalSettings);

  const handleSave = async () => {
    if (!settings || !hasChanges) return;

    setSaving(true);
    try {
      const updatedSettings = await updatePrivacySettings(settings);
      setSettings(updatedSettings);
      setOriginalSettings(updatedSettings);
      setTouchedFields(new Set()); // Clear touched fields after save
      toast.success("Privacy settings updated successfully!");
    } catch (error: any) {
      console.error("Failed to update privacy settings:", error);
      toast.error(error.message || "Failed to update privacy settings");
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    if (originalSettings) {
      setSettings(originalSettings);
      setTouchedFields(new Set()); // Clear touched fields on reset
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!settings || !choices) {
    return (
      <div className="text-center p-8 text-gray-500 dark:text-gray-400">
        Failed to load privacy settings
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 mb-4">
        <FaLock className="text-xl text-blue-600 dark:text-blue-400" />
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Privacy Settings
        </h3>
      </div>

      <div className="space-y-4">
        {/* Visibility Settings */}
        <div className="p-4 bg-gray-50/50 dark:bg-gray-900/30 rounded-xl space-y-4">
          <h4 className="font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
            <FaEye className="text-sm" />
            Visibility Controls
          </h4>

          <div className="space-y-3">
            <div>
              <HardLoadSelect
                label="Search Visibility"
                name="search_visibility"
                value={settings.search_visibility}
                onChange={(e) => handleSelectChange('search_visibility', e.target.value)}
                onBlur={() => handleBlur('search_visibility')}
                disabled={saving}
                choices={choices.search_visibility}
                hasChanged={settings.search_visibility !== originalSettings?.search_visibility}
                isTouched={touchedFields.has('search_visibility')}
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Who can find you through search
              </p>
            </div>

            <div>
              <HardLoadSelect
                label="Profile Visibility"
                name="profile_visibility"
                value={settings.profile_visibility}
                onChange={(e) => handleSelectChange('profile_visibility', e.target.value)}
                onBlur={() => handleBlur('profile_visibility')}
                disabled={saving}
                choices={choices.profile_visibility}
                hasChanged={settings.profile_visibility !== originalSettings?.profile_visibility}
                isTouched={touchedFields.has('profile_visibility')}
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Who can view your profile
              </p>
            </div>
          </div>
        </div>

        {/* Information Display Settings */}
        <div className="p-4 bg-gray-50/50 dark:bg-gray-900/30 rounded-xl space-y-4">
          <h4 className="font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
            <FaUserShield className="text-sm" />
            Information Display
          </h4>

          <div className="space-y-3">
            <label className="flex items-center justify-between cursor-pointer group">
              <div className="flex items-center gap-3">
                <FaUserShield className="text-gray-500 dark:text-gray-400" />
                <div>
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Show Full Name
                  </span>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Display your full name on your profile
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => handleToggleChange('show_full_name')}
                disabled={saving}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 cursor-pointer ${
                  settings.show_full_name
                    ? 'bg-blue-600'
                    : 'bg-gray-300 dark:bg-gray-600'
                } ${
                  touchedFields.has('show_full_name') && settings.show_full_name !== originalSettings?.show_full_name
                    ? 'ring-2 ring-red-300 dark:ring-red-500/50'
                    : ''
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200 ${
                    settings.show_full_name ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </label>

            <label className="flex items-center justify-between cursor-pointer group">
              <div className="flex items-center gap-3">
                <FaEnvelope className="text-gray-500 dark:text-gray-400" />
                <div>
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Show Email
                  </span>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Make your email visible to others
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => handleToggleChange('show_email')}
                disabled={saving}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 cursor-pointer ${
                  settings.show_email
                    ? 'bg-blue-600'
                    : 'bg-gray-300 dark:bg-gray-600'
                } ${
                  touchedFields.has('show_email') && settings.show_email !== originalSettings?.show_email
                    ? 'ring-2 ring-red-300 dark:ring-red-500/50'
                    : ''
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200 ${
                    settings.show_email ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </label>
          </div>
        </div>

        {/* Interaction Settings */}
        <div className="p-4 bg-gray-50/50 dark:bg-gray-900/30 rounded-xl space-y-4">
          <h4 className="font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
            <FaUserPlus className="text-sm" />
            Interaction Preferences
          </h4>

          <div className="space-y-3">
            <label className="flex items-center justify-between cursor-pointer group">
              <div className="flex items-center gap-3">
                <FaUserPlus className="text-gray-500 dark:text-gray-400" />
                <div>
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Allow Friend Requests
                  </span>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Let others send you friend requests
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => handleToggleChange('allow_friend_requests')}
                disabled={saving}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 cursor-pointer ${
                  settings.allow_friend_requests
                    ? 'bg-blue-600'
                    : 'bg-gray-300 dark:bg-gray-600'
                } ${
                  touchedFields.has('allow_friend_requests') && settings.allow_friend_requests !== originalSettings?.allow_friend_requests
                    ? 'ring-2 ring-red-300 dark:ring-red-500/50'
                    : ''
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200 ${
                    settings.allow_friend_requests ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </label>

            <label className="flex items-center justify-between cursor-pointer group">
              <div className="flex items-center gap-3">
                <FaComments className="text-gray-500 dark:text-gray-400" />
                <div>
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Allow Chat Invites
                  </span>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Let others invite you to chat
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => handleToggleChange('allow_chat_invites')}
                disabled={saving}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 cursor-pointer ${
                  settings.allow_chat_invites
                    ? 'bg-blue-600'
                    : 'bg-gray-300 dark:bg-gray-600'
                } ${
                  touchedFields.has('allow_chat_invites') && settings.allow_chat_invites !== originalSettings?.allow_chat_invites
                    ? 'ring-2 ring-red-300 dark:ring-red-500/50'
                    : ''
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200 ${
                    settings.allow_chat_invites ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </label>
          </div>
        </div>

        {/* Action Buttons */}
        {hasChanges && (
          <div className="flex gap-3 pt-4">
            <button
              onClick={handleSave}
              disabled={saving}
              className="flex-1 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white font-medium rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {saving ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Saving...</span>
                </>
              ) : (
                'Save Changes'
              )}
            </button>
            <button
              onClick={handleReset}
              disabled={saving}
              className="px-4 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 font-medium rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Reset
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default PrivacySettings;
