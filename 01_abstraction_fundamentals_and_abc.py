"""
================================================================================
Day 23: Python Object-Oriented Programming - Abstraction Fundamentals & ABC
================================================================================
Abstraction is the fourth foundational pillar of Object-Oriented Programming (OOP),
completing the four core pillars:
  1. Encapsulation (Day 20): Hiding internal state & access control.
  2. Inheritance   (Day 21): Code reuse & hierarchical classification.
  3. Polymorphism   (Day 22): Uniform interface across diverse types.
  4. Abstraction   (Day 23): Hiding implementation complexity & enforcing contracts.

Core Definition:
Abstraction is the process of exposing only the essential, high-level features of
an entity while hiding background details and algorithmic complexity. It defines
"WHAT" an object does rather than "HOW" it achieves it.

Key Concepts Covered in this Script:
1. The Mental Model of Abstraction & The Car Dashboard Analogy
2. Abstraction vs. Encapsulation (Key Distinctions)
3. Why Python Needs the `abc` Module (The NotImplementedError Dilemma)
4. Abstract Base Classes (`abc.ABC`) and `@abstractmethod`
5. Instantiation Enforcement at Runtime (Catching Incomplete Subclasses)
6. Abstract Methods with Default Implementations (`super()` Chaining)
7. Production Demonstration: Industrial IoT Smart Device Control Architecture
================================================================================
"""

import abc
from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime


def print_separator(title: str) -> None:
    """Utility helper to print structured visual headers for each demonstration."""
    print("\n" + "=" * 78)
    print(f" {title}")
    print("=" * 78)


# ==============================================================================
# 1. THE MENTAL MODEL OF ABSTRACTION
# ==============================================================================
# In everyday life, we interact with abstractions constantly:
# - Driving a car: You press the accelerator pedal. You don't need to manually
#   calculate fuel injection ratios, spark plug ignition timings, or transmission
#   gear mesh hydraulics. The pedal is the abstraction; the engine mechanics
#   are the hidden implementation.
# - Turning on a TV: You press the "Power" button on a remote. You don't need
#   to manage infrared carrier frequencies or capacitor charging cycles.
#
# In software engineering:
# An Abstraction provides a clean, predictable, and robust contract for client
# code while shielding the client from underlying volatility and complexity.

print_separator("1. Conceptual Foundation: The Car Dashboard Abstraction")

print("Key Principle of Abstraction:")
print(" - Client code interacts with a high-level contract ('accelerate', 'brake').")
print(" - Concrete implementations handle engine mechanics (Electric, Petrol, Diesel).")
print(" - Clients remain completely unaffected if the engine implementation changes!")


# ==============================================================================
# 2. ABSTRACTION VS. ENCAPSULATION
# ==============================================================================
# While often confused, Abstraction and Encapsulation solve different problems:
#
# +-------------------+-----------------------------------+-----------------------------------+
# | Dimension         | Abstraction                       | Encapsulation                     |
# +-------------------+-----------------------------------+-----------------------------------+
# | Primary Goal      | Hides COMPLEXITY                  | Hides DATA & INTERNAL STATE       |
# | Question Answered | "WHAT does this component do?"    | "HOW is this component protected?"|
# | Mechanism         | Abstract Base Classes, Interfaces | Private attributes (_, __), props |
# | Architectural Level| High-level design & contracts    | Low-level implementation details  |
# | Focus             | External interface to consumers   | Internal boundaries of the class  |
# +-------------------+-----------------------------------+-----------------------------------+

print_separator("2. Abstraction vs. Encapsulation Matrix")
print("Abstraction   : Defines the boundary of WHAT services an object guarantees.")
print("Encapsulation : Bundles state with logic and protects internal data from mutation.")


# ==============================================================================
# 3. THE NOTIMPLEMENTEDERROR DILEMMA (WHY PYTHON NEEDS THE `abc` MODULE)
# ==============================================================================
# Unlike languages such as Java or C#, Python historically lacked an `abstract`
# keyword built into its language grammar.
#
# The naive approach was raising `NotImplementedError` inside method bodies.
# Let's inspect why this naive approach is dangerous in production!

print_separator("3. The Naive Approach: Raising NotImplementedError (Flawed)")

class NaiveVehicleContract:
    """Naive base class without ABC."""
    def start_engine(self) -> str:
        raise NotImplementedError("Subclasses must implement start_engine()!")

    def stop_engine(self) -> str:
        raise NotImplementedError("Subclasses must implement stop_engine()!")


