from urllib import response
"""iam-orphaned-policies-report

This script is intended for enumerating all IAM policies to find any policies with no attached roles, groups or users.
Real handy for finding orphaned IAM policies in a given AWS account.

Example:
        $ python3 iam-orphaned-policies-report.py
"""

import boto3
import json
from progress.bar import Bar

def get_orphaned_policies():

    client = boto3.client('iam')

    paginator = client.get_paginator('list_policies')
    policies_response = paginator.paginate(
        Scope='Local',
        OnlyAttached=False,
    ).build_full_result()

    num_of_policies=len(policies_response['Policies'])+1
    if num_of_policies > 100: print("This may take a while to process all", num_of_policies,"policies, please wait....")

    return [x for x in policies_response['Policies'] if x['AttachmentCount'] == 0]


################################
if __name__ == "__main__":
    policies = get_orphaned_policies()
    print("The following policies are orphaned:")
    print("------------------------------------------------")
    for policy in policies:
        print(policy['PolicyName'])
