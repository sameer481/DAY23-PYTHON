"""
================================================================================
Day 23: Python Object-Oriented Programming - Protocols vs. ABCs & Design Principles
================================================================================
Abstraction is not merely a syntax feature—it is the bedrock of robust software
architecture. Understanding HOW and WHEN to apply abstraction separates amateur
scripts from maintainable enterprise systems.

Key Concepts Covered in this Script:
1. Nominal Typing (`abc.ABC`) vs. Structural Typing (`typing.Protocol`, PEP 544)
2. `@runtime_checkable` Protocols: Static Duck Typing at Runtime
3. Comparative Decision Matrix: When to choose ABC vs. Protocol
4. Interface Segregation Principle (ISP): Deconstructing "Fat" Interfaces
5. Dependency Inversion Principle (DIP): Inversion of Control in Action
6. The Template Method Pattern: Invariant Algorithm Skeletons with Abstract Steps
7. The Law of Leaky Abstractions (Joel Spolsky): Building Resilient Abstractions
================================================================================
"""

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable, List, Dict, Any, Optional
import time


def print_separator(title: str) -> None:
    """Utility helper to print structured visual headers for each demonstration."""
    print("\n" + "=" * 78)
    print(f" {title}")
    print("=" * 78)


# ==============================================================================
# 1. NOMINAL TYPING (abc.ABC) VS. STRUCTURAL TYPING (typing.Protocol)
# ==============================================================================
# Python offers two modern paradigms for defining abstract interfaces:
#
# 1. Nominal Typing via `abc.ABC` (Named inheritance):
#    A class MUST explicitly inherit from the ABC (or be registered).
#    Enforced at instantiation time.
#
# 2. Structural Typing via `typing.Protocol` (Shape-based subtyping / PEP 544):
#    A class satisfies the protocol if it possesses the required methods/attributes.
#    NO inheritance required! Validated by static type checkers (mypy/pyright)
#    and at runtime when marked `@runtime_checkable`.

print_separator("1. Structural Typing with @runtime_checkable Protocols")

@runtime_checkable
class Renderable(Protocol):
    """Structural protocol: Any class with a render() -> str method satisfies this."""
    def render(self) -> str:
        ...


class MarkdownDocument:
    """Does NOT inherit from Renderable, yet fulfills its contract structurally!"""
    def __init__(self, content: str):
        self.content = content

    def render(self) -> str:
        return f"[MARKDOWN]\n# Document\n{self.content}"


class HtmlPage:
    """Another completely independent class fulfilling the contract."""
    def __init__(self, body: str):
        self.body = body

    def render(self) -> str:
        return f"<html><body>{self.body}</body></html>"


doc = MarkdownDocument("Welcome to Day 23 Abstraction Masterclass.")
page = HtmlPage("Hello World from HTML.")

print(f"isinstance(doc, Renderable)  : {isinstance(doc, Renderable)}  (No inheritance!)")
print(f"isinstance(page, Renderable) : {isinstance(page, Renderable)} (No inheritance!)")


# ==============================================================================
# 2. COMPARATIVE DECISION MATRIX: ABC VS. PROTOCOL
# ==============================================================================
# +------------------------+---------------------------------+---------------------------------+
# | Architectural Feature  | Abstract Base Class (abc.ABC)   | Protocol (typing.Protocol)      |
# +------------------------+---------------------------------+---------------------------------+
# | Typing Philosophy      | Nominal Subtyping (Explicit)    | Structural Subtyping (Duck)     |
# | Inheritance Required   | YES (class Child(MyABC))        | NO (Any matching class fits)    |
# | Can Share Code/State   | YES (Concrete base methods)     | NO (Pure interface declaration) |
# | Instantiation Guard    | Immediate TypeError             | None (at static analysis/mypy)  |
# | Template Method Pattern| Ideal (defines skeleton steps)  | Not applicable                  |
# | Third-party Pluggable  | Requires ABC.register()         | Native and automatic            |
# | Best Used For          | Core domain logic, frameworks   | Public APIs, loose coupling     |
# +------------------------+---------------------------------+---------------------------------+

print_separator("2. Architectural Decision Matrix")
print("Use abc.ABC        : When you want code reuse, shared state, or template methods.")
print("Use typing.Protocol: When defining external API boundaries and zero-coupling interfaces.")


# ==============================================================================
# 3. INTERFACE SEGREGATION PRINCIPLE (ISP)
# ==============================================================================
# The "I" in SOLID:
# "Clients should not be forced to depend upon interfaces that they do not use."
#
# Anti-Pattern: Creating a single bloated "Fat Interface" that forces implementers
# to write dummy or empty implementations of irrelevant methods.

print_separator("3. Interface Segregation Principle (ISP)")

# --- ANTI-PATTERN: The Fat Interface ---
class UniversalWorkerAntiPattern(ABC):
    @abstractmethod
    def write_code(self) -> str:
        pass

    @abstractmethod
    def eat_lunch(self) -> str:
        pass

    @abstractmethod
    def recharge_battery(self) -> str:
        pass


