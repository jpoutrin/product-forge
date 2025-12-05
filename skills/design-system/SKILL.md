---
name: Design System
description: Automatic design system management for building and reusing UI components, tokens, and patterns
version: 1.0.0
triggers:
  - design system
  - component library
  - ui components
  - design tokens
  - style guide
  - reusable components
  - atomic design
---

# Design System Skill

This skill automatically activates when working with design systems, component libraries, or reusable UI patterns. It ensures consistency and promotes component reuse across projects.

## Core Principle

**BUILD ONCE, USE EVERYWHERE**

```
❌ Duplicating UI code across components
✅ Building reusable, documented design system components
```

## Automatic Behaviors

When this skill activates, Claude will:

### 1. Identify Design System Opportunities

Automatically detect when code could benefit from design system patterns:

| Pattern | Detection | Recommendation |
|---------|-----------|----------------|
| Repeated styles | Same CSS in multiple places | Extract to design token |
| Similar components | Components with slight variations | Create variant system |
| Magic numbers | Hard-coded values (colors, spacing) | Replace with tokens |
| Inconsistent naming | Different names for same concept | Standardize naming |
| Missing documentation | Undocumented components | Add usage docs |

### 2. Design Token Architecture

```
DESIGN TOKEN STRUCTURE
════════════════════════════════════════════════════════════

PRIMITIVE TOKENS (Raw Values)
└── color.blue.500: "#3b82f6"
└── space.4: "16px"
└── font.size.base: "16px"

SEMANTIC TOKENS (Purpose-Based)
└── color.primary: "{color.blue.500}"
└── spacing.component: "{space.4}"
└── text.body: "{font.size.base}"

COMPONENT TOKENS (Component-Specific)
└── button.background: "{color.primary}"
└── button.padding: "{spacing.component}"
└── button.fontSize: "{text.body}"
```

### 3. Token File Structure

```json
// tokens/primitives.json
{
  "color": {
    "blue": {
      "50": { "value": "#eff6ff" },
      "100": { "value": "#dbeafe" },
      "500": { "value": "#3b82f6" },
      "600": { "value": "#2563eb" },
      "900": { "value": "#1e3a8a" }
    },
    "gray": {
      "50": { "value": "#f9fafb" },
      "500": { "value": "#6b7280" },
      "900": { "value": "#111827" }
    }
  },
  "space": {
    "0": { "value": "0" },
    "1": { "value": "4px" },
    "2": { "value": "8px" },
    "4": { "value": "16px" },
    "8": { "value": "32px" }
  },
  "fontSize": {
    "xs": { "value": "12px" },
    "sm": { "value": "14px" },
    "base": { "value": "16px" },
    "lg": { "value": "18px" },
    "xl": { "value": "20px" }
  }
}

// tokens/semantic.json
{
  "color": {
    "primary": { "value": "{color.blue.500}" },
    "primaryHover": { "value": "{color.blue.600}" },
    "background": { "value": "{color.gray.50}" },
    "text": { "value": "{color.gray.900}" },
    "textMuted": { "value": "{color.gray.500}" }
  },
  "spacing": {
    "xs": { "value": "{space.1}" },
    "sm": { "value": "{space.2}" },
    "md": { "value": "{space.4}" },
    "lg": { "value": "{space.8}" }
  }
}
```

### 4. Component Structure

```
COMPONENT ORGANIZATION
════════════════════════════════════════════════════════════

src/components/
├── atoms/                    # Smallest building blocks
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.styles.ts
│   │   ├── Button.types.ts
│   │   ├── Button.test.tsx
│   │   ├── Button.stories.tsx
│   │   └── index.ts
│   ├── Input/
│   ├── Icon/
│   └── Text/
│
├── molecules/                # Combinations of atoms
│   ├── FormField/
│   │   ├── FormField.tsx    # Label + Input + Error
│   │   └── ...
│   ├── SearchBox/
│   └── Card/
│
├── organisms/                # Complex UI sections
│   ├── Header/
│   ├── Sidebar/
│   ├── DataTable/
│   └── Modal/
│
├── templates/                # Page layouts
│   ├── DashboardLayout/
│   ├── AuthLayout/
│   └── SettingsLayout/
│
└── index.ts                  # Public exports
```

### 5. Component Template

