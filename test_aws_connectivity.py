#!/usr/bin/env python3
"""Quick AWS connectivity test with per-service timeouts."""
import boto3
from botocore.config import Config

TIMEOUT_CFG = Config(
    connect_timeout=10,
    read_timeout=10,
    retries={"max_attempts": 1},
)

def test_s3():
    print("── S3 (us-east-1) ──")
    try:
        s3 = boto3.client("s3", region_name="us-east-1", config=TIMEOUT_CFG)
        resp = s3.list_objects_v2(Bucket="elpida-consciousness", MaxKeys=5)
        keys = [o["Key"] for o in resp.get("Contents", [])]
        print(f"  OK: {len(keys)} objects listed")
        for k in keys:
            print(f"    {k}")
    except Exception as e:
        print(f"  FAIL: {e}")

def test_eventbridge():
    print("── EventBridge (us-east-1) ──")
    try:
        eb = boto3.client("events", region_name="us-east-1", config=TIMEOUT_CFG)
        rule = eb.describe_rule(Name="elpida-scheduled-run")
        print(f"  Schedule: {rule['ScheduleExpression']}")
        print(f"  State: {rule['State']}")
    except Exception as e:
        print(f"  FAIL: {type(e).__name__}: {e}")

def test_ecs():
    print("── ECS (us-east-1) ──")
    try:
        ecs = boto3.client("ecs", region_name="us-east-1", config=TIMEOUT_CFG)
        clusters = ecs.list_clusters()
        print(f"  Clusters: {clusters['clusterArns']}")
    except Exception as e:
        print(f"  FAIL: {type(e).__name__}: {e}")

def test_ecs_tasks():
    print("── ECS Tasks (us-east-1) ──")
    try:
        ecs = boto3.client("ecs", region_name="us-east-1", config=TIMEOUT_CFG)
        tasks = ecs.list_tasks(cluster="elpida-cluster")
        print(f"  Running tasks: {tasks['taskArns']}")
        # Also check recent task runs
        tasks_stopped = ecs.list_tasks(cluster="elpida-cluster", desiredStatus="STOPPED")
        print(f"  Stopped tasks: {len(tasks_stopped['taskArns'])}")
    except Exception as e:
        print(f"  FAIL: {type(e).__name__}: {e}")

def test_cloudwatch_logs():
    print("── CloudWatch Logs (us-east-1) ──")
    try:
        logs = boto3.client("logs", region_name="us-east-1", config=TIMEOUT_CFG)
        streams = logs.describe_log_streams(
            logGroupName="/ecs/elpida-consciousness",
            orderBy="LastEventTime",
            descending=True,
            limit=3,
        )
        for s in streams.get("logStreams", []):
            print(f"  Stream: {s['logStreamName']}")
            from datetime import datetime
            if "lastEventTimestamp" in s:
                ts = datetime.fromtimestamp(s["lastEventTimestamp"] / 1000)
                print(f"    Last event: {ts.isoformat()}")
    except Exception as e:
        print(f"  FAIL: {type(e).__name__}: {e}")

def test_s3_memory():
    print("── S3 Memory File (us-east-1) ──")
    try:
        s3 = boto3.client("s3", region_name="us-east-1", config=TIMEOUT_CFG)
        # Check for evolution memory
        resp = s3.list_objects_v2(
            Bucket="elpida-consciousness",
            Prefix="ElpidaAI/elpida_evolution_memory",
            MaxKeys=5,
        )
        for o in resp.get("Contents", []):
            size_mb = o["Size"] / (1024 * 1024)
            print(f"  {o['Key']}: {size_mb:.1f} MB, modified {o['LastModified']}")
    except Exception as e:
        print(f"  FAIL: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_s3()
    test_s3_memory()
    test_eventbridge()
    test_ecs()
    test_ecs_tasks()
    test_cloudwatch_logs()
    print("\nDone.")
