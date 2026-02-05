import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { HiMenu, HiTrash, HiDuplicate } from 'react-icons/hi';
import type { EditorSlide } from '../../../types/editor.types';

interface SlideListProps {
  slides: EditorSlide[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onAdd: () => void;
  onDelete: (id: string) => void;
  onReorder: (slides: EditorSlide[]) => void;
  onDuplicate: (id: string) => void;
}

function SortableSlideItem({
  slide,
  index,
  isSelected,
  onSelect,
  onDelete,
  onDuplicate,
}: {
  slide: EditorSlide;
  index: number;
  isSelected: boolean;
  onSelect: () => void;
  onDelete: () => void;
  onDuplicate: () => void;
}) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: slide.tempId });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  const preview = slide.content.split('\n')[0].replace(/^#+\s*/, '').substring(0, 50) || 'Empty slide';

  return (
    <div ref={setNodeRef} style={style} className={`group relative`}>
      <div
        className={`flex items-start gap-2 p-3 border rounded-lg cursor-pointer transition-all ${
          isSelected
            ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-500'
            : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
        }`}
        onClick={onSelect}
      >
        <div {...attributes} {...listeners} className="cursor-grab active:cursor-grabbing pt-1">
          <HiMenu className="w-4 h-4 text-gray-400" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold text-gray-500">Slide {index + 1}</span>
          </div>
          <p className="text-sm text-gray-700 dark:text-gray-300 truncate">{preview}</p>
        </div>

        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onDuplicate();
            }}
            className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
            title="Duplicate"
          >
            <HiDuplicate className="w-4 h-4 text-gray-500" />
          </button>
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onDelete();
            }}
            className="p-1 rounded hover:bg-red-100 dark:hover:bg-red-900/20"
            title="Delete"
          >
            <HiTrash className="w-4 h-4 text-red-500" />
          </button>
        </div>
      </div>
    </div>
  );
}

export function SlideList({
  slides,
  selectedId,
  onSelect,
  onAdd,
  onDelete,
  onReorder,
  onDuplicate,
}: SlideListProps) {
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      const oldIndex = slides.findIndex((s) => s.tempId === active.id);
      const newIndex = slides.findIndex((s) => s.tempId === over.id);
      const reordered = arrayMove(slides, oldIndex, newIndex).map((slide, index) => ({
        ...slide,
        order: index,
      }));
      onReorder(reordered);
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-50 dark:bg-gray-900/30">
      <div className="p-3 border-b border-gray-200 dark:border-gray-700">
        <button
          type="button"
          onClick={onAdd}
          className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors cursor-pointer"
        >
          + Add Slide
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {slides.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>No slides yet</p>
            <p className="text-sm mt-1">Click "Add Slide" to start</p>
          </div>
        ) : (
          <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
            <SortableContext items={slides.map((s) => s.tempId)} strategy={verticalListSortingStrategy}>
              {slides.map((slide, index) => (
                <SortableSlideItem
                  key={slide.tempId}
                  slide={slide}
                  index={index}
                  isSelected={selectedId === slide.tempId}
                  onSelect={() => onSelect(slide.tempId)}
                  onDelete={() => onDelete(slide.tempId)}
                  onDuplicate={() => onDuplicate(slide.tempId)}
                />
              ))}
            </SortableContext>
          </DndContext>
        )}
      </div>
    </div>
  );
}