```typescript
// components/atoms/Button/Button.types.ts
export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';
export type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
}


// components/atoms/Button/Button.tsx
import { forwardRef } from 'react';
import { clsx } from 'clsx';
import { ButtonProps } from './Button.types';
import styles from './Button.module.css';

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      isLoading = false,
      leftIcon,
      rightIcon,
      fullWidth = false,
      disabled,
      className,
      children,
      ...props
    },
    ref
  ) => {
    return (
      <button
        ref={ref}
        className={clsx(
          styles.button,
          styles[variant],
          styles[size],
          fullWidth && styles.fullWidth,
          isLoading && styles.loading,
          className
        )}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading ? (
          <span className={styles.spinner} aria-hidden="true" />
        ) : (
          leftIcon && <span className={styles.leftIcon}>{leftIcon}</span>
        )}
        <span className={styles.label}>{children}</span>
        {rightIcon && !isLoading && (
          <span className={styles.rightIcon}>{rightIcon}</span>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';


// components/atoms/Button/Button.module.css
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  font-weight: var(--font-weight-medium);
  border-radius: var(--radius-md);
  transition: all var(--duration-fast) var(--ease-out);
  cursor: pointer;
}

.button:focus-visible {
  outline: 2px solid var(--color-focus);
  outline-offset: 2px;
}

.button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Variants */
.primary {
  background: var(--color-primary);
  color: var(--color-text-inverse);
  border: none;
}

.primary:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.secondary {
  background: transparent;
  color: var(--color-primary);
  border: 1px solid var(--color-primary);
}

.secondary:hover:not(:disabled) {
  background: var(--color-primary-subtle);
}

.ghost {
  background: transparent;
  color: var(--color-text);
  border: none;
}

.ghost:hover:not(:disabled) {
  background: var(--color-surface-hover);
}

.danger {
  background: var(--color-error);
  color: var(--color-text-inverse);
  border: none;
}

/* Sizes */
.sm {
  height: 32px;
  padding: 0 var(--spacing-sm);
  font-size: var(--font-size-sm);
}

.md {
  height: 40px;
  padding: 0 var(--spacing-md);
  font-size: var(--font-size-base);
}

.lg {
  height: 48px;
  padding: 0 var(--spacing-lg);
  font-size: var(--font-size-lg);
}

/* States */
.fullWidth {
  width: 100%;
}

.loading {
  position: relative;
  color: transparent;
}

.spinner {
  position: absolute;
  width: 1em;
  height: 1em;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
```

### 6. Storybook Documentation

```typescript
// components/atoms/Button/Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';
import { PlusIcon, ArrowRightIcon } from '@heroicons/react/24/outline';

const meta: Meta<typeof Button> = {
  title: 'Atoms/Button',
  component: Button,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'Primary UI element for user actions.',
      },
    },
  },
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'ghost', 'danger'],
      description: 'Visual style variant',
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
      description: 'Button size',
    },
    isLoading: {
      control: 'boolean',
      description: 'Shows loading spinner',
    },
    fullWidth: {
      control: 'boolean',
      description: 'Expands to full container width',
    },
    disabled: {
      control: 'boolean',
      description: 'Disables interaction',
    },
  },
};

export default meta;
type Story = StoryObj<typeof Button>;

export const Primary: Story = {
  args: {
    children: 'Primary Button',
    variant: 'primary',
  },
};

export const Secondary: Story = {
  args: {
    children: 'Secondary Button',
    variant: 'secondary',
  },
};

export const Ghost: Story = {
  args: {
    children: 'Ghost Button',
    variant: 'ghost',
  },
};

export const Danger: Story = {
  args: {
    children: 'Delete',
    variant: 'danger',
  },
};

export const WithIcons: Story = {
  args: {
    children: 'Add Item',
    leftIcon: <PlusIcon className="w-4 h-4" />,
  },
};

export const IconRight: Story = {
  args: {
    children: 'Continue',
    rightIcon: <ArrowRightIcon className="w-4 h-4" />,
  },
};

export const Loading: Story = {
  args: {
    children: 'Saving...',
    isLoading: true,
  },
};

export const Sizes: Story = {
  render: () => (
    <div className="flex items-center gap-4">
      <Button size="sm">Small</Button>
      <Button size="md">Medium</Button>
      <Button size="lg">Large</Button>
    </div>
  ),
};

export const AllVariants: Story = {
  render: () => (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-4">
        <Button variant="primary">Primary</Button>
        <Button variant="secondary">Secondary</Button>
        <Button variant="ghost">Ghost</Button>
        <Button variant="danger">Danger</Button>
      </div>
      <div className="flex items-center gap-4">
        <Button variant="primary" disabled>Disabled</Button>
        <Button variant="primary" isLoading>Loading</Button>
      </div>
    </div>
  ),
};
```

### 7. Component Composition Patterns

