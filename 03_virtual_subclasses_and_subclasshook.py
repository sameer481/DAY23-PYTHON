"""
================================================================================
Day 23: Python Object-Oriented Programming - Virtual Subclasses & __subclasshook__
================================================================================
In traditional object-oriented languages, type relationships are strictly nominal:
a class is only a subtype of an interface if it explicitly inherits from it in
source code.

Python's Abstract Base Classes provide a revolutionary capability:
  1. Virtual Subclassing via ABC.register()
  2. Dynamic Structural Type Checking via __subclasshook__()

This allows Python to combine the formal safety of abstract interfaces with
the runtime flexibility of Duck Typing!

Key Concepts Covered in this Script:
1. Nominal Subclasses vs. Virtual Subclasses
2. Explicit Registration via `ABC.register(TargetClass)`
3. Inspection of `__mro__` in Virtual Subclasses (Why ABC methods are NOT inherited)
4. Built-in Magic in `collections.abc` (Why `isinstance([], Sequence)` is True)
5. Custom Dynamic Structural Subtyping using `__subclasshook__(cls, C)`
6. Production Demonstration: Zero-Dependency Enterprise Plugin Orchestrator
================================================================================
"""

from abc import ABC, abstractmethod
from collections.abc import Sized, Iterable, Container
from typing import Dict, Any, List


def print_separator(title: str) -> None:
    """Utility helper to print structured visual headers for each demonstration."""
    print("\n" + "=" * 78)
    print(f" {title}")
    print("=" * 78)


# ==============================================================================
# 1. NOMINAL SUBCLASSES VS. VIRTUAL SUBCLASSES
# ==============================================================================
# - Nominal Subclass: Inherits directly `class Child(Parent):`. Present in MRO.
#   Inherits both method signatures and shared concrete method code.
# - Virtual Subclass: Does NOT inherit from Parent in source code. NOT in MRO.
#   Explicitly registered via `Parent.register(Child)`.
#   Satisfies `isinstance()` and `issubclass()`, but inherits NO code!

print_separator("1. Explicit Virtual Subclassing via ABC.register()")

class PaymentProcessor(ABC):
    """Abstract interface for all financial clearing processors."""

    @abstractmethod
    def process_transaction(self, account_id: str, amount_cents: int) -> bool:
        pass


# Imagine this is a 3rd-party library class (e.g. from vendor SDK) that you CANNOT edit:
class ThirdPartyLegacyStripeSDK:
    """Vendor SDK class that did not inherit from PaymentProcessor."""
    def process_transaction(self, account_id: str, amount_cents: int) -> bool:
        print(f"[Vendor Stripe SDK] Charged {amount_cents/100:.2f} to account {account_id}")
        return True


# BEFORE REGISTRATION:
print("Before registration:")
print(f"issubclass(ThirdPartyLegacyStripeSDK, PaymentProcessor): {issubclass(ThirdPartyLegacyStripeSDK, PaymentProcessor)}")

# REGISTER AS VIRTUAL SUBCLASS:
PaymentProcessor.register(ThirdPartyLegacyStripeSDK)

# AFTER REGISTRATION:
print("\nAfter PaymentProcessor.register(ThirdPartyLegacyStripeSDK):")
print(f"issubclass(ThirdPartyLegacyStripeSDK, PaymentProcessor): {issubclass(ThirdPartyLegacyStripeSDK, PaymentProcessor)}")

sdk_instance = ThirdPartyLegacyStripeSDK()
print(f"isinstance(sdk_instance, PaymentProcessor)             : {isinstance(sdk_instance, PaymentProcessor)}")


# ==============================================================================
# 2. CRITICAL MRO DIFFERENCE: VIRTUAL SUBCLASSES DO NOT INHERIT IMPLEMENTATION
# ==============================================================================
# Virtual subclasses satisfy type-checks (`isinstance`, `issubclass`), BUT:
# The ABC is NOT in the class's Method Resolution Order (`__mro__`).
# Concrete helper methods in the ABC are NOT inherited!

print_separator("2. Method Resolution Order (MRO) in Virtual Subclasses")

print("ThirdPartyLegacyStripeSDK MRO:")
for idx, cls_in_mro in enumerate(ThirdPartyLegacyStripeSDK.__mro__):
    print(f"  [{idx}] {cls_in_mro.__name__}")

