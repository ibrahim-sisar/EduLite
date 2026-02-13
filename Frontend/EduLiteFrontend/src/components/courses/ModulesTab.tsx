import { useState } from "react";
import { useTranslation } from "react-i18next";
import toast from "react-hot-toast";
import {
  HiPlus,
  HiPencil,
  HiTrash,
  HiChevronUp,
  HiChevronDown,
  HiQueueList,
} from "react-icons/hi2";
import * as coursesApi from "../../services/coursesApi";
import type { CourseModule } from "../../types/courses.types";
import ConfirmationModal from "../common/ConfirmationModal";
import AddModuleModal from "./AddModuleModal";

interface ModulesTabProps {
  courseId: number;
  modules: CourseModule[] | null;
  loading: boolean;
  error: string | null;
  isTeacher: boolean;
  refetch: () => void;
}

/**
 * Converts "app_label.model" format to a human-readable label.
 * e.g. "chat.chatroom" → "Chat Room"
 */
const formatContentType = (ct: string): string => {
  const parts = ct.split(".");
  const model = parts[parts.length - 1];
  // Insert space before capital letters and capitalize first letter
  return model
    .replace(/([A-Z])/g, " $1")
    .replace(/^./, (s) => s.toUpperCase())
    .trim();
};

const ModulesTab: React.FC<ModulesTabProps> = ({
  courseId,
  modules,
  loading,
  error,
  isTeacher,
  refetch,
}) => {
  const { t } = useTranslation();
  const [showAddModal, setShowAddModal] = useState(false);
  const [editModule, setEditModule] = useState<CourseModule | null>(null);
  const [deleteModule, setDeleteModule] = useState<CourseModule | null>(null);
  const [reordering, setReordering] = useState<number | null>(null);

  const handleAddModule = async (data: {
    title?: string;
    content_type: string;
    object_id: number;
  }) => {
    await coursesApi.createCourseModule(courseId, data);
    toast.success(t("course.detail.modules.addSuccess"));
    refetch();
  };

  const handleEditModule = async (data: {
    title?: string;
    content_type: string;
    object_id: number;
  }) => {
    if (!editModule) return;
    await coursesApi.updateCourseModule(courseId, editModule.id, data);
    toast.success(t("course.detail.modules.editSuccess"));
    setEditModule(null);
    refetch();
  };

  const handleDeleteModule = async () => {
    if (!deleteModule) return;
    try {
      await coursesApi.deleteCourseModule(courseId, deleteModule.id);
      toast.success(t("course.detail.modules.deleteSuccess"));
      refetch();
    } catch {
      toast.error(t("course.detail.modules.deleteError"));
    } finally {
      setDeleteModule(null);
    }
  };

  const handleReorder = async (mod: CourseModule, direction: "up" | "down") => {
    if (!modules) return;
    const sorted = [...modules].sort((a, b) => a.order - b.order);
    const idx = sorted.findIndex((m) => m.id === mod.id);
    const swapIdx = direction === "up" ? idx - 1 : idx + 1;
    if (swapIdx < 0 || swapIdx >= sorted.length) return;

    const swapModule = sorted[swapIdx];
    setReordering(mod.id);
    try {
      // Swap orders
      await Promise.all([
        coursesApi.updateCourseModule(courseId, mod.id, {
          order: swapModule.order,
        }),
        coursesApi.updateCourseModule(courseId, swapModule.id, {
          order: mod.order,
        }),
      ]);
      refetch();
    } catch {
      toast.error(t("course.detail.modules.editError"));
    } finally {
      setReordering(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500">{error}</p>
        <button
          onClick={refetch}
          className="mt-2 text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium cursor-pointer"
        >
          {t("course.detail.retryButton")}
        </button>
      </div>
    );
  }

  const moduleList = modules
    ? [...modules].sort((a, b) => a.order - b.order)
    : [];

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          {t("course.detail.modules.title")}
        </h3>
        {isTeacher && (
          <button
            onClick={() => setShowAddModal(true)}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-all text-sm cursor-pointer"
          >
            <HiPlus className="w-4 h-4" />
            {t("course.detail.modules.addButton")}
          </button>
        )}
      </div>

      {/* Empty state */}
      {moduleList.length === 0 ? (
        <div className="text-center py-12">
          <HiQueueList className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
          <p className="text-gray-500 dark:text-gray-400">
            {t("course.detail.modules.emptyState")}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {moduleList.map((mod, idx) => (
            <div
              key={mod.id}
              className={`flex items-center gap-4 p-4 bg-white/60 dark:bg-gray-700/30 rounded-xl border border-gray-200/30 dark:border-gray-600/20 transition-opacity ${reordering === mod.id ? "opacity-50" : ""}`}
            >
              {/* Order number */}
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-lg flex items-center justify-center text-sm font-medium">
                {mod.order}
              </div>

              {/* Module info */}
              <div className="flex-1 min-w-0">
                <p className="font-medium text-gray-900 dark:text-white truncate">
                  {mod.title ||
                    t("course.detail.modules.moduleTitle", {
                      order: mod.order,
                    })}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {formatContentType(mod.content_type)}
                </p>
              </div>

              {/* Teacher actions */}
              {isTeacher && (
                <div className="flex items-center gap-0.5 sm:gap-1 flex-shrink-0">
                  {/* Reorder */}
                  <button
                    onClick={() => handleReorder(mod, "up")}
                    disabled={idx === 0 || reordering !== null}
                    className="p-2.5 sm:p-1.5 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-600/30 rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer"
                    aria-label={t("course.detail.modules.moveUp")}
                    title={t("course.detail.modules.moveUp")}
                  >
                    <HiChevronUp className="w-5 h-5 sm:w-4 sm:h-4" />
                  </button>
                  <button
                    onClick={() => handleReorder(mod, "down")}
                    disabled={
                      idx === moduleList.length - 1 || reordering !== null
                    }
                    className="p-2.5 sm:p-1.5 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-600/30 rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer"
                    aria-label={t("course.detail.modules.moveDown")}
                    title={t("course.detail.modules.moveDown")}
                  >
                    <HiChevronDown className="w-5 h-5 sm:w-4 sm:h-4" />
                  </button>

                  {/* Edit */}
                  <button
                    onClick={() => setEditModule(mod)}
                    className="p-2.5 sm:p-1.5 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors cursor-pointer"
                    aria-label={t("course.detail.modules.edit")}
                    title={t("course.detail.modules.edit")}
                  >
                    <HiPencil className="w-5 h-5 sm:w-4 sm:h-4" />
                  </button>

                  {/* Delete */}
                  <button
                    onClick={() => setDeleteModule(mod)}
                    className="p-2.5 sm:p-1.5 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors cursor-pointer"
                    aria-label={t("course.detail.modules.delete")}
                    title={t("course.detail.modules.delete")}
                  >
                    <HiTrash className="w-5 h-5 sm:w-4 sm:h-4" />
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Add Module Modal */}
      <AddModuleModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSubmit={handleAddModule}
      />

      {/* Edit Module Modal */}
      <AddModuleModal
        isOpen={!!editModule}
        onClose={() => setEditModule(null)}
        onSubmit={handleEditModule}
        editModule={editModule}
      />

      {/* Delete Confirmation */}
      <ConfirmationModal
        isOpen={!!deleteModule}
        onClose={() => setDeleteModule(null)}
        onConfirm={handleDeleteModule}
        title={t("course.detail.modules.deleteConfirmTitle")}
        message={t("course.detail.modules.deleteConfirmMessage", {
          title:
            deleteModule?.title ||
            t("course.detail.modules.moduleTitle", {
              order: deleteModule?.order,
            }),
        })}
        confirmText={t("common.delete")}
        cancelText={t("common.cancel")}
        confirmButtonClass="bg-red-600 hover:bg-red-700 text-white"
      />
    </div>
  );
};

export default ModulesTab;
