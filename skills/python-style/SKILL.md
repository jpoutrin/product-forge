---
name: Python Style Best Practices
description: Automatic enforcement of Python coding style, PEP standards, type hints, and modern Python patterns
version: 1.0.0
triggers:
  - python
  - django
  - fastapi
  - celery
  - pytest
  - pydantic
  - async
  - type hints
---

# Python Style Best Practices Skill

This skill automatically activates when writing Python code to ensure consistency with PEP standards, type hints, and modern Python idioms across all Python agents.

## Core Principle

**CONSISTENT, READABLE, TYPE-SAFE PYTHON**

```
❌ Inconsistent style, missing types, legacy patterns
✅ PEP 8 compliant, fully typed, modern Python 3.11+
```

## Automatic Behaviors

When this skill activates, Claude will:

### 1. Code Style Standards

```python
# ═══════════════════════════════════════════════════════════
# NAMING CONVENTIONS (PEP 8)
# ═══════════════════════════════════════════════════════════

# Classes: PascalCase
class UserAccount:
    pass

class HTTPClientFactory:  # Acronyms capitalized
    pass

# Functions and variables: snake_case
def calculate_total_price():
    pass

user_name = "john"
total_count = 42

# Constants: SCREAMING_SNAKE_CASE
MAX_RETRY_COUNT = 3
DEFAULT_TIMEOUT_SECONDS = 30
API_BASE_URL = "https://api.example.com"

# Private: single underscore prefix
def _internal_helper():
    pass

_cached_value = None

# Name mangling (rarely needed): double underscore
class Parent:
    def __init__(self):
        self.__private_attr = "private"

# Module-level dunder: __all__, __version__
__all__ = ["UserAccount", "calculate_total_price"]
__version__ = "1.0.0"
```

### 2. Type Hints (PEP 484, 585, 604)

```python
# ═══════════════════════════════════════════════════════════
# MODERN TYPE HINTS (Python 3.10+)
# ═══════════════════════════════════════════════════════════

from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any, TypeVar, TypeAlias, ParamSpec

# Basic types (use built-in generics, not typing module)
def process_items(items: list[str]) -> dict[str, int]:
    return {item: len(item) for item in items}

# Optional (use | None instead of Optional)
def find_user(user_id: str) -> User | None:
    pass

# Union types (use | instead of Union)
def parse_value(value: str | int | float) -> str:
    return str(value)

# Type aliases
UserId: TypeAlias = str
UserMap: TypeAlias = dict[UserId, User]

# Generics
T = TypeVar("T")
P = ParamSpec("P")

def first_or_default(items: Sequence[T], default: T) -> T:
    return items[0] if items else default

# Callable types
Handler: TypeAlias = Callable[[str, int], bool]

def with_retry(func: Callable[P, T]) -> Callable[P, T]:
    pass

# Self type (Python 3.11+)
from typing import Self

class Builder:
    def with_name(self, name: str) -> Self:
        self.name = name
        return self

# TypedDict for structured dicts
from typing import TypedDict, NotRequired

class UserData(TypedDict):
    id: str
    name: str
    email: str
    age: NotRequired[int]  # Optional key

# Literal types
from typing import Literal

Status: TypeAlias = Literal["pending", "active", "completed"]

def update_status(status: Status) -> None:
    pass

# Final (constants)
from typing import Final

MAX_SIZE: Final = 1000
```

### 3. Docstrings (Google Style)

