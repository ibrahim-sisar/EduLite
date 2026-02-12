import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import type { CourseModule } from "../../types/courses.types";

interface AddModuleModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: {
    title?: string;
    content_type: string;
    object_id: number;
    order?: number;
  }) => Promise<void>;
  editModule?: CourseModule | null;
}

const AddModuleModal: React.FC<AddModuleModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  editModule,
}) => {
  const { t } = useTranslation();
  const isEdit = !!editModule;

  const [title, setTitle] = useState("");
  const [contentType, setContentType] = useState("");
  const [objectId, setObjectId] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (editModule) {
      setTitle(editModule.title || "");
      setContentType(editModule.content_type);
      setObjectId(String(editModule.object_id));
    } else {
      setTitle("");
      setContentType("");
      setObjectId("");
    }
    setError("");
  }, [editModule, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!contentType.trim()) {
      setError("Content type is required");
      return;
    }

    const parsedObjectId = parseInt(objectId, 10);
    if (isNaN(parsedObjectId) || parsedObjectId <= 0) {
      setError("Please enter a valid object ID");
      return;
    }

    setSubmitting(true);
    setError("");
    try {
      await onSubmit({
        title: title.trim() || undefined,
        content_type: contentType.trim(),
        object_id: parsedObjectId,
      });
      setTitle("");
      setContentType("");
      setObjectId("");
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save module");
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!submitting) {
      setTitle("");
      setContentType("");
      setObjectId("");
      setError("");
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={handleClose}
      />

      {/* Modal */}
      <div className="relative bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-md p-6 border border-gray-200/50 dark:border-gray-700/30">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          {isEdit
            ? t("course.detail.addModuleModal.editTitle")
            : t("course.detail.addModuleModal.title")}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Title (optional) */}
          <div>
            <label
              htmlFor="module-title"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >
              {t("course.detail.addModuleModal.titleLabel")}
            </label>
            <input
              id="module-title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder={t("course.detail.addModuleModal.titlePlaceholder")}
              disabled={submitting}
              className="w-full px-4 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-xl shadow-sm text-gray-700 dark:text-gray-200 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-200 disabled:opacity-60"
            />
          </div>

          {/* Content Type */}
          <div>
            <label
              htmlFor="module-content-type"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >
              {t("course.detail.addModuleModal.contentTypeLabel")}
            </label>
            <input
              id="module-content-type"
              type="text"
              value={contentType}
              onChange={(e) => {
                setContentType(e.target.value);
                setError("");
              }}
              placeholder={t(
                "course.detail.addModuleModal.contentTypePlaceholder",
              )}
              disabled={submitting}
              required
              className="w-full px-4 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-xl shadow-sm text-gray-700 dark:text-gray-200 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-200 disabled:opacity-60"
            />
          </div>

          {/* Object ID */}
          <div>
            <label
              htmlFor="module-object-id"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >
              {t("course.detail.addModuleModal.objectIdLabel")}
            </label>
            <input
              id="module-object-id"
              type="number"
              min="1"
              value={objectId}
              onChange={(e) => {
                setObjectId(e.target.value);
                setError("");
              }}
              placeholder={t(
                "course.detail.addModuleModal.objectIdPlaceholder",
              )}
              disabled={submitting}
              required
              className="w-full px-4 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-xl shadow-sm text-gray-700 dark:text-gray-200 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-200 disabled:opacity-60"
            />
          </div>

          {/* Error */}
          {error && <p className="text-red-500 text-sm">{error}</p>}

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={handleClose}
              disabled={submitting}
              className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-50 cursor-pointer"
            >
              {t("common.cancel")}
            </button>
            <button
              type="submit"
              disabled={submitting || !contentType || !objectId}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-all disabled:cursor-not-allowed disabled:opacity-50 cursor-pointer"
            >
              {submitting
                ? isEdit
                  ? t("course.detail.addModuleModal.saving")
                  : t("course.detail.addModuleModal.adding")
                : isEdit
                  ? t("course.detail.addModuleModal.editSubmitButton")
                  : t("course.detail.addModuleModal.submitButton")}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddModuleModal;