# An AI Bot must implement eat_lunch(), which makes no sense!
# A Human Developer must implement recharge_battery(), which makes no sense!

# --- CLEAN SOLUTION: Segregated, Focused Interfaces ---
@runtime_checkable
class Workable(Protocol):
    def perform_task(self) -> str:
        ...

@runtime_checkable
class Feedable(Protocol):
    def eat_meal(self) -> str:
        ...

@runtime_checkable
class Rechargeable(Protocol):
    def charge_battery(self) -> str:
        ...


class HumanEngineer:
    def __init__(self, name: str):
        self.name = name

    def perform_task(self) -> str:
        return f"{self.name} authored clean, tested Python code."

    def eat_meal(self) -> str:
        return f"{self.name} enjoyed a Mediterranean salad."


class AutonomousRoboticAgent:
    def __init__(self, serial_num: str):
        self.serial_num = serial_num

    def perform_task(self) -> str:
        return f"Agent {self.serial_num} executed automated test suite."

    def charge_battery(self) -> str:
        return f"Agent {self.serial_num} connected to 48V inductive charging pad."


human = HumanEngineer("Sameer")
bot = AutonomousRoboticAgent("BOT-9000")

print(f"Human is Workable    : {isinstance(human, Workable)} | Feedable: {isinstance(human, Feedable)} | Rechargeable: {isinstance(human, Rechargeable)}")
print(f"Bot is Workable      : {isinstance(bot, Workable)} | Feedable: {isinstance(bot, Feedable)} | Rechargeable: {isinstance(bot, Rechargeable)}")


# ==============================================================================
# 4. DEPENDENCY INVERSION PRINCIPLE (DIP)
# ==============================================================================
# The "D" in SOLID:
# 1. High-level modules should not depend on low-level modules. Both should depend on abstractions.
# 2. Abstractions should not depend on details. Details should depend on abstractions.

print_separator("4. Dependency Inversion Principle (DIP)")

# The Abstraction Contract:
class MessageNotificationSender(ABC):
    """Abstract contract for dispatching transactional alerts."""
    @abstractmethod
    def send_alert(self, recipient: str, message: str) -> bool:
        pass


# Low-level Concrete Implementation 1: AWS SES
class AmazonSESSender(MessageNotificationSender):
    def send_alert(self, recipient: str, message: str) -> bool:
        print(f"[AWS SES] Dispatched email to <{recipient}>: {message}")
        return True


# Low-level Concrete Implementation 2: Twilio SMS
class TwilioSMSSender(MessageNotificationSender):
    def send_alert(self, recipient: str, message: str) -> bool:
        print(f"[Twilio SMS] Dispatched text to +1-{recipient}: {message}")
        return True


# High-Level Domain Service (Inversion of Control):
# OrderCheckoutService does NOT instantiate AmazonSES or Twilio directly.
# It depends solely on the MessageNotificationSender abstraction injected at runtime!
class OrderCheckoutService:
    def __init__(self, notifier: MessageNotificationSender):
        self.notifier = notifier  # Injected dependency

    def finalize_order(self, customer_contact: str, order_id: str, amount: float) -> None:
        print(f"\n[Checkout] Order {order_id} processed for ${amount:.2f}.")
        alert_body = f"Your order #{order_id} has been confirmed!"
        self.notifier.send_alert(customer_contact, alert_body)


# We can swap notification backends without changing a single line in OrderCheckoutService!
email_service = OrderCheckoutService(notifier=AmazonSESSender())
email_service.finalize_order("customer@example.com", "ORD-101", 149.99)

sms_service = OrderCheckoutService(notifier=TwilioSMSSender())
sms_service.finalize_order("5550192834", "ORD-102", 89.50)


# ==============================================================================
# 5. THE TEMPLATE METHOD PATTERN
# ==============================================================================
# The Template Method is a classic Gang of Four behavioral pattern that exemplifies
# the power of Abstract Base Classes.
#
# Concept:
# The abstract base class defines the skeleton of an algorithm in a concrete
# method (the "template method"), deferring specific steps (primitive operations
# and hooks) to subclasses. The overall sequence of execution is fixed and invariant!

print_separator("5. The Template Method Pattern: Invariant Workflow Skeleton")