# THE FATAL FLAW:
# You can instantiate the naive base class or an incomplete subclass without error!
# The bug only explodes at RUNTIME when someone finally invokes the missing method.
naive_instance = NaiveVehicleContract()
print(f"Danger: Naive base class was successfully instantiated: {naive_instance}!")

try:
    # Failure only occurs during method call, potentially hours into production execution!
    naive_instance.start_engine()
except NotImplementedError as exc:
    print(f"Caught runtime error: {exc}")
    print("Conclusion: NotImplementedError is reactive, not proactive.")


# ==============================================================================
# 4. ABSTRACT BASE CLASSES (`abc.ABC`) AND `@abstractmethod`
# ==============================================================================
# Python PEP 3119 introduced the `abc` (Abstract Base Classes) standard module.
# Inheriting from `abc.ABC` and marking methods with `@abstractmethod` informs
# Python's class-creation machinery (ABCMeta) to PROHIBIT instantiation of any
# class that has not fulfilled the entire abstract contract!

print_separator("4. Formal Abstraction via abc.ABC and @abstractmethod")

class Vehicle(ABC):
    """
    Formal Abstract Base Class representing the universal vehicle contract.
    Any vehicle in our system MUST provide start_engine, stop_engine, and drive.
    """

    def __init__(self, vin: str, model: str):
        self.vin = vin
        self.model = model

    @abstractmethod
    def start_engine(self) -> str:
        """Initialize engine power train."""
        pass

    @abstractmethod
    def stop_engine(self) -> str:
        """Safely shut down power train."""
        pass

    @abstractmethod
    def drive(self, distance_km: float) -> str:
        """Propel the vehicle for a designated distance."""
        pass


# TEST 1: Attempting to instantiate the Abstract Base Class directly
print("Test 1: Attempting to instantiate Vehicle(ABC) directly...")
try:
    v = Vehicle("VIN-9999", "Prototype")
except TypeError as error:
    print(f"SUCCESSFULLY BLOCKED: {error}")


# TEST 2: Incomplete Subclass (Forgot to implement `drive()`)
class IncompleteElectricCar(Vehicle):
    """Subclass that only implements start_engine and stop_engine."""
    def start_engine(self) -> str:
        return f"{self.model}: High-voltage contactors closed. Silent power ON."

    def stop_engine(self) -> str:
        return f"{self.model}: High-voltage contactors opened. Power OFF."

    # Note: drive() is deliberately omitted!


print("\nTest 2: Attempting to instantiate IncompleteElectricCar (missing drive)...")
try:
    car = IncompleteElectricCar("VIN-1001", "Tesla Model 3")
except TypeError as error:
    print(f"SUCCESSFULLY BLOCKED: {error}")


# TEST 3: Fully Concrete Subclass
class ElectricCar(Vehicle):
    """Complete concrete subclass fulfilling every method in the contract."""
    def __init__(self, vin: str, model: str, battery_kwh: float):
        super().__init__(vin, model)
        self.battery_kwh = battery_kwh

    def start_engine(self) -> str:
        return f"[{self.model} | {self.vin}] Inverter active. 0 RPM hum."

    def stop_engine(self) -> str:
        return f"[{self.model} | {self.vin}] Regeneration paused. System standby."

    def drive(self, distance_km: float) -> str:
        energy_used = distance_km * 0.18
        self.battery_kwh -= energy_used
        return (
            f"[{self.model}] Drove {distance_km} km. Consumed {energy_used:.2f} kWh. "
            f"Remaining battery: {self.battery_kwh:.2f} kWh."
        )


print("\nTest 3: Instantiating complete ElectricCar...")
ev = ElectricCar("5YJ3E1EA1JF", "Tesla Model 3", battery_kwh=75.0)
print(ev.start_engine())
print(ev.drive(120.0))
print(ev.stop_engine())


# ==============================================================================
# 5. UNDER THE HOOD: HOW `@abstractmethod` WORKS
# ==============================================================================
# When you decorate a function with `@abstractmethod`, Python simply sets a boolean
# flag on the function object: `__isabstractmethod__ = True`.
#
# When `type.__call__` executes during class instantiation, `ABCMeta` scans the
# class namespace. If any callable has `__isabstractmethod__ == True`, it collects
# them into a set and raises `TypeError`.

print_separator("5. Under the Hood: The __isabstractmethod__ Flag")

def sample_func():
    pass

@abstractmethod
def sample_abstract_func():
    pass