```python
# ═══════════════════════════════════════════════════════════
# GOOGLE STYLE DOCSTRINGS
# ═══════════════════════════════════════════════════════════

def calculate_discount(
    price: float,
    discount_percent: float,
    *,
    min_price: float = 0.0,
) -> float:
    """Calculate discounted price with optional minimum.

    Applies a percentage discount to the given price, ensuring
    the result doesn't fall below the specified minimum.

    Args:
        price: Original price before discount.
        discount_percent: Discount percentage (0-100).
        min_price: Minimum allowed price after discount.

    Returns:
        The discounted price, not less than min_price.

    Raises:
        ValueError: If price is negative or discount_percent
            is not between 0 and 100.

    Examples:
        >>> calculate_discount(100.0, 20.0)
        80.0
        >>> calculate_discount(100.0, 90.0, min_price=20.0)
        20.0
    """
    if price < 0:
        raise ValueError("Price must be non-negative")
    if not 0 <= discount_percent <= 100:
        raise ValueError("Discount must be between 0 and 100")

    discounted = price * (1 - discount_percent / 100)
    return max(discounted, min_price)


class OrderProcessor:
    """Processes customer orders through the fulfillment pipeline.

    This class handles the complete order lifecycle from validation
    through shipping notification.

    Attributes:
        warehouse: The warehouse service for inventory checks.
        payment: The payment processing service.
        notify: The notification service for customer updates.

    Example:
        >>> processor = OrderProcessor(warehouse, payment, notify)
        >>> processor.process(order)
        ProcessingResult(status='completed', order_id='ORD-123')
    """

    def __init__(
        self,
        warehouse: WarehouseService,
        payment: PaymentService,
        notify: NotificationService,
    ) -> None:
        """Initialize the order processor with required services.

        Args:
            warehouse: Service for inventory management.
            payment: Service for payment processing.
            notify: Service for customer notifications.
        """
        self.warehouse = warehouse
        self.payment = payment
        self.notify = notify
```

### 4. Import Organization

```python
# ═══════════════════════════════════════════════════════════
# IMPORT ORGANIZATION (isort compatible)
# ═══════════════════════════════════════════════════════════

# 1. Standard library imports (alphabetical)
import asyncio
import json
import logging
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, TypeVar

# 2. Third-party imports (alphabetical)
import httpx
import structlog
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# 3. Local application imports (alphabetical)
from app.config import settings
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.services import UserService

# Avoid:
# - `from module import *`
# - Relative imports in applications (ok in packages)
# - Circular imports
```

### 5. Dataclasses and Pydantic

```python
# ═══════════════════════════════════════════════════════════
# DATACLASSES (Python 3.10+)
# ═══════════════════════════════════════════════════════════

from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class User:
    """User entity with automatic __init__, __repr__, __eq__."""
    id: str
    email: str
    name: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True

    def __post_init__(self) -> None:
        """Validate email format after initialization."""
        if "@" not in self.email:
            raise ValueError(f"Invalid email: {self.email}")


@dataclass(frozen=True)
class Coordinate:
    """Immutable coordinate (hashable, can be dict key)."""
    x: float
    y: float

    def distance_to(self, other: "Coordinate") -> float:
        """Calculate Euclidean distance to another coordinate."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


@dataclass(slots=True)
class Point:
    """Memory-efficient point using __slots__."""
    x: float
    y: float


# ═══════════════════════════════════════════════════════════
# PYDANTIC V2 MODELS
# ═══════════════════════════════════════════════════════════

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic import ConfigDict

class UserCreate(BaseModel):
    """Schema for creating a new user."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        str_min_length=1,
    )

    email: str = Field(..., examples=["user@example.com"])
    name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v.lower()


class UserResponse(BaseModel):
    """Schema for user API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    name: str
    created_at: datetime
    is_active: bool
```

### 6. Async/Await Patterns

```python
# ═══════════════════════════════════════════════════════════
# ASYNC PATTERNS
# ═══════════════════════════════════════════════════════════

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

# Async function
async def fetch_user(user_id: str) -> User | None:
    """Fetch user from database asynchronously."""
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()


# Async context manager
@asynccontextmanager
async def get_client() -> AsyncIterator[httpx.AsyncClient]:
    """Provide an async HTTP client with automatic cleanup."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        yield client


# Concurrent execution
async def fetch_all_users(user_ids: list[str]) -> list[User]:
    """Fetch multiple users concurrently."""
    tasks = [fetch_user(uid) for uid in user_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    users = []
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"Failed to fetch user: {result}")
        elif result is not None:
            users.append(result)
    return users


# Async generator
async def stream_events() -> AsyncIterator[Event]:
    """Stream events from message queue."""
    async for message in queue.subscribe():
        event = Event.from_message(message)
        yield event


# Timeout handling
async def fetch_with_timeout(url: str, timeout: float = 5.0) -> str:
    """Fetch URL with timeout."""
    try:
        async with asyncio.timeout(timeout):
            async with get_client() as client:
                response = await client.get(url)
                return response.text
    except asyncio.TimeoutError:
        raise TimeoutError(f"Request to {url} timed out")
```

