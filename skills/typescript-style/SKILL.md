---
name: TypeScript/JavaScript Style Best Practices
description: Automatic enforcement of TypeScript/JavaScript coding style, ESLint standards, type safety, and modern patterns
version: 1.0.0
triggers:
  - typescript
  - javascript
  - react
  - node
  - nextjs
  - jsx
  - tsx
  - eslint
  - prettier
---

# TypeScript/JavaScript Style Best Practices Skill

This skill automatically activates when writing TypeScript or JavaScript code to ensure consistency with modern standards, strict type safety, and best practices across frontend and Node.js projects.

## Core Principle

**TYPE-SAFE, CONSISTENT, MODERN JAVASCRIPT/TYPESCRIPT**

```
❌ Loose types, inconsistent style, legacy patterns
✅ Strict TypeScript, ESLint compliant, modern ES2024+
```

## Automatic Behaviors

When this skill activates, Claude will:

### 1. TypeScript Strict Mode

```typescript
// ═══════════════════════════════════════════════════════════
// tsconfig.json - STRICT CONFIGURATION
// ═══════════════════════════════════════════════════════════

{
  "compilerOptions": {
    // Strict Type Checking
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "useUnknownInCatchVariables": true,
    "alwaysStrict": true,

    // Additional Checks
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true,

    // Module Resolution
    "module": "ESNext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "esModuleInterop": true,
    "isolatedModules": true,

    // Output
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  }
}
```

### 2. Naming Conventions

```typescript
// ═══════════════════════════════════════════════════════════
// NAMING CONVENTIONS
// ═══════════════════════════════════════════════════════════

// Types and Interfaces: PascalCase
interface UserProfile {
  id: string;
  displayName: string;
}

type RequestHandler = (req: Request) => Promise<Response>;

// Classes: PascalCase
class UserService {
  private readonly repository: UserRepository;
}

// Functions and methods: camelCase
function calculateTotalPrice(items: CartItem[]): number {
  return items.reduce((sum, item) => sum + item.price, 0);
}

// Variables: camelCase
const userEmail = "user@example.com";
let isLoading = false;

// Constants: SCREAMING_SNAKE_CASE or camelCase (preference)
const MAX_RETRY_COUNT = 3;
const API_BASE_URL = "https://api.example.com";
// OR
const maxRetryCount = 3;
const apiBaseUrl = "https://api.example.com";

// ═══════════════════════════════════════════════════════════
// ENUMS vs UNION TYPES
// ═══════════════════════════════════════════════════════════
// RECOMMENDATION: Prefer union types over enums in most cases
//
// Why Union Types Win:
// - No runtime overhead (erased at compile time)
// - Better type safety (numeric enums accept any number)
// - Simpler interop with APIs (no casting needed)
//
// When Enums Make Sense:
// - Mapping numbers to readable labels (e.g., StatusCode.OK = 200)
// - When you need runtime iteration over all values
// - Comparing values by position

// ✅ PREFERRED: Union type (no runtime overhead)
type HttpStatus = 200 | 201 | 400 | 404 | 500;
type OrderStatus = "pending" | "processing" | "shipped" | "delivered";

// ✅ PREFERRED: `as const` object (dot notation + type safety)
const Status = {
  Active: "active",
  Inactive: "inactive",
  Pending: "pending",
} as const;

type Status = (typeof Status)[keyof typeof Status];
// Usage: Status.Active, Status.Inactive

// ⚠️ USE SPARINGLY: Enums (only when you need runtime iteration or number mapping)
enum HttpStatusCode {
  Ok = 200,
  Created = 201,
  BadRequest = 400,
  NotFound = 404,
}
// Note: Numeric enums accept ANY number, which can cause bugs

// React Components: PascalCase
function UserCard({ user }: UserCardProps) {
  return <div>{user.name}</div>;
}

// Custom Hooks: camelCase with "use" prefix
function useUserProfile(userId: string) {
  return useQuery({ queryKey: ['user', userId], queryFn: () => fetchUser(userId) });
}

// Event handlers: camelCase with "handle" or "on" prefix
const handleSubmit = (e: FormEvent) => { /* ... */ };
const onUserClick = (userId: string) => { /* ... */ };

// Boolean variables: camelCase with is/has/can/should prefix
const isAuthenticated = true;
const hasPermission = false;
const canEdit = true;
const shouldRefresh = false;

// Files: kebab-case for files, PascalCase for components
// user-service.ts
// UserCard.tsx
// use-user-profile.ts
// types.ts
```