print(f"Standard function has __isabstractmethod__: {getattr(sample_func, '__isabstractmethod__', False)}")
print(f"Decorated function has __isabstractmethod__: {getattr(sample_abstract_func, '__isabstractmethod__', False)}")


# ==============================================================================
# 6. ABSTRACT METHODS WITH DEFAULT IMPLEMENTATIONS (super() CHAINING)
# ==============================================================================
# Common misconception: "Abstract methods cannot have an implementation body."
# TRUTH IN PYTHON:
# An abstract method CAN have a full implementation body!
# Marking it `@abstractmethod` forces subclasses to explicitly override it,
# but the subclass can use `super().method()` to invoke the default base behavior.

print_separator("6. Abstract Methods with Default Concrete Logic via super()")

class AuditLogger(ABC):
    """Abstract base class that enforces audit logging across all operations."""

    @abstractmethod
    def log_event(self, action: str, actor: str) -> Dict[str, Any]:
        """
        Base implementation provides standard timestamp and schema formatting.
        Subclasses MUST override this method, but SHOULD invoke super().
        """
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "action": action,
            "actor": actor,
            "status": "RECORDED"
        }


class DatabaseAuditLogger(AuditLogger):
    """Subclass that extends base logging with database transaction metadata."""

    def __init__(self, table_name: str):
        self.table_name = table_name

    def log_event(self, action: str, actor: str) -> Dict[str, Any]:
        # Reuse standard base payload through super()
        payload = super().log_event(action, actor)
        payload["destination"] = f"DB_TABLE:{self.table_name}"
        payload["storage_engine"] = "PostgreSQL"
        return payload


class CloudWatchAuditLogger(AuditLogger):
    """Subclass that streams log payloads to AWS CloudWatch LogGroups."""

    def __init__(self, log_group: str):
        self.log_group = log_group

    def log_event(self, action: str, actor: str) -> Dict[str, Any]:
        payload = super().log_event(action, actor)
        payload["destination"] = f"AWS/CloudWatch:{self.log_group}"
        payload["retention_days"] = 90
        return payload


db_logger = DatabaseAuditLogger("security_events")
cw_logger = CloudWatchAuditLogger("/ecs/auth-service")

print("Database Audit Record :", db_logger.log_event("USER_LOGIN", "admin@company.com"))
print("CloudWatch Audit Record:", cw_logger.log_event("PASSWORD_RESET", "user_42"))


# ==============================================================================
# 7. PRODUCTION DEMONSTRATION: INDUSTRIAL IOT DEVICE CONTROLLER
# ==============================================================================
# Let's build a real-world, enterprise-grade architecture:
# A factory automation control plane managing heterogeneous IoT hardware
# (Robotic Arm, Thermal Chamber, Conveyor Belt).
#
# The control plane requires every device to implement:
# 1. connect()
# 2. execute_diagnostic()
# 3. emergency_shutdown()
# 4. read_telemetry()

print_separator("7. Production Architecture: Industrial IoT Device Controller")

class IndustrialIoTDevice(ABC):
    """
    Abstract contract for all industrial hardware operating on the factory floor.
    Ensures safe lifecycle state transitions and telemetric observation.
    """

    def __init__(self, device_id: str, location_zone: str):
        self.device_id = device_id
        self.location_zone = location_zone
        self._is_online = False
        self._safety_tripped = False

    @property
    def is_online(self) -> bool:
        return self._is_online

    @abstractmethod
    def connect(self) -> bool:
        """Establish handshake protocol with device firmware."""
        pass

    @abstractmethod
    def execute_diagnostic(self) -> Dict[str, Any]:
        """Run internal hardware diagnostics and return status matrix."""
        pass

    @abstractmethod
    def read_telemetry(self) -> Dict[str, Any]:
        """Query real-time physical sensor data."""
        pass

    @abstractmethod
    def emergency_shutdown(self) -> None:
        """Instantly trip electrical interlocks to safe-state."""
        pass


