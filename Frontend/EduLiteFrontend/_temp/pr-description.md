# Refactor: Decompose SlideshowViewer into Custom Hooks

Closes #202

## Summary

Refactored the `SlideshowViewer` component from 643 lines with 13+ intertwined useState hooks into a cleaner architecture using 4 focused custom hooks. The component is now 450 lines (30% reduction) with clear separation of concerns.

## Changes

### New Hooks Created

| Hook | Lines | Purpose |
|------|-------|---------|
| `useSlideNavigation` | 80 | Manages slide index, next/prev/goToSlide with bounds checking |
| `useSlideLoader` | 168 | Handles API calls, progressive loading, metadata |
| `usePresentationMode` | 178 | Fullscreen API, auto-hide bars, localStorage persistence |
| `useKeyboardNavigation` | 138 | Keyboard shortcuts (arrows, space, N, F, Home/End, 1-9) |

### New Test Files

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `useSlideNavigation.test.ts` | 20 | Initialization, navigation, bounds, edge cases |
| `useSlideLoader.test.ts` | 16 | Loading states, errors, progressive loading |
| `usePresentationMode.test.ts` | 21 | Fullscreen, auto-hide, localStorage, mouse tracking |
| `useKeyboardNavigation.test.ts` | 21 | All keyboard shortcuts, enabled/disabled states |

### Modified Files

- `SlideshowViewer.tsx` - Now uses the 4 custom hooks instead of inline state management

## Before/After

**Before:**
```tsx
// 643 lines, 13+ useState hooks
const [currentIndex, setCurrentIndex] = useState(initialSlide);
const [slides, setSlides] = useState(new Map());
const [showNotes, setShowNotes] = useState(showNotesInitial);
const [isLoading, setIsLoading] = useState(true);
const [error, setError] = useState(null);
const [isFullscreen, setIsFullscreen] = useState(false);
// ... 7 more state variables
```

**After:**
```tsx
// 450 lines, clean separation of concerns
const { slides, slideCount, isLoading, error, metadata } = useSlideLoader(slideshowId);
const navigation = useSlideNavigation({ slideCount, initialSlide });
const presentation = usePresentationMode({ containerRef, showNotes, settingsOpen, helpOpen });

useKeyboardNavigation({
  onNext: navigation.next,
  onPrev: navigation.prev,
  onGoToSlide: navigation.goToSlide,
  onToggleNotes: toggleNotes,
  onToggleFullscreen: handleToggleFullscreen,
  onExit,
  slideCount,
  allowFullscreen,
});
```

## Benefits

1. **Clarity** - Each hook does one thing, easy to understand in isolation
2. **Testability** - Can unit test navigation logic without rendering the full component
3. **Reusability** - `useSlideNavigation` could be reused for carousels, image galleries, etc.
4. **Maintainability** - Bug in fullscreen? Look at `usePresentationMode`, not 600+ lines

## Testing

- All 488 existing tests pass
- 78 new unit tests for the custom hooks
- TypeScript compiles without errors
- Original `SlideshowViewer.test.tsx` unchanged and passing (proves external API preserved)

## Files Changed

**Created:**
- `src/hooks/useSlideNavigation.ts`
- `src/hooks/useSlideLoader.ts`
- `src/hooks/usePresentationMode.ts`
- `src/hooks/useKeyboardNavigation.ts`
- `src/hooks/__tests__/useSlideNavigation.test.ts`
- `src/hooks/__tests__/useSlideLoader.test.ts`
- `src/hooks/__tests__/usePresentationMode.test.ts`
- `src/hooks/__tests__/useKeyboardNavigation.test.ts`

**Modified:**
- `src/components/slideshow/SlideshowViewer.tsx`
