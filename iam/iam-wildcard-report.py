from urllib import response
"""iam-wildcard-report

This script is intended for enumerating all IAM policies where theres a wildcard based action.
Real handy for finding overly permissive IAM policies in a given AWS account

Example:
        $ python3 iam-wildcard-report.py
"""

import boto3
import json

from botocore.exceptions import ClientError

def get_wildcard_policies():
    policies = []
    client = boto3.client('iam')

    paginator = client.get_paginator('list_policies')
    policies_response = paginator.paginate(
        Scope='Local',
        OnlyAttached=True,
    ).build_full_result()

    num_of_policies=len(policies_response['Policies'])+1
    if num_of_policies > 100: print("This may take a while to process all", num_of_policies,"policies, please wait....")

    for count, policy in enumerate(policies_response['Policies']):
        print("Processing policy:", count+1, "of", num_of_policies)

        # The policy doesn't contain the actual policy document, get the latest version of it.
        policy_version = client.get_policy_version(
            PolicyArn=policy['Arn'],
            VersionId = client.get_policy(PolicyArn=policy['Arn'])['Policy']['DefaultVersionId']
        )

        filtered_policies=[]
        # Process the policy statements for any wildcard actions
        for statement in policy_version['PolicyVersion']['Document']['Statement']:
            # Check the statement is a dictionary and has an action element in it before checking if there are any actions matching the filter
            if ((type(statement) is dict) and "Action" in statement) and len(list(filter(lambda x: "*" in x, statement['Action']))) > 0 :
                filtered_policies.append(policy_version['PolicyVersion']['Document'])
                policies.append( {"name": policy['PolicyName'], "policy": filtered_policies, "policy_raw": json.dumps(filtered_policies)} )

    return policies


################################
if __name__ == "__main__":
    policies = get_wildcard_policies()
    print("The following policies contain wildcard actions:")
    print("------------------------------------------------")
    for policy in policies:
        print(policy["name"])