### 7. Error Handling

```python
# ═══════════════════════════════════════════════════════════
# ERROR HANDLING
# ═══════════════════════════════════════════════════════════

# Custom exceptions with inheritance
class AppError(Exception):
    """Base exception for application errors."""
    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        self.code = code


class ValidationError(AppError):
    """Raised when input validation fails."""
    pass


class NotFoundError(AppError):
    """Raised when a resource is not found."""
    pass


class AuthenticationError(AppError):
    """Raised when authentication fails."""
    pass


# Proper exception handling
async def get_user_or_404(user_id: str) -> User:
    """Fetch user or raise NotFoundError."""
    user = await fetch_user(user_id)
    if user is None:
        raise NotFoundError(f"User not found: {user_id}", code="USER_NOT_FOUND")
    return user


# Context-specific handling
def process_file(path: Path) -> str:
    """Process file with proper error handling."""
    try:
        content = path.read_text()
    except FileNotFoundError:
        raise NotFoundError(f"File not found: {path}")
    except PermissionError:
        raise AppError(f"Permission denied: {path}", code="PERMISSION_DENIED")
    except OSError as e:
        raise AppError(f"Failed to read file: {e}", code="FILE_ERROR")

    return process_content(content)


# Avoid bare except
# ❌ Bad
try:
    risky_operation()
except:  # Catches everything including KeyboardInterrupt
    pass

# ✅ Good
try:
    risky_operation()
except Exception as e:
    logger.exception("Operation failed")
    raise
```

### 8. Context Managers

```python
# ═══════════════════════════════════════════════════════════
# CONTEXT MANAGERS
# ═══════════════════════════════════════════════════════════

from contextlib import contextmanager, asynccontextmanager
from collections.abc import Iterator, AsyncIterator

# Class-based context manager
class DatabaseTransaction:
    """Context manager for database transactions."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def __enter__(self) -> Session:
        return self.session

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        if exc_type is not None:
            self.session.rollback()
            return False  # Re-raise exception
        self.session.commit()
        return False


# Generator-based context manager
@contextmanager
def timer(name: str) -> Iterator[None]:
    """Context manager to time code blocks."""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        logger.info(f"{name} took {elapsed:.3f}s")


# Async context manager
@asynccontextmanager
async def acquire_lock(key: str, timeout: float = 10.0) -> AsyncIterator[bool]:
    """Acquire distributed lock with automatic release."""
    lock = await redis.lock(key, timeout=timeout)
    acquired = await lock.acquire()
    try:
        yield acquired
    finally:
        if acquired:
            await lock.release()


# Usage
with timer("database_query"):
    results = db.query(...)

async with acquire_lock("process_order") as locked:
    if locked:
        await process_order(order)
```

### 9. Logging Best Practices

```python
# ═══════════════════════════════════════════════════════════
# STRUCTURED LOGGING
# ═══════════════════════════════════════════════════════════

import logging
import structlog

# Configure structlog for structured output
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Structured logging with context
async def process_order(order: Order) -> None:
    """Process order with structured logging."""
    log = logger.bind(order_id=order.id, customer_id=order.customer_id)

    log.info("processing_order_started")

    try:
        result = await payment_service.charge(order)
        log.info(
            "payment_processed",
            amount=order.total,
            transaction_id=result.transaction_id,
        )
    except PaymentError as e:
        log.error(
            "payment_failed",
            error=str(e),
            error_code=e.code,
        )
        raise

    log.info("processing_order_completed", status="success")


# Avoid
# ❌ Bad: String formatting in log calls
logger.info(f"Processing order {order.id}")
logger.info("Processing order %s" % order.id)

# ✅ Good: Structured data
logger.info("processing_order", order_id=order.id)
```

### 10. Configuration with pyproject.toml

