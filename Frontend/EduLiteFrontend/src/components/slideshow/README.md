# Slideshow Viewer Component

A comprehensive presentation viewer built for EduLite with progressive loading, keyboard navigation, and offline capability. Designed for "present through a blackout" scenarios where network connectivity may be unreliable.

## Features

- ✨ **Progressive Loading**: Load first 3 slides immediately, fetch remaining in background
- ⌨️ **Keyboard Navigation**: Full keyboard control (arrows, space, escape, etc.)
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile
- 🌐 **Offline Capability**: Once loaded, works without network connection
- 🎨 **Dark Mode**: Presentation-friendly dark theme
- 📝 **Speaker Notes**: Toggleable notes panel for presenters
- 🖥️ **Fullscreen Support**: Optional fullscreen mode
- 🌍 **i18n Ready**: Full support for English and Arabic

## Installation

The component is already installed in the EduLite frontend. Simply import it:

```tsx
import { SlideshowViewer } from '@/components/slideshow';
```

## Basic Usage

```tsx
import { SlideshowViewer } from '@/components/slideshow';

function MyPage() {
  const handleExit = () => {
    navigate('/slideshows');
  };

  return (
    <SlideshowViewer
      slideshowId={5}
      onExit={handleExit}
    />
  );
}
```

## Advanced Usage

```tsx
<SlideshowViewer
  slideshowId={5}
  initialSlide={2}              // Start at slide 3 (0-indexed)
  showNotes={true}              // Show speaker notes by default
  allowFullscreen={true}        // Enable fullscreen button
  onExit={() => navigate('/slideshows')}
/>
```

## Props

### SlideshowViewer

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `slideshowId` | `number` | *required* | The ID of the slideshow to display |
| `initialSlide` | `number` | `0` | The index of the slide to start with (0-based) |
| `showNotes` | `boolean` | `false` | Whether to show speaker notes by default |
| `onExit` | `() => void` | `undefined` | Callback when user exits the viewer (e.g., via Escape key) |
| `allowFullscreen` | `boolean` | `false` | Whether to show the fullscreen toggle button |

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `→` or `Space` | Next slide |
| `←` or `Backspace` | Previous slide |
| `Escape` | Exit presentation (calls `onExit`) |
| `N` | Toggle speaker notes |
| `F` | Toggle fullscreen (if `allowFullscreen` is true) |
| `Home` | Jump to first slide |
| `End` | Jump to last slide |
| `1-9` | Jump to slide 1-9 |

## Progressive Loading Strategy

The viewer implements a smart loading strategy optimized for low-connectivity environments:

1. **Initial Load**: Fetches first 3 slides immediately via `getSlideshowDetail(id, 3)`
2. **Background Loading**: Fetches remaining slides in batches of 5 (parallel requests)
3. **Offline Ready**: Once all slides are loaded, the viewer works completely offline
4. **Loading Indicators**: Shows visual feedback for slides still being fetched

This approach ensures:
- Instant presentation start (first 3 slides ready immediately)
- Efficient bandwidth usage (parallel batch loading)
- "Blackout resilience" (all slides cached in memory after loading)

## Component Architecture

```
SlideshowViewer (Main Container)
├── SlideDisplay (Renders current slide)
├── SlideProgress (Progress indicator with dots/bar)
└── SpeakerNotes (Toggleable notes panel)
```

### SlideDisplay

Renders individual slide content with HTML from the backend.

**Props:**
- `slide`: The slide data (or null if loading)
- `isLoading`: Whether the slide is being fetched
- `slideNumber`: Current slide number (1-based)
- `totalSlides`: Total number of slides

### SlideProgress

Shows progress through the presentation with clickable navigation.

**Props:**
- `currentIndex`: Current slide index (0-based)
- `totalSlides`: Total number of slides
- `loadedSlides`: Array indicating which slides are loaded
- `onSlideClick`: Callback when a slide dot is clicked

**Behavior:**
- Shows individual dots for ≤20 slides
- Shows condensed progress bar for >20 slides

### SpeakerNotes

Toggleable panel displaying speaker notes for the current slide.

**Props:**
- `notes`: The notes content (or null)
- `isVisible`: Whether the panel is expanded
- `onToggle`: Callback to toggle visibility

## Styling

The component uses EduLite's design system:

- **Glass-morphism effects**: `backdrop-blur-xl` with semi-transparent backgrounds
- **Dark theme**: Presentation-friendly dark background (`bg-gray-900`)
- **Smooth transitions**: `transition-all duration-300 ease-out`
- **Responsive sizing**: Adapts to desktop, tablet, and mobile
- **Tailwind CSS**: All styling via utility classes

## HTML Rendering Security

Slides contain pre-rendered HTML from the backend (via Spellbook markdown processor). The component uses `dangerouslySetInnerHTML` to render this content:

```tsx
<div dangerouslySetInnerHTML={{ __html: slide.rendered_content }} />
```

**Security Notes:**
- Content is server-rendered and trusted
- Backend sanitizes markdown before rendering
- No user-provided HTML is directly rendered
- Follows React's security best practices

## Error Handling

The viewer gracefully handles errors:

```tsx
// Network errors
<SlideshowViewer slideshowId={999} onExit={() => navigate(-1)} />
// Shows: "Error Loading Slideshow" with go-back button

// 403 Forbidden
// Shows: "You don't have permission to view this slideshow"

// 404 Not Found
// Shows: "Slideshow not found"
```

## Testing

Comprehensive test suite included:

```bash
npm test -- slideshow
```

Test coverage includes:
- Component rendering
- Keyboard navigation
- Progressive loading logic
- Error states
- Accessibility
- User interactions

## i18n Support

All UI text is internationalized. Translation keys:

```json
{
  "slideshow": {
    "viewer": {
      "loading": "Loading presentation...",
      "slideOf": "Slide {{current}} of {{total}}",
      "speakerNotes": "Speaker Notes",
      "exitPresentation": "Exit",
      // ... more keys in en.json and ar.json
    }
  }
}
```

## Browser Support

- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Performance Considerations

- **Lazy Loading**: Slides fetched progressively
- **React.memo**: Child components memoized to prevent re-renders
- **Cleanup**: Event listeners properly removed on unmount
- **Debouncing**: Rapid keyboard navigation handled efficiently

## Accessibility

- ✅ Keyboard navigation
- ✅ ARIA labels on interactive elements
- ✅ Focus management
- ✅ Screen reader friendly
- ✅ Semantic HTML structure

## Future Enhancements

Potential v2 features (not in current scope):

- Touch/swipe gestures for mobile
- Slide thumbnails (currently just dots/numbers)
- Navigation persistence (localStorage)
- PDF export
- Presentation timer
- Laser pointer mode

## Contributing

When adding features:

1. Follow EduLite's TypeScript-first approach
2. Add comprehensive tests
3. Update i18n strings in both `en.json` and `ar.json`
4. Maintain accessibility standards
5. Keep the "offline-first" philosophy

## Related Issues

- [#196 - FRONTEND Slideshow Viewer Component](https://github.com/ibrahim-sisar/EduLite/issues/196)
- [#189 - TypeScript types and API service for slideshows](https://github.com/ibrahim-sisar/EduLite/pull/189) (merged)

## License

Part of the EduLite project - 100% open source, volunteer-driven.

---

**Built with ❤️ for students who just want to learn — no matter where they are.**