class RoboticArmController(IndustrialIoTDevice):
    """Precision 6-Axis articulation arm for assembly line fabrication."""

    def __init__(self, device_id: str, location_zone: str, max_payload_kg: float):
        super().__init__(device_id, location_zone)
        self.max_payload_kg = max_payload_kg
        self.joint_angles = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    def connect(self) -> bool:
        self._is_online = True
        print(f"[{self.device_id}] CAN bus link established at 1 Mbps.")
        return True

    def execute_diagnostic(self) -> Dict[str, Any]:
        return {
            "device": self.device_id,
            "servo_calibration": "NOMINAL",
            "joint_temperatures_c": [38.2, 39.1, 41.0, 37.8, 36.5, 35.9],
            "firmware": "v4.12.8"
        }

    def read_telemetry(self) -> Dict[str, Any]:
        return {
            "device": self.device_id,
            "status": "OPERATIONAL" if self._is_online else "OFFLINE",
            "current_payload_kg": 12.4,
            "active_cycle_count": 1420
        }

    def emergency_shutdown(self) -> None:
        self._safety_tripped = True
        self._is_online = False
        print(f"[EMERGENCY STOP] {self.device_id}: Mechanical brake clamps ENGAGED. Arm frozen in place!")


class ThermalChamberController(IndustrialIoTDevice):
    """Environmental stress testing thermal oven with PID heating coils."""

    def __init__(self, device_id: str, location_zone: str, target_temp_c: float):
        super().__init__(device_id, location_zone)
        self.target_temp_c = target_temp_c
        self.current_temp_c = 22.0

    def connect(self) -> bool:
        self._is_online = True
        print(f"[{self.device_id}] Modbus TCP session connected to heating PLC.")
        return True

    def execute_diagnostic(self) -> Dict[str, Any]:
        return {
            "device": self.device_id,
            "heating_elements": "ALL_OK",
            "cooling_compressor_pressure_psi": 145.2,
            "chamber_seal": "HERMETIC"
        }

    def read_telemetry(self) -> Dict[str, Any]:
        return {
            "device": self.device_id,
            "current_temp_c": self.current_temp_c,
            "target_temp_c": self.target_temp_c,
            "heater_duty_cycle_pct": 68.5
        }

    def emergency_shutdown(self) -> None:
        self._safety_tripped = True
        self._is_online = False
        print(f"[EMERGENCY STOP] {self.device_id}: Power contactors de-energized. Liquid N2 purge active!")


# ------------------------------------------------------------------------------
# High-Level Factory Control Plane (Dependent on the Abstraction)
# ------------------------------------------------------------------------------
class FactoryControlPlane:
    """
    Central orchestration supervisory system.
    This class depends EXCLUSIVELY on the IndustrialIoTDevice abstraction.
    It does not know or care whether a device is a robotic arm, a furnace, or a sensor!
    """

    def __init__(self, facility_name: str):
        self.facility_name = facility_name
        self.fleet: list[IndustrialIoTDevice] = []

    def register_device(self, device: IndustrialIoTDevice) -> None:
        self.fleet.append(device)
        print(f"Registered {device.device_id} into {self.facility_name} fleet.")

    def boot_all_devices(self) -> None:
        print(f"\n--- Booting Fleet in {self.facility_name} ---")
        for dev in self.fleet:
            dev.connect()

    def run_fleet_health_check(self) -> None:
        print(f"\n--- Fleet Diagnostic Report ({self.facility_name}) ---")
        for dev in self.fleet:
            diag = dev.execute_diagnostic()
            print(f"Device: {dev.device_id} | Zone: {dev.location_zone} | Health: {diag}")

    def trigger_facility_emergency_stop(self) -> None:
        print(f"\n[!] TRIGGERING FACILITY-WIDE EMERGENCY STOP AT {self.facility_name.upper()} [!]")
        for dev in self.fleet:
            dev.emergency_shutdown()


# Execute Factory Orchestration
factory = FactoryControlPlane("Gigafactory Texas - Line 4")
arm = RoboticArmController("ROBO-ARM-01", "Zone A - Weld", max_payload_kg=50.0)
oven = ThermalChamberController("THERMAL-CHAMBER-09", "Zone B - Stress Test", target_temp_c=125.0)

factory.register_device(arm)
factory.register_device(oven)

factory.boot_all_devices()
factory.run_fleet_health_check()
factory.trigger_facility_emergency_stop()


# ==============================================================================
# KEY SUMMARY & TAKEAWAYS
# ==============================================================================
print_separator("Key Takeaways: Abstraction Fundamentals & ABC")
print("1. Abstraction focuses on WHAT an object does, hiding internal complexity.")
print("2. Encapsulation protects internal state; Abstraction defines high-level contracts.")
print("3. Pure NotImplementedError fails too late at runtime call; abc.ABC fails at instantiation.")
print("4. Any class inheriting from abc.ABC with unimplemented @abstractmethods CANNOT be instantiated.")
print("5. Abstract methods CAN contain default implementations callable via super().")
print("6. High-level client systems should depend on Abstractions, not concrete details.")
print("=" * 78)