```toml
# ═══════════════════════════════════════════════════════════
# pyproject.toml CONFIGURATION
# ═══════════════════════════════════════════════════════════

[tool.ruff]
target-version = "py311"
line-length = 88
select = [
    "E",     # pycodestyle errors
    "W",     # pycodestyle warnings
    "F",     # pyflakes
    "I",     # isort
    "B",     # flake8-bugbear
    "C4",    # flake8-comprehensions
    "UP",    # pyupgrade
    "ARG",   # flake8-unused-arguments
    "SIM",   # flake8-simplify
    "TCH",   # flake8-type-checking
    "PTH",   # flake8-use-pathlib
    "ERA",   # eradicate (commented-out code)
    "RUF",   # Ruff-specific rules
]
ignore = [
    "E501",  # line too long (handled by formatter)
]

[tool.ruff.isort]
known-first-party = ["app"]
force-single-line = false
lines-after-imports = 2

[tool.ruff.per-file-ignores]
"tests/**/*.py" = ["ARG001"]  # Unused arguments in tests (fixtures)

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
disallow_incomplete_defs = true

[[tool.mypy.overrides]]
module = ["tests.*"]
disallow_untyped_defs = false

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = "-ra -q --strict-markers"

[tool.coverage.run]
source = ["app"]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
```

### 11. Constants and Magic Values

```python
# ═══════════════════════════════════════════════════════════
# CONSTANTS: AVOID MAGIC NUMBERS AND STRINGS
# ═══════════════════════════════════════════════════════════

# RULE: Extract ALL magic values into named constants
# This improves readability, maintainability, and prevents bugs

# ❌ BAD: Magic numbers and strings
def calculate_shipping(weight: float) -> float:
    if weight > 50:  # What is 50?
        return weight * 2.5  # What is 2.5?
    return 15.0  # What is 15.0?

def check_status(code: int) -> bool:
    return code == 200  # What does 200 mean here?

if retry_count > 3:  # Why 3?
    raise TooManyRetriesError()

# ✅ GOOD: Named constants with clear meaning
MAX_STANDARD_WEIGHT_KG = 50
HEAVY_PACKAGE_RATE_PER_KG = 2.5
STANDARD_SHIPPING_FEE = 15.0
MAX_RETRY_ATTEMPTS = 3
HTTP_STATUS_OK = 200

def calculate_shipping(weight: float) -> float:
    if weight > MAX_STANDARD_WEIGHT_KG:
        return weight * HEAVY_PACKAGE_RATE_PER_KG
    return STANDARD_SHIPPING_FEE

def check_status(code: int) -> bool:
    return code == HTTP_STATUS_OK

if retry_count > MAX_RETRY_ATTEMPTS:
    raise TooManyRetriesError()


# ═══════════════════════════════════════════════════════════
# GROUP RELATED CONSTANTS
# ═══════════════════════════════════════════════════════════

# For related constants, use a class or module
class HttpStatus:
    """HTTP status codes."""
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    NOT_FOUND = 404
    INTERNAL_ERROR = 500


class OrderStatus:
    """Order processing status values."""
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Timeouts:
    """Timeout values in seconds."""
    API_REQUEST = 30
    DATABASE_QUERY = 10
    CACHE_LOOKUP = 5
    FILE_UPLOAD = 120


# ═══════════════════════════════════════════════════════════
# CONFIGURATION CONSTANTS
# ═══════════════════════════════════════════════════════════

# Use environment-aware configuration
from typing import Final

# Application defaults
DEFAULT_PAGE_SIZE: Final = 20
MAX_PAGE_SIZE: Final = 100
MIN_PASSWORD_LENGTH: Final = 8
MAX_LOGIN_ATTEMPTS: Final = 5
SESSION_TIMEOUT_MINUTES: Final = 30

# Feature flags as constants
FEATURE_NEW_CHECKOUT: Final = True
FEATURE_DARK_MODE: Final = False
```

### 12. Expressive Naming