class DataETLPipeline(ABC):
    """
    Abstract ETL (Extract, Transform, Load) Pipeline.
    Defines the invariant template method `run_pipeline()`.
    """

    def run_pipeline(self, source_path: str, target_destination: str) -> Dict[str, Any]:
        """
        The Template Method: Invariant execution sequence.
        Subclasses cannot alter the algorithm's order of operations!
        """
        print(f"\n--- Initiating Pipeline: {self.__class__.__name__} ---")
        start_time = time.time()

        # Step 1: Invariant pre-flight setup
        self._initialize_resources()

        # Step 2: Abstract primitive operation (subclass provides)
        raw_data = self.extract(source_path)

        # Step 3: Abstract primitive operation (subclass provides)
        transformed_data = self.transform(raw_data)

        # Step 4: Optional hook method (subclass may override, default no-op)
        if self.should_validate():
            self.validate(transformed_data)

        # Step 5: Abstract primitive operation (subclass provides)
        record_count = self.load(transformed_data, target_destination)

        # Step 6: Invariant post-flight cleanup
        self._cleanup_resources()

        elapsed = time.time() - start_time
        print(f"Pipeline completed in {elapsed*1000:.2f} ms. Processed {record_count} records.")
        return {"status": "SUCCESS", "records": record_count}

    def _initialize_resources(self) -> None:
        """Concrete invariant step."""
        print("[Step 1: Init] Allocating worker thread pool and memory buffers.")

    def _cleanup_resources(self) -> None:
        """Concrete invariant step."""
        print("[Step 6: Cleanup] Flushing buffers and releasing socket locks.")

    # Primitive operations (Must be implemented by concrete pipelines)
    @abstractmethod
    def extract(self, source_path: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def transform(self, raw_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def load(self, cleaned_records: List[Dict[str, Any]], destination: str) -> int:
        pass

    # Hook method: Subclasses can customize behavior without overriding the workflow
    def should_validate(self) -> bool:
        """Hook method: defaults to True."""
        return True

    def validate(self, records: List[Dict[str, Any]]) -> None:
        """Hook method: default implementation checks for empty payloads."""
        print("[Step 4: Validation Hook] Executing default schema integrity check.")
        if not records:
            raise ValueError("Validation failed: transformed record set is empty!")


class FinancialTransactionsETL(DataETLPipeline):
    """Concrete pipeline specialized for financial audit trails."""

    def extract(self, source_path: str) -> List[Dict[str, Any]]:
        print(f"[Step 2: Extract] Streaming financial raw ledger records from {source_path}")
        return [
            {"tx_id": "TX_01", "raw_amount": "1500.50", "currency": "usd"},
            {"tx_id": "TX_02", "raw_amount": "250.00", "currency": "eur"}
        ]

    def transform(self, raw_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        print("[Step 3: Transform] Normalizing currencies to USD and computing tax.")
        cleaned = []
        for r in raw_records:
            cleaned.append({
                "tx_id": r["tx_id"],
                "usd_amount": float(r["raw_amount"]),
                "tax_withheld": float(r["raw_amount"]) * 0.05
            })
        return cleaned

    def load(self, cleaned_records: List[Dict[str, Any]], destination: str) -> int:
        print(f"[Step 5: Load] Writing {len(cleaned_records)} encrypted records into {destination}")
        return len(cleaned_records)


# Execute the Template Method workflow
etl = FinancialTransactionsETL()
result = etl.run_pipeline("s3://raw-banking-vault/2026/10/tx.csv", "snowflake://warehouse.ledger")


# ==============================================================================
# 6. THE LAW OF LEAKY ABSTRACTIONS
# ==============================================================================
# Coined by Joel Spolsky (2002):
# "All non-trivial abstractions, to some degree, are leaky."
#
# Meaning:
# No matter how well you encapsulate or abstract a mechanism, underlying reality
# will occasionally bleed through the abstraction layer:
#   - Network abstractions (e.g. NFS / RPC) hide networks, but latency and packet
#     drops leak through.
#   - SQL ORMs hide SQL, but Cartesian products and N+1 queries leak through.
#   - Memory management (Garbage Collection) hides pointers, but Out-Of-Memory
#     errors and pause latency leak through.
#
# Architect's Defense:
# 1. Provide transparent diagnostic telemetry and escape hatches.
# 2. Never swallow underlying exceptions silently; re-raise them wrapped in domain-specific errors.
# 3. Always expose timeout, retry, and cancellation policies in abstract contracts.

print_separator("6. Designing Leak-Resilient Abstractions (Domain Error Wrapping)")

class StorageError(Exception):
    """Base domain exception for the storage abstraction."""
    pass

class StorageTimeoutError(StorageError):
    """Wrapped exception indicating network latency or timeout leakage."""
    pass

class StorageQuotaExceededError(StorageError):
    """Wrapped exception indicating underlying capacity leakage."""
    pass

print("Domain Error Wrapping Principle:")
print(" - When an underlying low-level library throws (e.g. socket.timeout or BotoCoreError),")
print(" - The abstraction catches it and translates it into a domain-level StorageTimeoutError.")
print(" - Client code stays decoupled from vendor-specific exception hierarchies!")


# ==============================================================================
# KEY SUMMARY & TAKEAWAYS
# ==============================================================================
print_separator("Key Takeaways: Protocols vs ABCs & Design Principles")
print("1. ABCs provide nominal typing and can share code; Protocols provide structural static duck typing.")
print("2. @runtime_checkable allows Protocols to participate in isinstance() checks without inheritance.")
print("3. Interface Segregation Principle (ISP) prevents bloated, monolithic interfaces.")
print("4. Dependency Inversion Principle (DIP) decouples high-level policy from low-level mechanics.")
print("5. The Template Method pattern defines an invariant workflow skeleton with abstract primitive steps.")
print("6. All non-trivial abstractions leak; wrap underlying faults in domain-specific exceptions.")
print("=" * 78)
