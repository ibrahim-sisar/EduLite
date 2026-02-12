import { createPortal } from "react-dom";
import { useTranslation } from "react-i18next";
import { HiCubeTransparent } from "react-icons/hi2";
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

const AddModuleModal: React.FC<AddModuleModalProps> = ({ isOpen, onClose }) => {
  const { t } = useTranslation();

  if (!isOpen) return null;

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-md p-8 border border-gray-200/50 dark:border-gray-700/30 text-center">
        <HiCubeTransparent className="w-16 h-16 text-blue-400 dark:text-blue-500 mx-auto mb-4 opacity-60" />

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          {t("course.detail.addModuleModal.title")}
        </h2>

        <p className="text-gray-500 dark:text-gray-400 mb-6">
          {t("course.detail.addModuleModal.comingSoon")}
        </p>

        <button
          type="button"
          onClick={onClose}
          className="px-6 py-2.5 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-xl font-medium transition-colors cursor-pointer"
        >
          {t("common.close")}
        </button>
      </div>
    </div>,
    document.body,
  );
};

export default AddModuleModal;