```python
# ═══════════════════════════════════════════════════════════
# EXPRESSIVE NAMING: CODE SHOULD READ LIKE PROSE
# ═══════════════════════════════════════════════════════════

# RULE: Names should clearly express INTENT and PURPOSE
# The name should answer: What is this? What does it do? Why?

# ═══════════════════════════════════════════════════════════
# VARIABLES: Name for WHAT it represents
# ═══════════════════════════════════════════════════════════

# ❌ BAD: Cryptic, abbreviated, or generic names
d = get_data()
temp = process(d)
x = temp[0]
flag = True
lst = []
res = calc(a, b)

# ✅ GOOD: Descriptive names that explain purpose
user_profile = get_user_profile(user_id)
validated_orders = validate_orders(pending_orders)
primary_email_address = user_profile.emails[0]
is_subscription_active = True
unprocessed_notifications = []
total_discount_amount = calculate_discount(subtotal, coupon_code)


# ═══════════════════════════════════════════════════════════
# FUNCTIONS: Name for WHAT it does (verb + noun)
# ═══════════════════════════════════════════════════════════

# ❌ BAD: Vague or misleading function names
def process(data):  # Process how? What data?
    pass

def do_stuff(x, y):  # What stuff?
    pass

def handle(item):  # Handle how?
    pass

def get_data():  # What data? From where?
    pass

# ✅ GOOD: Action + target, describes transformation
def validate_shipping_address(address: Address) -> ValidatedAddress:
    """Validate address fields and normalize format."""
    pass

def calculate_order_total_with_tax(order: Order, tax_rate: float) -> Decimal:
    """Calculate order total including applicable taxes."""
    pass

def send_password_reset_email(user: User) -> None:
    """Send password reset link to user's email."""
    pass

def fetch_user_orders_since(user_id: str, since_date: date) -> list[Order]:
    """Retrieve all user orders placed after the given date."""
    pass


# ═══════════════════════════════════════════════════════════
# BOOLEANS: Name as yes/no questions
# ═══════════════════════════════════════════════════════════

# ❌ BAD: Unclear boolean names
active = True
status = False
check = True
valid = False

# ✅ GOOD: Reads as a question that can be answered yes/no
is_user_active = True
has_valid_subscription = False
can_edit_document = True
should_send_notification = False
was_payment_successful = True
is_email_verified = False


# ═══════════════════════════════════════════════════════════
# COLLECTIONS: Name with plural nouns describing contents
# ═══════════════════════════════════════════════════════════

# ❌ BAD: Singular or vague collection names
user = []
data = {}
items = set()

# ✅ GOOD: Clear plural nouns
active_users: list[User] = []
order_totals_by_customer_id: dict[str, Decimal] = {}
unique_product_categories: set[str] = set()
pending_notification_ids: list[str] = []


# ═══════════════════════════════════════════════════════════
# AVOID ABBREVIATIONS (except widely known ones)
# ═══════════════════════════════════════════════════════════

# ❌ BAD: Unnecessary abbreviations
usr_nm = "John"
btn_clk_cnt = 0
msg_txt = ""
calc_ttl = calculate_total

# ✅ GOOD: Full words (or well-known abbreviations)
user_name = "John"
button_click_count = 0
message_text = ""
calculate_total = calculate_total

# ✅ OK: Widely recognized abbreviations
url = "https://..."
http_client = httpx.Client()
json_data = response.json()
html_content = render_template()
api_response = fetch_api()
id = "user-123"  # Universally understood
```

### 13. Function Length Guidelines

```python
# ═══════════════════════════════════════════════════════════
# FUNCTION LENGTH RULES
# ═══════════════════════════════════════════════════════════

# RULE: Functions should be SHORT and focused on ONE task
#
# ✅ IDEAL: < 30 lines
#    Function is well-scoped, easy to test, easy to understand
#
# ⚠️ REVIEW (30-50 lines):
#    Function should be reviewed for potential refactoring
#    Ask: Can this be split into smaller, reusable functions?
#
# ❌ REFACTOR (> 50 lines):
#    Function MUST be broken down into smaller units
#    This is a code smell indicating too many responsibilities

# ❌ BAD: Monolithic function (> 50 lines)
def process_order(order: Order) -> ProcessedOrder:
    """This function does too many things."""
    # Validate order... (10 lines)
    # Check inventory... (15 lines)
    # Calculate totals... (12 lines)
    # Process payment... (18 lines)
    # Send notifications... (10 lines)
    # Update database... (8 lines)
    # Total: 73 lines - TOO LONG!
    pass


# ✅ GOOD: Decomposed into focused functions
def process_order(order: Order) -> ProcessedOrder:
    """Orchestrate order processing through focused steps."""
    validated_order = validate_order(order)
    inventory_result = check_inventory(validated_order)
    totals = calculate_order_totals(validated_order, inventory_result)
    payment_result = process_payment(validated_order, totals)
    await send_order_notifications(validated_order, payment_result)
    return save_processed_order(validated_order, payment_result)


def validate_order(order: Order) -> ValidatedOrder:
    """Validate order data and business rules."""
    # 15 lines - focused on validation only
    pass


def check_inventory(order: ValidatedOrder) -> InventoryResult:
    """Check product availability in warehouse."""
    # 12 lines - focused on inventory check
    pass


def calculate_order_totals(
    order: ValidatedOrder,
    inventory: InventoryResult,
) -> OrderTotals:
    """Calculate subtotal, tax, shipping, and total."""
    # 18 lines - focused on calculations
    pass


# EXCEPTION: Some functions may legitimately exceed 30 lines:
# - Complex state machines with many cases
# - Functions with extensive error handling
# - Database migrations
# In these cases, add a comment explaining why

def complex_state_handler(event: Event) -> State:
    """Handle state transitions for order lifecycle.

    Note: This function exceeds 30 lines due to the number of
    state transitions that must be handled atomically.
    """
    # Justified longer function...
    pass
```