### 3. Type Definitions

```typescript
// ═══════════════════════════════════════════════════════════
// TYPE DEFINITIONS BEST PRACTICES
// ═══════════════════════════════════════════════════════════

// Prefer `interface` for objects, `type` for unions/intersections
interface User {
  id: string;
  email: string;
  name: string;
  createdAt: Date;
}

// Use type for unions and mapped types
type Status = "pending" | "active" | "completed";
type UserWithRole = User & { role: string };

// Use readonly for immutable properties
interface Config {
  readonly apiUrl: string;
  readonly timeout: number;
}

// Use `as const` for literal types
const ROUTES = {
  home: "/",
  users: "/users",
  settings: "/settings",
} as const;

type Route = (typeof ROUTES)[keyof typeof ROUTES];

// Generic constraints
function first<T>(items: readonly T[]): T | undefined {
  return items[0];
}

// Utility types
type PartialUser = Partial<User>;
type RequiredUser = Required<User>;
type ReadonlyUser = Readonly<User>;
type UserKeys = keyof User;
type UserValues = User[keyof User];

// Conditional types
type ApiResponse<T> = T extends undefined
  ? { success: true }
  : { success: true; data: T };

// Template literal types
type EventName = `on${Capitalize<string>}`;

// Discriminated unions (prefer over type assertions)
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };

function processResult<T>(result: Result<T>): T {
  if (result.success) {
    return result.data;
  }
  throw result.error;
}

// Branded types for type-safe IDs
type UserId = string & { readonly __brand: "UserId" };
type OrderId = string & { readonly __brand: "OrderId" };

function createUserId(id: string): UserId {
  return id as UserId;
}
```

### 4. Function Patterns

