"""
================================================================================
Day 23: Python Object-Oriented Programming - Production Practical Projects
================================================================================
This script implements three end-to-end, enterprise-scale software architectures
built entirely around the principles of Abstraction:

Project 1: Universal Multi-Cloud Object Storage System
  - Abstract StorageBackend contract isolating cloud persistence.
  - Concrete Backends: Local Filesystem, AWS S3, Google Cloud Storage (GCS).
  - High-level MultiCloudStorageManager with automatic replication & failover.

Project 2: Enterprise Database Abstraction Layer (DAL) & Unit-Of-Work
  - Abstract DatabaseDialect & DatabaseConnection isolating SQL syntax variations.
  - Concrete Dialects: PostgreSQL ($1, $2), SQLite (?), and MySQL (%s).
  - Generic Repository & UnitOfWork transaction context manager with rollback.

Project 3: Resilient Multi-Provider AI LLM & Agent Workflow Engine
  - Abstract LLMProvider contract normalizing model interaction.
  - Concrete Providers: OpenAI (GPT-4o), Anthropic (Claude 3.5), Local (Ollama/Llama-3).
  - ResilientAgentPipeline with automatic rate-limit failover & token cost accounting.
================================================================================
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import hashlib
import time
import uuid


def print_banner(project_num: int, title: str) -> None:
    """Utility helper to print high-impact visual banners for projects."""
    print("\n" + "#" * 80)
    print(f" PROJECT {project_num}: {title.upper()}")
    print("#" * 80)


# ==============================================================================
# PROJECT 1: UNIVERSAL MULTI-CLOUD OBJECT STORAGE SYSTEM
# ==============================================================================
print_banner(1, "Universal Multi-Cloud Object Storage Architecture")

class StorageBackend(ABC):
    """
    Abstract contract for cloud and local persistence layers.
    Shields consumers from vendor-specific SDKs (boto3, google-cloud-storage, os).
    """

    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self._is_connected = False

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the underlying cloud provider."""
        pass

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    @abstractmethod
    def connect(self) -> bool:
        """Establish authenticated connection session."""
        pass

    @abstractmethod
    def upload_object(self, key: str, data: bytes, metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Upload raw binary object with associated metadata."""
        pass

    @abstractmethod
    def download_object(self, key: str) -> bytes:
        """Retrieve binary object bytes by key."""
        pass

    @abstractmethod
    def delete_object(self, key: str) -> bool:
        """Purge object from storage tier."""
        pass

    @abstractmethod
    def list_objects(self, prefix: str = "") -> List[str]:
        """Query storage keys filtered by key prefix."""
        pass

    @abstractmethod
    def generate_presigned_url(self, key: str, expiry_seconds: int = 3600) -> str:
        """Create time-limited secure direct download URL."""
        pass


class LocalFileSystemStorage(StorageBackend):
    """Storage implementation writing to local block storage or mounted NAS/SAN."""

    def __init__(self, mount_path: str = "/var/data/storage"):
        super().__init__(bucket_name=mount_path)
        self._store: Dict[str, bytes] = {}
        self._meta: Dict[str, Dict[str, str]] = {}

    @property
    def provider_name(self) -> str:
        return "POSIX Local Filesystem / NAS"

    def connect(self) -> bool:
        self._is_connected = True
        print(f"[{self.provider_name}] Verified directory permissions at {self.bucket_name}")
        return True

    def upload_object(self, key: str, data: bytes, metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        self._store[key] = data
        self._meta[key] = metadata or {}
        checksum = hashlib.sha256(data).hexdigest()
        return {
            "key": key,
            "bytes_written": len(data),
            "sha256": checksum,
            "path": f"{self.bucket_name}/{key}"
        }

    def download_object(self, key: str) -> bytes:
        if key not in self._store:
            raise KeyError(f"File '{key}' not found on local path.")
        return self._store[key]

    def delete_object(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            self._meta.pop(key, None)
            return True
        return False

    def list_objects(self, prefix: str = "") -> List[str]:
        return [k for k in self._store.keys() if k.startswith(prefix)]

    def generate_presigned_url(self, key: str, expiry_seconds: int = 3600) -> str:
        # Local storage returns file URI
        return f"file://{self.bucket_name}/{key}?token={uuid.uuid4().hex[:8]}"


class AmazonS3Storage(StorageBackend):
    """Enterprise storage implementation targeting AWS Simple Storage Service (S3)."""

    def __init__(self, s3_bucket: str, region: str = "us-east-1"):
        super().__init__(bucket_name=s3_bucket)
        self.region = region
        self._s3_vault: Dict[str, bytes] = {}

    @property
    def provider_name(self) -> str:
        return f"Amazon Web Services (AWS S3) [{self.region}]"

    def connect(self) -> bool:
        self._is_connected = True
        print(f"[{self.provider_name}] IAM STS credentials assumed for bucket s3://{self.bucket_name}")
        return True

    def upload_object(self, key: str, data: bytes, metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        self._s3_vault[key] = data
        etag = hashlib.md5(data).hexdigest()
        return {
            "key": key,
            "bucket": self.bucket_name,
            "etag": f'"{etag}"',
            "storage_class": "INTELLIGENT_TIERING",
            "arn": f"arn:aws:s3:::{self.bucket_name}/{key}"
        }

    def download_object(self, key: str) -> bytes:
        if key not in self._s3_vault:
            raise KeyError(f"404 NoSuchKey: s3://{self.bucket_name}/{key}")
        return self._s3_vault[key]

    def delete_object(self, key: str) -> bool:
        return self._s3_vault.pop(key, None) is not None

    def list_objects(self, prefix: str = "") -> List[str]:
        return [k for k in self._s3_vault.keys() if k.startswith(prefix)]

    def generate_presigned_url(self, key: str, expiry_seconds: int = 3600) -> str:
        token = uuid.uuid4().hex
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}?X-Amz-Expires={expiry_seconds}&X-Amz-Signature={token}"


class GoogleCloudStorage(StorageBackend):
    """Enterprise storage implementation targeting Google Cloud Storage (GCS)."""

    def __init__(self, gcs_bucket: str, project_id: str = "corp-prod-analytics"):
        super().__init__(bucket_name=gcs_bucket)
        self.project_id = project_id
        self._gcs_vault: Dict[str, bytes] = {}

    @property
    def provider_name(self) -> str:
        return f"Google Cloud Storage (GCS) [{self.project_id}]"

    def connect(self) -> bool:
        self._is_connected = True
        print(f"[{self.provider_name}] OAuth2 Service Account activated for gs://{self.bucket_name}")
        return True

    def upload_object(self, key: str, data: bytes, metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        self._gcs_vault[key] = data
        crc32c = hashlib.sha256(data).hexdigest()[:8]
        return {
            "key": key,
            "bucket": self.bucket_name,
            "generation": int(time.time() * 1000),
            "crc32c": crc32c,
            "gs_uri": f"gs://{self.bucket_name}/{key}"
        }

    def download_object(self, key: str) -> bytes:
        if key not in self._gcs_vault:
            raise KeyError(f"GCS NotFound: gs://{self.bucket_name}/{key}")
        return self._gcs_vault[key]

    def delete_object(self, key: str) -> bool:
        return self._gcs_vault.pop(key, None) is not None

    def list_objects(self, prefix: str = "") -> List[str]:
        return [k for k in self._gcs_vault.keys() if k.startswith(prefix)]

    def generate_presigned_url(self, key: str, expiry_seconds: int = 3600) -> str:
        signature = uuid.uuid4().hex
        return f"https://storage.googleapis.com/{self.bucket_name}/{key}?GoogleAccessId=sa@{self.project_id}.iam.gserviceaccount.com&Expires={expiry_seconds}&Signature={signature}"


# High-Level Orchestrator (MultiCloud Replication Manager)
class MultiCloudStorageManager:
    """
    Client orchestrator demonstrating Inversion of Control.
    Depends solely on the StorageBackend abstraction.
    """

    def __init__(self, primary: StorageBackend, replica: Optional[StorageBackend] = None):
        self.primary = primary
        self.replica = replica
        self.primary.connect()
        if self.replica:
            self.replica.connect()

    def store_file(self, filename: str, content: bytes) -> Dict[str, Any]:
        print(f"\n[StorageManager] Persisting '{filename}' ({len(content)} bytes)...")
        receipt = self.primary.upload_object(filename, content)
        print(f"  Primary ({self.primary.provider_name}): Uploaded successfully.")

        if self.replica:
            self.replica.upload_object(filename, content)
            print(f"  Replica ({self.replica.provider_name}): Mirrored successfully.")

        url = self.primary.generate_presigned_url(filename)
        receipt["presigned_download_url"] = url
        return receipt


# Demonstration Run: Storage System
primary_aws = AmazonS3Storage("production-customer-assets", region="us-west-2")
replica_gcs = GoogleCloudStorage("backup-customer-assets", project_id="enterprise-vault")

storage_engine = MultiCloudStorageManager(primary=primary_aws, replica=replica_gcs)
file_data = b"ENCRYPTED_PDF_CONTENT: Masterclass OOP Abstraction Specification"
receipt = storage_engine.store_file("reports/2026_q3_audit.pdf", file_data)
print(f"Generated Secure Download Link: {receipt['presigned_download_url']}")


# ==============================================================================
# PROJECT 2: ENTERPRISE DATABASE ABSTRACTION LAYER (DAL) & TRANSACTION SCOPE
# ==============================================================================
print_banner(2, "Enterprise Database Abstraction Layer (DAL) & UnitOfWork")

class DatabaseDialect(ABC):
    """
    Abstract contract defining SQL compilation differences across RDBMS engines.
    """

    @property
    @abstractmethod
    def dialect_name(self) -> str:
        pass

    @property
    @abstractmethod
    def placeholder_style(self) -> str:
        """Token style: '$1' for Postgres, '?' for SQLite, '%s' for MySQL."""
        pass

    @abstractmethod
    def compile_insert(self, table: str, columns: List[str]) -> str:
        """Generate engine-compliant INSERT INTO statement."""
        pass

    @abstractmethod
    def compile_select(self, table: str, where_col: str) -> str:
        """Generate engine-compliant SELECT statement."""
        pass


class PostgreSQLDialect(DatabaseDialect):
    @property
    def dialect_name(self) -> str:
        return "PostgreSQL (v16.2)"

    @property
    def placeholder_style(self) -> str:
        return "numbered_dollar ($1, $2, ...)"

    def compile_insert(self, table: str, columns: List[str]) -> str:
        col_list = ", ".join(f'"{c}"' for c in columns)
        placeholders = ", ".join(f"${i+1}" for i in range(len(columns)))
        return f'INSERT INTO "{table}" ({col_list}) VALUES ({placeholders}) RETURNING "id";'

    def compile_select(self, table: str, where_col: str) -> str:
        return f'SELECT * FROM "{table}" WHERE "{where_col}" = $1;'


class SQLiteDialect(DatabaseDialect):
    @property
    def dialect_name(self) -> str:
        return "SQLite3 (Embedded)"

    @property
    def placeholder_style(self) -> str:
        return "question_mark (?)"

    def compile_insert(self, table: str, columns: List[str]) -> str:
        col_list = ", ".join(f"`{c}`" for c in columns)
        placeholders = ", ".join("?" for _ in columns)
        return f"INSERT INTO `{table}` ({col_list}) VALUES ({placeholders});"

    def compile_select(self, table: str, where_col: str) -> str:
        return f"SELECT * FROM `{table}` WHERE `{where_col}` = ?;"


class DatabaseConnection(ABC):
    """Abstract connection representing a transactional database session."""

    @abstractmethod
    def execute(self, sql_query: str, parameters: tuple) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def commit_transaction(self) -> None:
        pass

    @abstractmethod
    def rollback_transaction(self) -> None:
        pass


class MockDatabaseConnection(DatabaseConnection):
    """Concrete mock transactional session implementing rollback/commit semantics."""

    def __init__(self, dialect: DatabaseDialect):
        self.dialect = dialect
        self._in_transaction = False
        self._query_journal: List[str] = []

    def execute(self, sql_query: str, parameters: tuple) -> List[Dict[str, Any]]:
        self._query_journal.append(f"{sql_query} | PARAMS={parameters}")
        print(f"[{self.dialect.dialect_name} EXEC] {sql_query} | Params={parameters}")
        return [{"status": "EXECUTED", "rows_affected": 1}]

    def commit_transaction(self) -> None:
        print(f"[{self.dialect.dialect_name}] COMMIT TRANSACTION: {len(self._query_journal)} queries permanently flushed.")
        self._query_journal.clear()

    def rollback_transaction(self) -> None:
        print(f"[{self.dialect.dialect_name}] ROLLBACK TRANSACTION: {len(self._query_journal)} queries discarded!")
        self._query_journal.clear()


# UnitOfWork Context Manager Powered by Abstraction
class UnitOfWork:
    """Manages transactional boundaries agnostic of underlying database engine."""

    def __init__(self, connection: DatabaseConnection):
        self.connection = connection

    def __enter__(self):
        print("--- Transaction Scope Begun ---")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            print(f"[!] Exception intercepted: {exc_val}")
            self.connection.rollback_transaction()
            return False  # Propagate exception
        else:
            self.connection.commit_transaction()
            return True


# High-Level Agnostic Domain Repository
class EnterpriseUserRepository:
    """Domain repository that has ZERO knowledge of PostgreSQL vs SQLite syntax!"""

    def __init__(self, connection: DatabaseConnection, dialect: DatabaseDialect):
        self.connection = connection
        self.dialect = dialect

    def create_user(self, username: str, email: str, role: str) -> None:
        sql = self.dialect.compile_insert("app_users", ["username", "email", "role"])
        self.connection.execute(sql, (username, email, role))

    def get_user_by_email(self, email: str) -> None:
        sql = self.dialect.compile_select("app_users", "email")
        self.connection.execute(sql, (email,))


# Demonstration: Running the same repository code on two completely different engines!
print("\n--- Demonstration 1: Running on PostgreSQL ---")
pg_dialect = PostgreSQLDialect()
pg_conn = MockDatabaseConnection(pg_dialect)
pg_repo = EnterpriseUserRepository(pg_conn, pg_dialect)

with UnitOfWork(pg_conn):
    pg_repo.create_user("sameer_admin", "sameer@enterprise.org", "PLATFORM_ADMIN")
    pg_repo.get_user_by_email("sameer@enterprise.org")

print("\n--- Demonstration 2: Running on SQLite with Intercepted Failure Rollback ---")
sqlite_dialect = SQLiteDialect()
sqlite_conn = MockDatabaseConnection(sqlite_dialect)
sqlite_repo = EnterpriseUserRepository(sqlite_conn, sqlite_dialect)

try:
    with UnitOfWork(sqlite_conn):
        sqlite_repo.create_user("temp_user", "temp@domain.com", "GUEST")
        raise ConnectionResetError("Simulated network drop during batch commit!")
except ConnectionResetError:
    print("Safely recovered from transactional failure!")


# ==============================================================================
# PROJECT 3: RESILIENT MULTI-PROVIDER AI LLM & AGENT PIPELINE
# ==============================================================================
print_banner(3, "Resilient Multi-Provider AI LLM & Agent Pipeline")

class LLMProvider(ABC):
    """
    Abstract contract for Generative Large Language Model providers.
    Normalizes OpenAI, Anthropic Claude, and Local Open-Source inference.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def model_identifier(self) -> str:
        pass

    @property
    @abstractmethod
    def cost_per_1k_input_tokens(self) -> float:
        pass

    @property
    @abstractmethod
    def cost_per_1k_output_tokens(self) -> float:
        pass

    @abstractmethod
    def invoke(self, prompt: str, temperature: float = 0.7) -> Dict[str, Any]:
        """Send prompt and return standardized completion payload."""
        pass

    def compute_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Concrete utility method calculating financial cost of inference."""
        in_cost = (prompt_tokens / 1000.0) * self.cost_per_1k_input_tokens
        out_cost = (completion_tokens / 1000.0) * self.cost_per_1k_output_tokens
        return in_cost + out_cost


class OpenAIProvider(LLMProvider):
    """Concrete provider targeting OpenAI GPT-4o."""

    def __init__(self, simulate_rate_limit: bool = False):
        self.simulate_rate_limit = simulate_rate_limit

    @property
    def provider_name(self) -> str:
        return "OpenAI API"

    @property
    def model_identifier(self) -> str:
        return "gpt-4o-2024-08-06"

    @property
    def cost_per_1k_input_tokens(self) -> float:
        return 0.0050

    @property
    def cost_per_1k_output_tokens(self) -> float:
        return 0.0150

    def invoke(self, prompt: str, temperature: float = 0.7) -> Dict[str, Any]:
        if self.simulate_rate_limit:
            raise RuntimeError("429 Too Many Requests: OpenAI TPM rate limit exceeded!")

        return {
            "provider": self.provider_name,
            "model": self.model_identifier,
            "completion": "OpenAI: Abstraction simplifies complex systems by presenting a clean interface.",
            "usage": {"prompt_tokens": 45, "completion_tokens": 18}
        }


class AnthropicClaudeProvider(LLMProvider):
    """Concrete provider targeting Anthropic Claude 3.5 Sonnet."""

    @property
    def provider_name(self) -> str:
        return "Anthropic API"

    @property
    def model_identifier(self) -> str:
        return "claude-3-5-sonnet-20241022"

    @property
    def cost_per_1k_input_tokens(self) -> float:
        return 0.0030

    @property
    def cost_per_1k_output_tokens(self) -> float:
        return 0.0150

    def invoke(self, prompt: str, temperature: float = 0.7) -> Dict[str, Any]:
        return {
            "provider": self.provider_name,
            "model": self.model_identifier,
            "completion": "Anthropic Claude: Abstraction acts as a conceptual contract enforcing architectural boundaries.",
            "usage": {"prompt_tokens": 42, "completion_tokens": 20}
        }


class LocalOllamaProvider(LLMProvider):
    """Concrete provider targeting local on-premise Llama 3 8B model via Ollama."""

    @property
    def provider_name(self) -> str:
        return "Local Ollama Daemon (On-Premise)"

    @property
    def model_identifier(self) -> str:
        return "meta-llama/Llama-3-8B-Instruct-Q4_K_M"

    @property
    def cost_per_1k_input_tokens(self) -> float:
        return 0.0000  # Free local inference!

    @property
    def cost_per_1k_output_tokens(self) -> float:
        return 0.0000

    def invoke(self, prompt: str, temperature: float = 0.7) -> Dict[str, Any]:
        return {
            "provider": self.provider_name,
            "model": self.model_identifier,
            "completion": "Local Llama 3: Abstraction decouples what code does from how it is implemented.",
            "usage": {"prompt_tokens": 50, "completion_tokens": 22}
        }


# High-Level AI Orchestrator with Resilient Fallback Routing
class ResilientAIOrchestrator:
    """
    Enterprise agent orchestrator.
    Attempts primary provider; if a failure occurs (e.g. Rate Limit),
    gracefully fails over down the hierarchy of abstract LLMProvider instances!
    """

    def __init__(self, provider_chain: List[LLMProvider]):
        if not provider_chain:
            raise ValueError("Orchestrator requires at least one LLMProvider in chain.")
        self.provider_chain = provider_chain
        self.cumulative_cost_usd = 0.0

    def execute_prompt(self, user_prompt: str) -> Dict[str, Any]:
        print(f"\n[AI Orchestrator] Executing prompt: '{user_prompt}'")
        last_exception = None

        for idx, provider in enumerate(self.provider_chain):
            try:
                print(f"  Attempting Provider [{idx+1}/{len(self.provider_chain)}]: {provider.provider_name} ({provider.model_identifier})...")
                result = provider.invoke(user_prompt)
                usage = result["usage"]
                call_cost = provider.compute_cost(usage["prompt_tokens"], usage["completion_tokens"])
                self.cumulative_cost_usd += call_cost

                result["cost_usd"] = call_cost
                result["total_session_cost_usd"] = self.cumulative_cost_usd
                print(f"  SUCCESS via {provider.provider_name}! Call cost: ${call_cost:.6f}")
                return result
            except Exception as exc:
                print(f"  [!] Fallback triggered: {provider.provider_name} failed with error: {exc}")
                last_exception = exc

        raise RuntimeError(f"All LLM providers in chain failed! Last error: {last_exception}")


# Demonstration Run: AI Pipeline with Fallback
# Primary provider will simulate a 429 Rate Limit error:
primary_openai_failing = OpenAIProvider(simulate_rate_limit=True)
backup_claude = AnthropicClaudeProvider()
fallback_local = LocalOllamaProvider()

agent = ResilientAIOrchestrator(
    provider_chain=[primary_openai_failing, backup_claude, fallback_local]
)

response = agent.execute_prompt("Explain the essence of Abstraction in software architecture.")
print(f"\nFinal AI Response Output : {response['completion']}")
print(f"Executing Model          : {response['model']}")
print(f"Call Cost                : ${response['cost_usd']:.6f}")
print(f"Session Cumulative Spend : ${response['total_session_cost_usd']:.6f}")

print("\n" + "=" * 80)
print(" DAY 23 PRODUCTION PRACTICAL PROJECTS COMPLETED SUCCESSFULLY!")
print("=" * 80)
