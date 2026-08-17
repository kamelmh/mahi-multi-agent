#!/usr/bin/env python3
"""
MAHI Floci Integration — Local AWS services for development.

Provides S3-compatible file storage and DynamoDB-compatible session storage
using Floci (local AWS emulator) or fallback to local filesystem/JSON.

Usage:
    from floci_integration import S3Storage, DynamoSession

    # S3 storage
    s3 = S3Storage()
    s3.upload("my-bucket", "file.txt", b"content")
    data = s3.download("my-bucket", "file.txt")

    # DynamoDB sessions
    session = DynamoSession()
    session.save("session-123", {"user": "mahi", "state": "active"})
    data = session.load("session-123")
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Optional, Any
from datetime import datetime

MAHI_ROOT = Path(__file__).parent.resolve()
DATA_DIR = MAHI_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)


class S3Storage:
    """S3-compatible file storage using Floci or local fallback."""

    def __init__(self, endpoint_url: str = None):
        self.endpoint_url = endpoint_url or os.environ.get(
            "AWS_ENDPOINT_URL", "http://localhost:4566"
        )
        self.region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
        self._client = None
        self._available = None

    def _get_client(self):
        """Get boto3 S3 client (lazy import)."""
        if self._client is not None:
            return self._client
        try:
            import boto3
            self._client = boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                region_name=self.region,
                aws_access_key_id="test",
                aws_secret_access_key="test",
            )
            return self._client
        except ImportError:
            return None

    def is_available(self) -> bool:
        """Check if Floci S3 is available."""
        if self._available is not None:
            return self._available
        client = self._get_client()
        if not client:
            self._available = False
            return False
        try:
            client.list_buckets()
            self._available = True
        except Exception:
            self._available = False
        return self._available

    def upload(self, bucket: str, key: str, data: bytes) -> dict:
        """Upload file to S3 (or local fallback)."""
        if self.is_available():
            try:
                self._client.put_object(Bucket=bucket, Key=key, Body=data)
                return {"success": True, "backend": "s3", "bucket": bucket, "key": key}
            except Exception as e:
                return {"success": False, "error": str(e)}

        # Local fallback
        local_path = DATA_DIR / "s3" / bucket / key
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_bytes(data)
        return {"success": True, "backend": "local", "path": str(local_path)}

    def download(self, bucket: str, key: str) -> Optional[bytes]:
        """Download file from S3 (or local fallback)."""
        if self.is_available():
            try:
                response = self._client.get_object(Bucket=bucket, Key=key)
                return response["Body"].read()
            except Exception:
                return None

        # Local fallback
        local_path = DATA_DIR / "s3" / bucket / key
        if local_path.exists():
            return local_path.read_bytes()
        return None

    def list_files(self, bucket: str, prefix: str = "") -> list:
        """List files in S3 bucket."""
        if self.is_available():
            try:
                response = self._client.list_objects_v2(
                    Bucket=bucket, Prefix=prefix
                )
                return [
                    {"key": obj["Key"], "size": obj["Size"]}
                    for obj in response.get("Contents", [])
                ]
            except Exception:
                return []

        # Local fallback
        local_dir = DATA_DIR / "s3" / bucket / prefix
        if not local_dir.exists():
            return []
        return [
            {"key": str(f.relative_to(DATA_DIR / "s3" / bucket)), "size": f.stat().st_size}
            for f in local_dir.rglob("*")
            if f.is_file()
        ]

    def delete(self, bucket: str, key: str) -> bool:
        """Delete file from S3."""
        if self.is_available():
            try:
                self._client.delete_object(Bucket=bucket, Key=key)
                return True
            except Exception:
                return False

        # Local fallback
        local_path = DATA_DIR / "s3" / bucket / key
        if local_path.exists():
            local_path.unlink()
            return True
        return False


class DynamoSession:
    """DynamoDB-compatible session storage using Floci or local JSON fallback."""

    def __init__(self, endpoint_url: str = None):
        self.endpoint_url = endpoint_url or os.environ.get(
            "AWS_ENDPOINT_URL", "http://localhost:4566"
        )
        self.region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
        self.table_name = "mahi-sessions"
        self._client = None
        self._resource = None
        self._available = None
        self._local_store = {}

    def _get_resource(self):
        """Get boto3 DynamoDB resource (lazy import)."""
        if self._resource is not None:
            return self._resource, self._client
        try:
            import boto3
            self._resource = boto3.resource(
                "dynamodb",
                endpoint_url=self.endpoint_url,
                region_name=self.region,
                aws_access_key_id="test",
                aws_secret_access_key="test",
            )
            self._client = boto3.client(
                "dynamodb",
                endpoint_url=self.endpoint_url,
                region_name=self.region,
                aws_access_key_id="test",
                aws_secret_access_key="test",
            )
            return self._resource, self._client
        except ImportError:
            return None, None

    def _ensure_table(self):
        """Create DynamoDB table if it doesn't exist."""
        resource, client = self._get_resource()
        if not resource:
            return False
        try:
            client.describe_table(TableName=self.table_name)
            return True
        except Exception:
            try:
                resource.create_table(
                    TableName=self.table_name,
                    KeySchema=[{"AttributeName": "session_id", "KeyType": "HASH"}],
                    AttributeDefinitions=[
                        {"AttributeName": "session_id", "AttributeType": "S"}
                    ],
                    BillingMode="PAY_PER_REQUEST",
                )
                return True
            except Exception:
                return False

    def is_available(self) -> bool:
        """Check if Floci DynamoDB is available."""
        if self._available is not None:
            return self._available
        resource, client = self._get_resource()
        if not resource:
            self._available = False
            return False
        try:
            self._ensure_table()
            self._available = True
        except Exception:
            self._available = False
        return self._available

    def save(self, session_id: str, data: dict, ttl: int = 86400) -> dict:
        """Save session data."""
        data["_session_id"] = session_id
        data["_ttl"] = int(time.time()) + ttl
        data["_updated"] = datetime.now().isoformat()

        if self.is_available():
            try:
                table = self._resource.Table(self.table_name)
                table.put_item(Item={"session_id": session_id, **data})
                return {"success": True, "backend": "dynamodb", "session_id": session_id}
            except Exception as e:
                return {"success": False, "error": str(e)}

        # Local JSON fallback
        self._local_store[session_id] = data
        local_path = DATA_DIR / "sessions" / f"{session_id}.json"
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return {"success": True, "backend": "local", "path": str(local_path)}

    def load(self, session_id: str) -> Optional[dict]:
        """Load session data."""
        if self.is_available():
            try:
                table = self._resource.Table(self.table_name)
                response = table.get_item(Key={"session_id": session_id})
                return response.get("Item")
            except Exception:
                return None

        # Local fallback
        if session_id in self._local_store:
            return self._local_store[session_id]
        local_path = DATA_DIR / "sessions" / f"{session_id}.json"
        if local_path.exists():
            return json.loads(local_path.read_text(encoding="utf-8"))
        return None

    def delete(self, session_id: str) -> bool:
        """Delete session."""
        if self.is_available():
            try:
                table = self._resource.Table(self.table_name)
                table.delete_item(Key={"session_id": session_id})
                return True
            except Exception:
                return False

        # Local fallback
        self._local_store.pop(session_id, None)
        local_path = DATA_DIR / "sessions" / f"{session_id}.json"
        if local_path.exists():
            local_path.unlink()
            return True
        return False

    def list_sessions(self) -> list:
        """List all sessions."""
        if self.is_available():
            try:
                table = self._resource.Table(self.table_name)
                response = table.scan()
                return [
                    {"session_id": item["session_id"], "updated": item.get("_updated")}
                    for item in response.get("Items", [])
                ]
            except Exception:
                return []

        # Local fallback
        sessions_dir = DATA_DIR / "sessions"
        if not sessions_dir.exists():
            return []
        return [
            {"session_id": f.stem, "updated": None}
            for f in sessions_dir.glob("*.json")
        ]


