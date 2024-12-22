#!/usr/bin/env python3

# Created with ChatGPT
#
# Prompt Summary:
# This script attaches a specified IAM Permission Boundary policy to all IAM Users and Roles in an AWS account.
# Key details for script behavior:
# - Input: The full ARN of the IAM Policy to use as the Permission Boundary is required as a parameter.
# - Exclusions:
#   - AWS Service Roles are excluded (roles with "AWSServiceRoleFor" in their name).
#   - Roles managed by AWS Identity Center are excluded (roles starting with "AWSReservedSSO_").
# - Features:
#   - Dry-run mode: Add the --dry-run flag to simulate changes without applying them.
#   - Validation: The script validates the provided policy ARN before proceeding.
# - Output: Logs each action, including skipped roles, for transparency.
#
# Expected script implementation details:
# - Uses Python's `boto3` library to interact with AWS IAM.
# - The function `attach_permission_boundary` handles attaching the boundary to users and roles.
# - `list_users` and `list_roles` are used to retrieve IAM Users and Roles.
# - The script validates the policy ARN using `iam.get_policy`.
#
# Example usage:
# python3 attach_permission_boundary.py arn:aws:iam::123456789012:policy/my-permission-boundary-policy --dry-run

#!/usr/bin/env python3

import argparse
import boto3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def validate_policy_arn(iam_client, policy_arn):
    try:
        iam_client.get_policy(PolicyArn=policy_arn)
        logger.info(f"Validated policy ARN: {policy_arn}")
        return True
    except iam_client.exceptions.NoSuchEntityException:
        logger.error(f"Policy ARN {policy_arn} does not exist.")
        return False

def attach_permission_boundary(iam_client, policy_arn, dry_run):
    # List and process IAM users
    users = iam_client.list_users()['Users']
    for user in users:
        username = user['UserName']
        if dry_run:
            logger.info(f"[DRY-RUN] Would attach permission boundary to user: {username}")
        else:
            iam_client.put_user_permissions_boundary(
                UserName=username,
                PermissionsBoundary=policy_arn
            )
            logger.info(f"Attached permission boundary to user: {username}")

    # List and process IAM roles
    roles = iam_client.list_roles()['Roles']
    for role in roles:
        role_name = role['RoleName']
        if "AWSServiceRoleFor" in role_name or role_name.startswith("AWSReservedSSO_"):
            logger.info(f"Skipping excluded role: {role_name}")
            continue

        if dry_run:
            logger.info(f"[DRY-RUN] Would attach permission boundary to role: {role_name}")
        else:
            iam_client.put_role_permissions_boundary(
                RoleName=role_name,
                PermissionsBoundary=policy_arn
            )
            logger.info(f"Attached permission boundary to role: {role_name}")

def main():
    parser = argparse.ArgumentParser(description="Attach a specified IAM Permission Boundary policy to all IAM Users and Roles in an AWS account.")
    parser.add_argument("policy_arn", help="The full ARN of the IAM Policy to use as the Permission Boundary.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate changes without applying them.")

    args = parser.parse_args()

    iam_client = boto3.client("iam")

    # Validate the policy ARN
    if not validate_policy_arn(iam_client, args.policy_arn):
        logger.error("Exiting due to invalid policy ARN.")
        return

    # Attach the permission boundary
    attach_permission_boundary(iam_client, args.policy_arn, args.dry_run)

if __name__ == "__main__":
    main()

