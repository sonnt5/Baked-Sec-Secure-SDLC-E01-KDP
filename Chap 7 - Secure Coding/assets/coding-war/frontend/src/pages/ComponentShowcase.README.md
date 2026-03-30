# Component Showcase Page

## Overview

The ComponentShowcase page is an interactive demonstration of all base UI components in the Coding War frontend application. It serves as both a visual reference guide and a testing ground for the component library.

## Purpose

- **Visual Reference**: Developers can see all available components and their variants in one place
- **Interactive Testing**: Test component behavior, states, and interactions
- **Accessibility Verification**: Verify keyboard navigation, focus indicators, and ARIA labels
- **Code Examples**: View implementation code snippets for each component
- **Design Consistency**: Ensure all components follow the design system

## Features

### Component Categories

1. **Buttons**
   - Variants: Primary, Secondary, Danger, Ghost
   - Sizes: Small, Medium, Large
   - States: Default, Hover, Focus, Disabled

2. **Inputs**
   - States: Default, Error, Success, Disabled
   - Validation feedback with ARIA attributes
   - Accessible labels and error messages

3. **Modals**
   - Focus trap implementation
   - Keyboard navigation (ESC to close)
   - Click outside to close
   - Accessible dialog with ARIA roles

4. **Tables**
   - Responsive design
   - Sortable columns (hover states)
   - Semantic HTML structure
   - Mobile-friendly horizontal scroll

5. **Badges**
   - Status indicators (Accepted, Wrong Answer, Pending, etc.)
   - Difficulty levels (Easy, Medium, Hard)
   - Color-coded with dark mode support

6. **Cards**
   - Simple card layout
   - Card with badges
   - Card with actions
   - Responsive grid layout

7. **Dropdowns**
   - Keyboard navigation support
   - ARIA menu roles
   - Click outside to close
   - Accessible menu items

8. **Tabs**
   - Tab navigation with keyboard support
   - Active state indicators
   - ARIA current page attribute
   - Content switching

9. **Toast Notifications**
   - Success, Error, Info, Warning types
   - Color-coded with icons
   - Auto-dismiss capability (simulated)
   - Accessible announcements

10. **Skeleton Loaders**
    - Text content placeholders
    - Card loading states
    - Table loading states
    - User profile loading states
    - Animated pulse effect

## Accessibility Features

The showcase demonstrates the following accessibility features:

- ✓ **Keyboard Navigation**: All interactive elements are keyboard accessible (Tab, Enter, Escape, Arrow keys)
- ✓ **Focus Indicators**: Visible focus rings on all interactive elements
- ✓ **ARIA Labels**: Proper ARIA attributes for screen readers
- ✓ **Color Contrast**: WCAG 2.1 Level AA compliant (4.5:1 for text)
- ✓ **Semantic HTML**: Proper use of semantic elements (button, nav, table, etc.)
- ✓ **Focus Trap**: Modal implements focus trap to prevent focus escape
- ✓ **Error Messages**: Descriptive error messages linked to inputs via aria-describedby

## Usage

### Accessing the Showcase

1. Start the development server: `npm run dev`
2. Navigate to the home page
3. Click the "🎨 Component Showcase" button

### Testing Components

1. Use the top navigation tabs to switch between component categories
2. Interact with each component to test behavior
3. Test keyboard navigation using Tab, Enter, Escape, and Arrow keys
4. Verify focus indicators are visible
5. Review code snippets for implementation examples

### Code Snippets

Each component section includes a code snippet showing how to implement the component. These snippets demonstrate:
- Required CSS classes
- Accessibility attributes
- Event handlers
- State management

## Requirements Fulfilled

This component fulfills the following requirements from the spec:

- **20.2**: Keyboard navigation and focus management
- **20.3**: Screen reader compatibility with ARIA labels
- **20.7**: Visual feedback for interactive elements
- **20.8**: Error states and validation feedback
- **30.1**: WCAG 2.1 Level AA color contrast compliance

## Technical Implementation

### State Management

The page uses React's `useState` hook for:
- Active tab selection
- Modal open/close state
- Dropdown open/close state
- Tab content switching

### Styling

- **Tailwind CSS**: Utility-first CSS framework
- **Dark Mode**: Full dark mode support with `dark:` variants
- **Responsive Design**: Mobile-first responsive breakpoints
- **Animations**: Pulse animation for skeleton loaders

### Component Structure

```
ComponentShowcase
├── Navigation Tabs (category selection)
├── Component Sections (conditional rendering based on active tab)
│   ├── Buttons Section
│   ├── Inputs Section
│   ├── Modals Section
│   ├── Tables Section
│   ├── Badges Section
│   ├── Cards Section
│   ├── Dropdowns Section
│   ├── Tabs Section
│   ├── Toasts Section
│   └── Skeletons Section
└── Accessibility Features Summary
```

### Helper Components

- **ComponentSection**: Wrapper for each component category with title and description
- **CodeSnippet**: Displays formatted code examples
- **TabsExample**: Nested tabs component for demonstration

## Future Enhancements

Once the actual UI component library (task 1.3) is implemented, this showcase should be updated to:

1. Import and use the actual component implementations
2. Remove inline component examples
3. Add prop tables showing all available props
4. Add interactive prop controls (Storybook-style)
5. Add visual regression testing
6. Add component performance metrics

## Notes

- This showcase currently uses inline component examples since the actual UI component library hasn't been created yet
- The toast notification buttons show alerts instead of actual toasts (will be replaced when Toast component is implemented)
- All components follow the design system specified in the design document
- Dark mode is fully supported across all components