class MAHIStorage:
    """Unified storage interface for MAHI system."""

    def __init__(self):
        self.s3 = S3Storage()
        self.sessions = DynamoSession()
        self._initialized = False

    def init(self) -> dict:
        """Initialize and check service availability."""
        self._initialized = True
        return {
            "s3": self.s3.is_available(),
            "dynamodb": self.sessions.is_available(),
            "mode": "floci" if (self.s3.is_available() and self.sessions.is_available()) else "local",
        }

    def save_agent_output(self, agent_id: str, task_id: str, output: str) -> dict:
        """Save agent output to S3."""
        bucket = "mahi-agent-outputs"
        key = f"{agent_id}/{task_id}.json"
        data = json.dumps({
            "agent_id": agent_id,
            "task_id": task_id,
            "output": output,
            "timestamp": datetime.now().isoformat(),
        }, ensure_ascii=False).encode("utf-8")
        return self.s3.upload(bucket, key, data)

    def load_agent_output(self, agent_id: str, task_id: str) -> Optional[dict]:
        """Load agent output from S3."""
        bucket = "mahi-agent-outputs"
        key = f"{agent_id}/{task_id}.json"
        data = self.s3.download(bucket, key)
        if data:
            return json.loads(data)
        return None

    def get_status(self) -> dict:
        """Get storage system status."""
        if not self._initialized:
            self.init()
        return {
            "s3_available": self.s3.is_available(),
            "dynamodb_available": self.sessions.is_available(),
            "endpoint": self.s3.endpoint_url,
            "local_fallback": DATA_DIR,
        }


# Global instance
storage = MAHIStorage()


def get_storage() -> MAHIStorage:
    """Get the global storage instance."""
    return storage


if __name__ == "__main__":
    print("MAHI Floci Integration")
    print("=" * 40)

    status = storage.init()
    print(f"Mode: {status['mode']}")
    print(f"S3: {'OK' if status['s3'] else 'LOCAL'}")
    print(f"DynamoDB: {'OK' if status['dynamodb'] else 'LOCAL'}")
    print(f"\nLocal data: {DATA_DIR}")

    # Test S3
    print("\n--- S3 Test ---")
    result = storage.s3.upload("test-bucket", "hello.txt", b"Hello from MAHI!")
    print(f"Upload: {result}")
    data = storage.s3.download("test-bucket", "hello.txt")
    print(f"Download: {data}")

    # Test DynamoDB
    print("\n--- DynamoDB Test ---")
    result = storage.sessions.save("test-session", {"user": "mahi", "state": "active"})
    print(f"Save: {result}")
    data = storage.sessions.load("test-session")
    print(f"Load: {data}")
