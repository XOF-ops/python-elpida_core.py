from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Dict, List


@dataclass(slots=True)
class ElpidaBuckets:
    mind: str = "elpida-consciousness"
    federation: str = "elpida-body-evolution"
    world: str = "elpida-external-interfaces"


class S3Client:
    """Minimal read-only S3 helper for SDK phase 1."""

    def __init__(self) -> None:
        try:
            import boto3  # type: ignore
        except Exception as e:  # pragma: no cover
            raise RuntimeError("boto3 is required for S3Client") from e
        self._s3 = boto3.client("s3")
        self.buckets = ElpidaBuckets()

    def list_keys(self, bucket: str, prefix: str, limit: int = 50) -> List[str]:
        resp = self._s3.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=limit)
        contents = resp.get("Contents", [])
        return [str(obj.get("Key", "")) for obj in contents if obj.get("Key")]

    def head_object(self, bucket: str, key: str) -> Dict[str, Any]:
        return self._s3.head_object(Bucket=bucket, Key=key)

    def read_text(self, bucket: str, key: str) -> str:
        resp = self._s3.get_object(Bucket=bucket, Key=key)
        body = resp["Body"].read()
        return body.decode("utf-8")

    def read_json(self, bucket: str, key: str) -> Dict[str, Any]:
        text = self.read_text(bucket=bucket, key=key)
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError(f"expected JSON object at s3://{bucket}/{key}")
        return data

    def read_jsonl(self, bucket: str, key: str, limit: int = 20) -> List[Dict[str, Any]]:
        if limit <= 0:
            return []
        text = self.read_text(bucket=bucket, key=key)
        lines = [ln for ln in text.splitlines() if ln.strip()]
        out: List[Dict[str, Any]] = []
        for ln in lines[-limit:]:
            item = json.loads(ln)
            if isinstance(item, dict):
                out.append(item)
        return out
