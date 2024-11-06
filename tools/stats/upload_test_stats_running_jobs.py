import argparse
from pathlib import Path
import sys

from tools.stats.test_dashboard import upload_additional_info
from tools.stats.upload_stats_lib import get_s3_resource
from tools.stats.upload_test_stats import get_tests

def upload_for(workflow_id: str, workflow_attempt: int) -> None:
    test_cases = get_tests(workflow_id, workflow_attempt)

    # Flush stdout so that any errors in Rockset upload show up last in the logs.
    sys.stdout.flush()

    upload_additional_info(workflow_id, workflow_attempt, test_cases)

def read_s3():
    bucket_prefix = "workflows_failing_pending_upload"
    bucket = get_s3_resource().Bucket("gha-artifacts")
    objs = bucket.objects.filter(
        Prefix=bucket_prefix
    )
    workflows = [obj.key.split("/")[-1].split(".")[0] for obj in objs]
    for workflow_id in workflows:
        print(workflow_id)
        upload_for(workflow_id, 1)
        bucket.delete_objects(
            Delete={
                "Objects": [{"Key": f"{bucket_prefix}/{workflow_id}.txt"}],
                "Quiet": True,
            }
        )


if __name__ == "__main__":
    read_s3()