print("\nNotice: PaymentProcessor does NOT appear in the MRO!")
print("Virtual subclasses are pure type assertions; they never inherit code.")


# ==============================================================================
# 3. HOW THE STANDARD LIBRARY USES THIS: collections.abc
# ==============================================================================
# Have you ever wondered why `isinstance([1, 2, 3], Sized)` returns True, even
# though `list` never inherited from `collections.abc.Sized`?

print_separator("3. Standard Library Magic in collections.abc")

my_list = [10, 20, 30]

print(f"isinstance(my_list, Sized)    : {isinstance(my_list, Sized)}     (has __len__)")
print(f"isinstance(my_list, Iterable) : {isinstance(my_list, Iterable)}  (has __iter__)")
print(f"isinstance(my_list, Container): {isinstance(my_list, Container)} (has __contains__)")

print("\nDoes Python's 'list' explicitly inherit from Sized in its MRO?")
print([cls.__name__ for cls in list.__mro__])
print("No! It works dynamically via __subclasshook__!")


# ==============================================================================
# 4. CUSTOM STRUCTURAL SUBTYPING USING __subclasshook__
# ==============================================================================
# `__subclasshook__(cls, C)` is a special class method called by ABCMeta during
# `issubclass(C, cls)`.
#
# Return values:
#   True           -> Class C is confirmed as a subclass.
#   False          -> Class C is explicitly NOT a subclass.
#   NotImplemented -> Defer to normal inheritance / register() checks.
#
# Let's create an ABC that automatically detects ANY class having a `.serialize()`
# and `.deserialize()` method without requiring explicit inheritance!

print_separator("4. Custom Dynamic __subclasshook__ for Structural Contracts")

class Serializable(ABC):
    """
    Abstract contract for serializable entities.
    Automatically recognizes any class that provides both serialize and deserialize!
    """

    @abstractmethod
    def serialize(self) -> str:
        pass

    @abstractmethod
    def deserialize(self, raw_data: str) -> None:
        pass

    @classmethod
    def __subclasshook__(cls, subclass: type) -> bool:
        if cls is Serializable:
            # Check if any class in the subclass's MRO provides both required methods
            has_serialize = any("serialize" in B.__dict__ for B in subclass.__mro__)
            has_deserialize = any("deserialize" in B.__dict__ for B in subclass.__mro__)
            if has_serialize and has_deserialize:
                return True
        return NotImplemented


# Class A: Completely independent class, no inheritance, no register() call!
class UserProfile:
    def serialize(self) -> str:
        return "user_profile_json_data"

    def deserialize(self, raw_data: str) -> None:
        pass


# Class B: Incomplete class (only has serialize)
class IncompleteOrder:
    def serialize(self) -> str:
        return "order_data"


print(f"UserProfile satisfies Serializable     : {issubclass(UserProfile, Serializable)}")
print(f"IncompleteOrder satisfies Serializable : {issubclass(IncompleteOrder, Serializable)}")

user = UserProfile()
print(f"isinstance(user, Serializable)         : {isinstance(user, Serializable)}")


# ==============================================================================
# 5. PRODUCTION DEMONSTRATION: ZERO-DEPENDENCY PLUGIN ORCHESTRATOR
# ==============================================================================
# Real-world scenario:
# You are building a high-throughput Data Ingestion Pipeline. Third-party developers
# submit custom plugins.
#
# To avoid forcing third parties to install our internal framework library or
# import our ABC, our pipeline uses `__subclasshook__` to automatically validate
# and execute external third-party plugins based on pure structural contracts!

print_separator("5. Production Architecture: Dynamic Data Pipeline Plugin Engine")