## Style Checklist

```
📋 Python Style Checklist

□ NAMING
  □ Classes use PascalCase
  □ Functions/variables use snake_case
  □ Constants use SCREAMING_SNAKE_CASE
  □ Private members prefixed with _

□ TYPE HINTS
  □ All function parameters typed
  □ All return types specified
  □ Using modern syntax (| for Union, list[] not List)
  □ Complex types have TypeAlias

□ DOCSTRINGS
  □ All public functions documented
  □ Google style format used
  □ Args, Returns, Raises sections present
  □ Examples included where helpful

□ IMPORTS
  □ Organized: stdlib → third-party → local
  □ Alphabetically sorted within groups
  □ No wildcard imports
  □ No circular imports

□ ERROR HANDLING
  □ Custom exceptions defined
  □ Specific exceptions caught
  □ No bare except clauses
  □ Errors logged with context

□ ASYNC
  □ Async functions properly awaited
  □ Context managers used for resources
  □ Timeouts specified
  □ Concurrent tasks use gather()

□ FUNCTION LENGTH
  □ Functions under 30 lines (ideal)
  □ Functions 30-50 lines reviewed for refactoring
  □ No functions over 50 lines (or justified with comment)
  □ Each function has single responsibility

□ CONSTANTS & NAMING
  □ No magic numbers (use named constants)
  □ No magic strings (use constants or enums)
  □ Variable names describe what they represent
  □ Function names describe what they do (verb + noun)
  □ Boolean names are yes/no questions (is/has/can/should)
  □ Collection names are descriptive plurals
  □ No unnecessary abbreviations
```

## Warning Triggers

Automatically warn user when:

1. **Missing type hints**
   > "⚠️ PYTHON STYLE: Add type hints for function parameters and return type"

2. **Legacy type syntax**
   > "⚠️ PYTHON STYLE: Use `list[str]` instead of `List[str]` (Python 3.9+)"

3. **Missing docstring**
   > "⚠️ PYTHON STYLE: Add docstring for public function/class"

4. **Bare except clause**
   > "⚠️ PYTHON STYLE: Avoid bare `except:`, use `except Exception:` minimum"

5. **String formatting in logs**
   > "⚠️ PYTHON STYLE: Use structured logging: `logger.info('msg', key=value)`"

6. **Function exceeds 30 lines**
   > "⚠️ PYTHON STYLE: Function has {n} lines - review for potential refactoring"

7. **Function exceeds 50 lines**
   > "🚨 PYTHON STYLE: Function has {n} lines - MUST be broken down into smaller functions"

8. **Magic number detected**
   > "⚠️ PYTHON STYLE: Extract magic number into named constant"

9. **Non-expressive variable name**
   > "⚠️ PYTHON STYLE: Use descriptive name instead of `{name}` - names should express intent"

10. **Vague function name**
    > "⚠️ PYTHON STYLE: Function name should describe what it does (e.g., `process` → `validate_user_input`)"

## Integration with Other Agents

This skill applies to all Python agents:
- **Django Expert**: Django-specific Python patterns
- **FastAPI Expert**: Async Python patterns
- **FastMCP Expert**: MCP Python patterns
- **Celery Expert**: Task queue Python patterns
- **Python Testing Expert**: Test Python patterns