```typescript
// ═══════════════════════════════════════════════════════════
// FUNCTION PATTERNS
// ═══════════════════════════════════════════════════════════

// Always type parameters and return values
function calculateDiscount(price: number, percent: number): number {
  return price * (1 - percent / 100);
}

// Use arrow functions for callbacks
const doubled = numbers.map((n) => n * 2);

// Use function declarations for hoisting and stack traces
function processOrder(order: Order): ProcessedOrder {
  // Implementation
}

// Optional parameters with defaults
function greet(name: string, greeting: string = "Hello"): string {
  return `${greeting}, ${name}!`;
}

// Rest parameters
function sum(...numbers: number[]): number {
  return numbers.reduce((a, b) => a + b, 0);
}

// Object parameters for many arguments
interface CreateUserOptions {
  email: string;
  name: string;
  role?: string;
  sendWelcomeEmail?: boolean;
}

function createUser({
  email,
  name,
  role = "user",
  sendWelcomeEmail = true,
}: CreateUserOptions): User {
  // Implementation
}

// Overloads for different signatures
function parseValue(value: string): string;
function parseValue(value: number): number;
function parseValue(value: string | number): string | number {
  return typeof value === "string" ? value.trim() : value;
}

// Generic functions
function identity<T>(value: T): T {
  return value;
}

// Async functions
async function fetchUser(userId: string): Promise<User> {
  const response = await fetch(`/api/users/${userId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch user: ${response.status}`);
  }
  return response.json();
}

// Higher-order functions
function withLogging<T extends (...args: unknown[]) => unknown>(
  fn: T,
  name: string
): T {
  return ((...args: Parameters<T>) => {
    console.log(`Calling ${name} with`, args);
    const result = fn(...args);
    console.log(`${name} returned`, result);
    return result;
  }) as T;
}
```

### 5. Error Handling

```typescript
// ═══════════════════════════════════════════════════════════
// ERROR HANDLING
// ═══════════════════════════════════════════════════════════

// Custom error classes
class AppError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode: number = 500
  ) {
    super(message);
    this.name = this.constructor.name;
    Error.captureStackTrace(this, this.constructor);
  }
}

class NotFoundError extends AppError {
  constructor(resource: string, id: string) {
    super(`${resource} not found: ${id}`, "NOT_FOUND", 404);
  }
}

class ValidationError extends AppError {
  constructor(
    message: string,
    public readonly field?: string
  ) {
    super(message, "VALIDATION_ERROR", 400);
  }
}

// Type guard for errors
function isAppError(error: unknown): error is AppError {
  return error instanceof AppError;
}

// Proper try-catch typing
async function safeOperation<T>(
  operation: () => Promise<T>
): Promise<Result<T>> {
  try {
    const data = await operation();
    return { success: true, data };
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    return { success: false, error: new Error(message) };
  }
}

// Never use `any` for caught errors
try {
  await riskyOperation();
} catch (error) {
  // ❌ Bad
  // console.log(error.message); // error is 'unknown'

  // ✅ Good
  if (error instanceof Error) {
    console.log(error.message);
  }
}

// Exhaustive error handling with never
function handleError(error: AppError): never {
  switch (error.code) {
    case "NOT_FOUND":
      // handle
      break;
    case "VALIDATION_ERROR":
      // handle
      break;
    default:
      // TypeScript will error if we miss a case
      const _exhaustive: never = error.code;
      throw new Error(`Unhandled error code: ${_exhaustive}`);
  }
  throw error;
}
```

### 6. React Patterns

```typescript
// ═══════════════════════════════════════════════════════════
// REACT TYPESCRIPT PATTERNS
// ═══════════════════════════════════════════════════════════

import { type ReactNode, type FC, useState, useCallback, useMemo } from "react";

// Component Props with children
interface CardProps {
  title: string;
  children: ReactNode;
  className?: string;
}

// Use function declaration for components
function Card({ title, children, className }: CardProps) {
  return (
    <div className={className}>
      <h2>{title}</h2>
      {children}
    </div>
  );
}

// Props with event handlers
interface ButtonProps {
  label: string;
  onClick: () => void;
  disabled?: boolean;
  variant?: "primary" | "secondary" | "danger";
}

function Button({
  label,
  onClick,
  disabled = false,
  variant = "primary",
}: ButtonProps) {
  return (
    <button onClick={onClick} disabled={disabled} data-variant={variant}>
      {label}
    </button>
  );
}

// Generic component
interface ListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => ReactNode;
  keyExtractor: (item: T) => string;
}

function List<T>({ items, renderItem, keyExtractor }: ListProps<T>) {
  return (
    <ul>
      {items.map((item, index) => (
        <li key={keyExtractor(item)}>{renderItem(item, index)}</li>
      ))}
    </ul>
  );
}

// Hooks with proper typing
function useCounter(initialValue: number = 0) {
  const [count, setCount] = useState(initialValue);

  const increment = useCallback(() => setCount((c) => c + 1), []);
  const decrement = useCallback(() => setCount((c) => c - 1), []);
  const reset = useCallback(() => setCount(initialValue), [initialValue]);

  return { count, increment, decrement, reset } as const;
}

// Context with proper typing
interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}

// Form event typing
function Form() {
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    // Process form
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    // Handle change
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="email" onChange={handleChange} />
    </form>
  );
}

// Ref typing
function InputWithFocus() {
  const inputRef = useRef<HTMLInputElement>(null);

  const focusInput = () => {
    inputRef.current?.focus();
  };

  return <input ref={inputRef} />;
}
```

### 7. Import/Export Patterns

```typescript
// ═══════════════════════════════════════════════════════════
// IMPORT/EXPORT PATTERNS
// ═══════════════════════════════════════════════════════════

// Named exports (preferred)
export function calculateTotal(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price, 0);
}

export interface User {
  id: string;
  name: string;
}

export type Status = "pending" | "active";

// Type-only imports (for types not used at runtime)
import type { User, Status } from "./types";
import { calculateTotal } from "./utils";

// Re-exports with type
export type { User } from "./types";
export { calculateTotal } from "./utils";

// Barrel exports (index.ts)
export * from "./user";
export * from "./order";
export type * from "./types";

// Default exports (use sparingly, mainly for React components)
export default function UserProfile() {
  return <div>Profile</div>;
}

// Import ordering (enforced by ESLint)
// 1. External packages
import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";

// 2. Internal absolute imports
import { Button } from "@/components/ui";
import { useAuth } from "@/hooks";

// 3. Relative imports
import { formatDate } from "../utils";
import type { UserProps } from "./types";

// 4. Side-effect imports
import "./styles.css";
```

### 8. Async/Await Patterns

```typescript
// ═══════════════════════════════════════════════════════════
// ASYNC PATTERNS
// ═══════════════════════════════════════════════════════════

// Always return Promise<T> for async functions
async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return response.json();
}

// Parallel execution
async function fetchDashboardData(): Promise<DashboardData> {
  const [user, orders, notifications] = await Promise.all([
    fetchUser(userId),
    fetchOrders(userId),
    fetchNotifications(userId),
  ]);

  return { user, orders, notifications };
}

// Sequential execution when order matters
async function processSequentially(items: Item[]): Promise<Result[]> {
  const results: Result[] = [];
  for (const item of items) {
    const result = await processItem(item);
    results.push(result);
  }
  return results;
}

// Error handling with Promise.allSettled
async function fetchMultipleUsers(
  ids: string[]
): Promise<Map<string, User | Error>> {
  const results = await Promise.allSettled(ids.map((id) => fetchUser(id)));

  return new Map(
    ids.map((id, index) => {
      const result = results[index];
      return [id, result.status === "fulfilled" ? result.value : result.reason];
    })
  );
}

// Timeout wrapper
async function withTimeout<T>(
  promise: Promise<T>,
  ms: number
): Promise<T> {
  const timeout = new Promise<never>((_, reject) =>
    setTimeout(() => reject(new Error("Timeout")), ms)
  );
  return Promise.race([promise, timeout]);
}

// Retry logic
async function withRetry<T>(
  fn: () => Promise<T>,
  retries: number = 3,
  delay: number = 1000
): Promise<T> {
  try {
    return await fn();
  } catch (error) {
    if (retries <= 0) throw error;
    await new Promise((r) => setTimeout(r, delay));
    return withRetry(fn, retries - 1, delay * 2);
  }
}

// Abort controller
async function fetchWithAbort(url: string, signal?: AbortSignal): Promise<Response> {
  return fetch(url, { signal });
}

// Usage with cleanup
function useData(url: string) {
  useEffect(() => {
    const controller = new AbortController();

    fetchWithAbort(url, controller.signal)
      .then(setData)
      .catch((e) => {
        if (e.name !== "AbortError") {
          setError(e);
        }
      });

    return () => controller.abort();
  }, [url]);
}
```

### 9. ESLint Configuration

```javascript
// ═══════════════════════════════════════════════════════════
// eslint.config.js (Flat Config - ESLint 9+)
// ═══════════════════════════════════════════════════════════

import eslint from "@eslint/js";
import tseslint from "typescript-eslint";
import react from "eslint-plugin-react";
import reactHooks from "eslint-plugin-react-hooks";
import importPlugin from "eslint-plugin-import";

export default tseslint.config(
  eslint.configs.recommended,
  ...tseslint.configs.strictTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,
  {
    languageOptions: {
      parserOptions: {
        project: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
    plugins: {
      react,
      "react-hooks": reactHooks,
      import: importPlugin,
    },
    rules: {
      // TypeScript
      "@typescript-eslint/explicit-function-return-type": "warn",
      "@typescript-eslint/no-unused-vars": [
        "error",
        { argsIgnorePattern: "^_" },
      ],
      "@typescript-eslint/no-explicit-any": "error",
      "@typescript-eslint/prefer-nullish-coalescing": "error",
      "@typescript-eslint/prefer-optional-chain": "error",
      "@typescript-eslint/strict-boolean-expressions": "error",
      "@typescript-eslint/no-floating-promises": "error",
      "@typescript-eslint/await-thenable": "error",
      "@typescript-eslint/no-misused-promises": "error",

      // React
      "react/jsx-key": "error",
      "react/jsx-no-target-blank": "error",
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "warn",

      // Import
      "import/order": [
        "error",
        {
          groups: [
            "builtin",
            "external",
            "internal",
            "parent",
            "sibling",
            "index",
          ],
          "newlines-between": "always",
          alphabetize: { order: "asc" },
        },
      ],
      "import/no-duplicates": "error",

      // General
      "no-console": ["warn", { allow: ["warn", "error"] }],
      eqeqeq: ["error", "always"],
      "prefer-const": "error",
    },
  },
  {
    files: ["**/*.test.ts", "**/*.test.tsx"],
    rules: {
      "@typescript-eslint/no-unsafe-assignment": "off",
    },
  }
);
```

### 10. Modern JavaScript Features

```typescript
// ═══════════════════════════════════════════════════════════
// MODERN JAVASCRIPT PATTERNS (ES2020+)
// ═══════════════════════════════════════════════════════════

// Optional chaining
const userName = user?.profile?.name ?? "Anonymous";

// Nullish coalescing
const count = data?.count ?? 0; // Only falls back for null/undefined
const value = input || "default"; // Falls back for all falsy values

// Logical assignment
user.name ??= "Anonymous"; // Assign if null/undefined
user.settings ||= defaultSettings; // Assign if falsy
user.permissions &&= filteredPermissions; // Assign if truthy

// Array methods
const unique = [...new Set(items)];
const grouped = Object.groupBy(users, (u) => u.role); // ES2024
const flattened = nested.flat(2);
const found = items.find((i) => i.id === id);
const included = items.includes(value);
const some = items.some((i) => i.active);
const every = items.every((i) => i.valid);

// Object methods
const entries = Object.entries(obj);
const fromEntries = Object.fromEntries(entries);
const keys = Object.keys(obj);
const values = Object.values(obj);
const hasOwn = Object.hasOwn(obj, "key"); // ES2022

// String methods
const trimmed = str.trim();
const padded = str.padStart(5, "0");
const replaced = str.replaceAll("old", "new");
const atIndex = str.at(-1); // Last character

// Destructuring
const { name, age = 0, ...rest } = user;
const [first, second, ...remaining] = items;
const { data: userData } = response; // Rename

// Spread
const merged = { ...defaults, ...overrides };
const combined = [...arr1, ...arr2];
const cloned = structuredClone(deepObject); // Deep clone

// Template literals
const message = `Hello, ${name}!`;
const multiline = `
  Line 1
  Line 2
`;

// Private class fields
class Service {
  #apiKey: string;
  static #instance: Service;

  constructor(apiKey: string) {
    this.#apiKey = apiKey;
  }
}

// Top-level await (ES modules)
const config = await loadConfig();
export { config };
```

### 11. Constants and Magic Values

```typescript
// ═══════════════════════════════════════════════════════════
// CONSTANTS: AVOID MAGIC NUMBERS AND STRINGS
// ═══════════════════════════════════════════════════════════

// RULE: Extract ALL magic values into named constants
// This improves readability, maintainability, and prevents bugs

// ❌ BAD: Magic numbers and strings
function calculateShipping(weight: number): number {
  if (weight > 50) {
    // What is 50?
    return weight * 2.5; // What is 2.5?
  }
  return 15.0; // What is 15.0?
}

if (retryCount > 3) {
  // Why 3?
  throw new TooManyRetriesError();
}

// ✅ GOOD: Named constants with clear meaning
const MAX_STANDARD_WEIGHT_KG = 50;
const HEAVY_PACKAGE_RATE_PER_KG = 2.5;
const STANDARD_SHIPPING_FEE = 15.0;
const MAX_RETRY_ATTEMPTS = 3;

function calculateShipping(weight: number): number {
  if (weight > MAX_STANDARD_WEIGHT_KG) {
    return weight * HEAVY_PACKAGE_RATE_PER_KG;
  }
  return STANDARD_SHIPPING_FEE;
}

if (retryCount > MAX_RETRY_ATTEMPTS) {
  throw new TooManyRetriesError();
}

// ═══════════════════════════════════════════════════════════
// GROUP RELATED CONSTANTS WITH `as const`
// ═══════════════════════════════════════════════════════════

// ✅ PREFERRED: Use `as const` objects for related constants
const HttpStatus = {
  Ok: 200,
  Created: 201,
  BadRequest: 400,
  Unauthorized: 401,
  NotFound: 404,
  InternalError: 500,
} as const;

type HttpStatus = (typeof HttpStatus)[keyof typeof HttpStatus];

const OrderStatus = {
  Pending: "pending",
  Processing: "processing",
  Shipped: "shipped",
  Delivered: "delivered",
  Cancelled: "cancelled",
} as const;

type OrderStatus = (typeof OrderStatus)[keyof typeof OrderStatus];

const Timeouts = {
  ApiRequest: 30_000, // Use numeric separators for readability
  DatabaseQuery: 10_000,
  CacheLookup: 5_000,
  FileUpload: 120_000,
} as const;

// ═══════════════════════════════════════════════════════════
// CONFIGURATION CONSTANTS
// ═══════════════════════════════════════════════════════════

// Application defaults
const DEFAULT_PAGE_SIZE = 20;
const MAX_PAGE_SIZE = 100;
const MIN_PASSWORD_LENGTH = 8;
const MAX_LOGIN_ATTEMPTS = 5;
const SESSION_TIMEOUT_MINUTES = 30;

// API endpoints (avoid string literals in code)
const ApiEndpoints = {
  Users: "/api/v1/users",
  Orders: "/api/v1/orders",
  Products: "/api/v1/products",
} as const;

// ═══════════════════════════════════════════════════════════
// REACT: Extract component-specific constants
// ═══════════════════════════════════════════════════════════

// ❌ BAD: Magic values in components
function DataTable() {
  const [pageSize, setPageSize] = useState(25);
  if (items.length > 1000) {
    // Magic numbers scattered
  }
}

// ✅ GOOD: Constants at module level or in config
const TABLE_CONFIG = {
  DefaultPageSize: 25,
  MaxDisplayRows: 1000,
  MinSearchLength: 3,
  DebounceMs: 300,
} as const;

function DataTable() {
  const [pageSize, setPageSize] = useState(TABLE_CONFIG.DefaultPageSize);
  if (items.length > TABLE_CONFIG.MaxDisplayRows) {
    // Clear meaning
  }
}
```

### 12. Expressive Naming

```typescript
// ═══════════════════════════════════════════════════════════
// EXPRESSIVE NAMING: CODE SHOULD READ LIKE PROSE
// ═══════════════════════════════════════════════════════════

// RULE: Names should clearly express INTENT and PURPOSE
// The name should answer: What is this? What does it do? Why?

// ═══════════════════════════════════════════════════════════
// VARIABLES: Name for WHAT it represents
// ═══════════════════════════════════════════════════════════

// ❌ BAD: Cryptic, abbreviated, or generic names
const d = getData();
const temp = process(d);
const x = temp[0];
let flag = true;
const arr: string[] = [];
const res = calc(a, b);

// ✅ GOOD: Descriptive names that explain purpose
const userProfile = getUserProfile(userId);
const validatedOrders = validateOrders(pendingOrders);
const primaryEmailAddress = userProfile.emails[0];
let isSubscriptionActive = true;
const unprocessedNotifications: Notification[] = [];
const totalDiscountAmount = calculateDiscount(subtotal, couponCode);

// ═══════════════════════════════════════════════════════════
// FUNCTIONS: Name for WHAT it does (verb + noun)
// ═══════════════════════════════════════════════════════════

// ❌ BAD: Vague or misleading function names
function process(data: unknown): void {} // Process how? What data?
function doStuff(x: number, y: number): void {} // What stuff?
function handle(item: Item): void {} // Handle how?
function getData(): unknown {} // What data? From where?

// ✅ GOOD: Action + target, describes transformation
function validateShippingAddress(address: Address): ValidatedAddress {
  // Validate address fields and normalize format
}

function calculateOrderTotalWithTax(order: Order, taxRate: number): number {
  // Calculate order total including applicable taxes
}

async function sendPasswordResetEmail(user: User): Promise<void> {
  // Send password reset link to user's email
}

async function fetchUserOrdersSince(
  userId: string,
  sinceDate: Date
): Promise<Order[]> {
  // Retrieve all user orders placed after the given date
}

// ═══════════════════════════════════════════════════════════
// BOOLEANS: Name as yes/no questions
// ═══════════════════════════════════════════════════════════

// ❌ BAD: Unclear boolean names
const active = true;
const status = false;
const check = true;
let valid = false;

// ✅ GOOD: Reads as a question that can be answered yes/no
const isUserActive = true;
const hasValidSubscription = false;
const canEditDocument = true;
let shouldSendNotification = false;
const wasPaymentSuccessful = true;
const isEmailVerified = false;

// React: Same pattern for state
const [isLoading, setIsLoading] = useState(false);
const [hasError, setHasError] = useState(false);
const [isModalOpen, setIsModalOpen] = useState(false);

// ═══════════════════════════════════════════════════════════
// COLLECTIONS: Name with plural nouns describing contents
// ═══════════════════════════════════════════════════════════

// ❌ BAD: Singular or vague collection names
const user: User[] = [];
const data: Record<string, number> = {};
const items = new Set<string>();

// ✅ GOOD: Clear plural nouns
const activeUsers: User[] = [];
const orderTotalsByCustomerId: Map<string, number> = new Map();
const uniqueProductCategories = new Set<string>();
const pendingNotificationIds: string[] = [];

// ═══════════════════════════════════════════════════════════
// EVENT HANDLERS: Clear action naming
// ═══════════════════════════════════════════════════════════

// ❌ BAD: Generic handler names
const click = () => {};
const change = () => {};
const submit = () => {};

// ✅ GOOD: handle + What + Action pattern
const handleFormSubmit = (e: FormEvent) => {};
const handleUserNameChange = (value: string) => {};
const handleDeleteButtonClick = () => {};
const handleModalClose = () => {};
const handleSearchInputChange = (query: string) => {};

// ═══════════════════════════════════════════════════════════
// AVOID ABBREVIATIONS (except widely known ones)
// ═══════════════════════════════════════════════════════════

// ❌ BAD: Unnecessary abbreviations
const usrNm = "John";
const btnClkCnt = 0;
const msgTxt = "";

// ✅ GOOD: Full words (or well-known abbreviations)
const userName = "John";
const buttonClickCount = 0;
const messageText = "";

// ✅ OK: Widely recognized abbreviations
const url = "https://...";
const httpClient = new HttpClient();
const jsonData = response.json();
const htmlContent = renderTemplate();
const apiResponse = await fetchApi();
const id = "user-123"; // Universally understood
const props = { name: "Component props" }; // React convention
```

### 13. Function Length Guidelines

```typescript
// ═══════════════════════════════════════════════════════════
// FUNCTION LENGTH RULES
// ═══════════════════════════════════════════════════════════

// RULE: Functions should be SHORT and focused on ONE task
//
// ✅ IDEAL: < 30 lines
//    Function is well-scoped, easy to test, easy to understand
//
// ⚠️ REVIEW (30-50 lines):
//    Function should be reviewed for potential refactoring
//    Ask: Can this be split into smaller, reusable functions?
//
// ❌ REFACTOR (> 50 lines):
//    Function MUST be broken down into smaller units
//    This is a code smell indicating too many responsibilities

// ❌ BAD: Monolithic function (> 50 lines)
async function processOrder(order: Order): Promise<ProcessedOrder> {
  // Validate order... (10 lines)
  // Check inventory... (15 lines)
  // Calculate totals... (12 lines)
  // Process payment... (18 lines)
  // Send notifications... (10 lines)
  // Update database... (8 lines)
  // Total: 73 lines - TOO LONG!
}

// ✅ GOOD: Decomposed into focused functions
async function processOrder(order: Order): Promise<ProcessedOrder> {
  const validatedOrder = validateOrder(order);
  const inventoryResult = await checkInventory(validatedOrder);
  const totals = calculateOrderTotals(validatedOrder, inventoryResult);
  const paymentResult = await processPayment(validatedOrder, totals);
  await sendOrderNotifications(validatedOrder, paymentResult);
  return saveProcessedOrder(validatedOrder, paymentResult);
}

function validateOrder(order: Order): ValidatedOrder {
  // 15 lines - focused on validation only
}

async function checkInventory(order: ValidatedOrder): Promise<InventoryResult> {
  // 12 lines - focused on inventory check
}

function calculateOrderTotals(
  order: ValidatedOrder,
  inventory: InventoryResult
): OrderTotals {
  // 18 lines - focused on calculations
}

// EXCEPTION: Some functions may legitimately exceed 30 lines:
// - Reducers with many action types
// - Complex switch statements
// - Functions with extensive error handling
// In these cases, add a comment explaining why

function orderReducer(state: OrderState, action: OrderAction): OrderState {
  /**
   * Note: This reducer exceeds 30 lines due to the number of
   * action types that must be handled in a single pure function.
   */
  switch (action.type) {
    // Many cases...
  }
}

// React components: Same rules apply
// ❌ BAD: Component with 80 lines of logic
function UserDashboard() {
  // Too much logic inline...
}

// ✅ GOOD: Extract logic into custom hooks and helper functions
function UserDashboard() {
  const { user, isLoading, error } = useUser();
  const { stats, refreshStats } = useUserStats(user?.id);
  const handleAction = useUserActions();

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <DashboardLayout>
      <UserHeader user={user} />
      <StatsPanel stats={stats} onRefresh={refreshStats} />
      <ActionButtons onAction={handleAction} />
    </DashboardLayout>
  );
}
```

## Style Checklist

```
📋 TypeScript/JavaScript Style Checklist

□ TYPE SAFETY
  □ Strict mode enabled in tsconfig
  □ No `any` types (use `unknown` if needed)
  □ All functions have explicit return types
  □ Null/undefined handled properly

□ NAMING
  □ PascalCase for types/interfaces/classes/components
  □ camelCase for functions/variables/methods
  □ SCREAMING_SNAKE_CASE for constants (optional)
  □ Boolean prefixes: is/has/can/should

□ IMPORTS
  □ Type-only imports for types
  □ Proper import ordering
  □ No circular dependencies
  □ Barrel exports for modules

□ ERROR HANDLING
  □ Custom error classes defined
  □ Unknown type for catch blocks
  □ Result types for operations
  □ Proper async error handling

□ REACT
  □ Typed props interfaces
  □ Typed event handlers
  □ Typed refs
  □ Typed context

□ MODERN FEATURES
  □ Optional chaining used
  □ Nullish coalescing used
  □ Const assertions where needed
  □ Template literals

□ FUNCTION LENGTH
  □ Functions under 30 lines (ideal)
  □ Functions 30-50 lines reviewed for refactoring
  □ No functions over 50 lines (or justified with comment)
  □ Each function has single responsibility
  □ React components use custom hooks for logic extraction

□ CONSTANTS & NAMING
  □ No magic numbers (use named constants)
  □ No magic strings (use `as const` objects)
  □ Variable names describe what they represent
  □ Function names describe what they do (verb + noun)
  □ Boolean names are yes/no questions (is/has/can/should)
  □ Collection names are descriptive plurals
  □ Event handlers use handle + What + Action pattern
  □ No unnecessary abbreviations
```

## Warning Triggers

Automatically warn user when:

1. **Using `any` type**
   > "⚠️ TS STYLE: Avoid `any`, use `unknown` or proper type"

2. **Missing return type**
   > "⚠️ TS STYLE: Add explicit return type to function"

3. **Using `==` instead of `===`**
   > "⚠️ TS STYLE: Use strict equality `===`"

4. **Unhandled promise**
   > "⚠️ TS STYLE: Add await or .catch() to Promise"

5. **Type assertion without guard**
   > "⚠️ TS STYLE: Use type guard instead of `as` assertion"

6. **Using enum instead of union type**
   > "⚠️ TS STYLE: Prefer union types or `as const` objects over enums for better type safety"

7. **Function exceeds 30 lines**
   > "⚠️ TS STYLE: Function has {n} lines - review for potential refactoring"

8. **Function exceeds 50 lines**
   > "🚨 TS STYLE: Function has {n} lines - MUST be broken down into smaller functions"

9. **Magic number detected**
   > "⚠️ TS STYLE: Extract magic number into named constant"

10. **Non-expressive variable name**
    > "⚠️ TS STYLE: Use descriptive name instead of `{name}` - names should express intent"

11. **Vague function name**
    > "⚠️ TS STYLE: Function name should describe what it does (e.g., `process` → `validateUserInput`)"

## Integration with Other Agents

This skill applies to TypeScript/JavaScript agents:
- **React TypeScript Expert**: React-specific patterns
- **Playwright Testing Expert**: Test patterns
- **UI Product Expert**: Component patterns