class PipelinePlugin(ABC):
    """
    Contract for pipeline plugins.
    A valid plugin must define:
      - `plugin_name` (property or method returning str)
      - `transform(self, record: Dict[str, Any]) -> Dict[str, Any]`
    """

    @abstractmethod
    def transform(self, record: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @classmethod
    def __subclasshook__(cls, C: type) -> bool:
        if cls is PipelinePlugin:
            has_transform = any(
                callable(getattr(B, "transform", None)) for B in C.__mro__
            )
            has_name = any(
                hasattr(B, "plugin_name") for B in C.__mro__
            )
            if has_transform and has_name:
                return True
        return NotImplemented


# ------------------------------------------------------------------------------
# Third-Party Plugin 1: External Developer's PII Masking Plugin
# (Zero dependencies: did NOT import PipelinePlugin or abc!)
# ------------------------------------------------------------------------------
class ThirdPartyPIIMasker:
    """Developed by external security team with zero knowledge of our ABC."""
    plugin_name = "security_pii_masker_v1"

    def transform(self, record: Dict[str, Any]) -> Dict[str, Any]:
        sanitized = record.copy()
        if "email" in sanitized:
            email = sanitized["email"]
            name, domain = email.split("@", 1)
            sanitized["email"] = f"{name[0]}***@{domain}"
        if "ssn" in sanitized:
            sanitized["ssn"] = "***-**-****"
        return sanitized


# ------------------------------------------------------------------------------
# Third-Party Plugin 2: External Analytics Enrichment Plugin
# (Also zero dependencies!)
# ------------------------------------------------------------------------------
class ThirdPartyGeoEnricher:
    """Enriches IP addresses with country codes."""
    plugin_name = "geo_enricher_v2"

    def transform(self, record: Dict[str, Any]) -> Dict[str, Any]:
        enriched = record.copy()
        enriched["geo_country"] = "US"
        enriched["geo_region"] = "North America"
        return enriched


# ------------------------------------------------------------------------------
# High-Level Data Ingestion Pipeline
# ------------------------------------------------------------------------------
class EnterpriseDataPipeline:
    """Ingests raw records and runs them through structurally validated plugins."""

    def __init__(self):
        self._plugins: List[Any] = []

    def load_plugin(self, plugin_instance: Any) -> None:
        """Type-check using the PipelinePlugin ABC before accepting the plugin."""
        if not isinstance(plugin_instance, PipelinePlugin):
            raise TypeError(
                f"Rejection: {type(plugin_instance).__name__} does not conform to the "
                f"PipelinePlugin contract (must provide 'plugin_name' and 'transform' method)!"
            )
        self._plugins.append(plugin_instance)
        print(f"[PIPELINE] Successfully loaded plugin: {plugin_instance.plugin_name} ({type(plugin_instance).__name__})")

    def process_record(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        current = raw_record
        for p in self._plugins:
            current = p.transform(current)
        return current


# Pipeline Orchestration Execution
pipeline = EnterpriseDataPipeline()

# Instantiate independent third-party plugins
pii_plugin = ThirdPartyPIIMasker()
geo_plugin = ThirdPartyGeoEnricher()

# Load plugins: PipelinePlugin validates both via __subclasshook__!
pipeline.load_plugin(pii_plugin)
pipeline.load_plugin(geo_plugin)

# Process enterprise telemetry record
raw_event = {
    "event_id": "EVT-9042",
    "email": "sarah.connor@cyberdyne.corp",
    "ssn": "987-65-4321",
    "action": "QUERY_INVENTORY",
    "ip_address": "192.168.1.100"
}

print("\n--- Processing Raw Data Event Through Pipeline ---")
print("Raw Input Event  :", raw_event)
processed_event = pipeline.process_record(raw_event)
print("Sanitized Output :", processed_event)


# Testing Rejection of Non-Conforming Object
class InvalidRandomClass:
    def do_something_else(self):
        pass

print("\n--- Testing Pipeline Rejection of Invalid Object ---")
try:
    pipeline.load_plugin(InvalidRandomClass())
except TypeError as rejection_err:
    print(f"Contract Guard Triggered: {rejection_err}")


# ==============================================================================
# KEY SUMMARY & TAKEAWAYS
# ==============================================================================
print_separator("Key Takeaways: Virtual Subclasses & __subclasshook__")
print("1. Nominal subclasses inherit code and participate in MRO (class A(B)).")
print("2. Virtual subclasses (ABC.register) pass isinstance/issubclass but inherit NO code.")
print("3. __subclasshook__ enables runtime dynamic duck-typed structural subtyping.")
print("4. Python's collections.abc (Iterable, Sized, Mapping) relies on __subclasshook__.")
print("5. Zero-dependency plugin systems can safely enforce contracts without tight coupling.")
print("=" * 78)