```typescript
// Compound Components Pattern
// components/molecules/Card/Card.tsx
import { createContext, useContext, ReactNode } from 'react';

interface CardContextType {
  variant: 'default' | 'elevated' | 'outlined';
}

const CardContext = createContext<CardContextType | null>(null);

const useCardContext = () => {
  const context = useContext(CardContext);
  if (!context) throw new Error('Card components must be used within Card');
  return context;
};

interface CardProps {
  variant?: 'default' | 'elevated' | 'outlined';
  children: ReactNode;
  className?: string;
}

export const Card = ({ variant = 'default', children, className }: CardProps) => {
  return (
    <CardContext.Provider value={{ variant }}>
      <div className={clsx(styles.card, styles[variant], className)}>
        {children}
      </div>
    </CardContext.Provider>
  );
};

Card.Header = function CardHeader({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={clsx(styles.header, className)}>{children}</div>;
};

Card.Body = function CardBody({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={clsx(styles.body, className)}>{children}</div>;
};

Card.Footer = function CardFooter({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={clsx(styles.footer, className)}>{children}</div>;
};

Card.Title = function CardTitle({ children, className }: { children: ReactNode; className?: string }) {
  return <h3 className={clsx(styles.title, className)}>{children}</h3>;
};

Card.Description = function CardDescription({ children, className }: { children: ReactNode; className?: string }) {
  return <p className={clsx(styles.description, className)}>{children}</p>;
};

// Usage
<Card variant="elevated">
  <Card.Header>
    <Card.Title>Card Title</Card.Title>
    <Card.Description>Card description text</Card.Description>
  </Card.Header>
  <Card.Body>
    <p>Card content goes here</p>
  </Card.Body>
  <Card.Footer>
    <Button variant="ghost">Cancel</Button>
    <Button>Submit</Button>
  </Card.Footer>
</Card>
```

### 8. CSS Variables Integration

```css
/* styles/tokens.css */
:root {
  /* Colors */
  --color-primary: #3b82f6;
  --color-primary-hover: #2563eb;
  --color-primary-subtle: #eff6ff;

  --color-error: #ef4444;
  --color-success: #10b981;
  --color-warning: #f59e0b;

  --color-text: #111827;
  --color-text-muted: #6b7280;
  --color-text-inverse: #ffffff;

  --color-surface: #ffffff;
  --color-surface-hover: #f9fafb;
  --color-border: #e5e7eb;
  --color-focus: #3b82f6;

  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;

  /* Typography */
  --font-size-xs: 12px;
  --font-size-sm: 14px;
  --font-size-base: 16px;
  --font-size-lg: 18px;
  --font-size-xl: 20px;

  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;

  /* Borders */
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);

  /* Animation */
  --duration-fast: 150ms;
  --duration-normal: 200ms;
  --duration-slow: 300ms;
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
}

/* Dark mode tokens */
[data-theme="dark"] {
  --color-text: #f9fafb;
  --color-text-muted: #9ca3af;
  --color-text-inverse: #111827;

  --color-surface: #1f2937;
  --color-surface-hover: #374151;
  --color-border: #374151;
}
```

## Design System Checklist

```
📋 Design System Audit

□ TOKENS
  □ Color primitives defined
  □ Semantic color tokens exist
  □ Spacing scale consistent
  □ Typography scale defined
  □ Shadow/elevation scale exists

□ COMPONENTS
  □ Atomic structure followed
  □ Components are documented
  □ Storybook stories exist
  □ TypeScript types defined
  □ Accessibility tested

□ PATTERNS
  □ Layout patterns documented
  □ Form patterns standardized
  □ Error handling consistent
  □ Loading states defined

□ TOOLING
  □ Token generation automated
  □ Component scaffolding available
  □ Visual regression testing
  □ Accessibility linting

□ GOVERNANCE
  □ Contribution guidelines exist
  □ Versioning strategy defined
  □ Breaking change process
  □ Deprecation policy
```

## Warning Triggers

Automatically warn user when:

1. **Hard-coded values detected**
   > "⚠️ DESIGN SYSTEM: Consider replacing hard-coded value with design token"

2. **Duplicate styles found**
   > "⚠️ DESIGN SYSTEM: This style exists in [component]. Consider extracting to shared token"

3. **Missing documentation**
   > "⚠️ DESIGN SYSTEM: Component missing Storybook story or usage documentation"

4. **Inconsistent naming**
   > "⚠️ DESIGN SYSTEM: Naming pattern differs from existing components"

5. **Component too complex**
   > "⚠️ DESIGN SYSTEM: Consider breaking this into smaller atomic components"

## Integration with Other Agents

- **UI Product Expert**: Defines design tokens and visual specifications
- **React TypeScript Expert**: Implements design system components
- **Playwright Testing Expert**: Tests visual consistency
- **UX Expert**: Validates component usability
