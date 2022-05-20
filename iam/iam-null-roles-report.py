"""iam-null-roles-report

This script is intended for enumerating all IAM roles to find those with no attached permissions.
Real handy for finding null IAM roles in a given AWS account.

Example:
        $ python3 iam-null-roles-report.py
"""

import boto3
from progress.bar import Bar


def get_null_roles():
    roles = []
    client = boto3.client('iam')

    paginator = client.get_paginator('list_roles')
    roles_response = paginator.paginate().build_full_result()

    num_of_roles=len(roles_response['Roles'])+1
    bar = Bar('Processing roles:', max = num_of_roles)
    if num_of_roles > 50: print("This may take a while to process all", num_of_roles,"roles, please wait....")

    for count, role in enumerate(roles_response['Roles']):
        bar.next()

        attached_policies = client.list_attached_role_policies(
            RoleName=role['RoleName']
        )

        if role['RoleName'] == "AmazonSSMRoleForAutomationAssumeQuickSetup":
            print()

        if len(attached_policies['AttachedPolicies']) == 0:
            roles.append(role)

    print()
    return roles


################################
if __name__ == "__main__":
    roles = get_null_roles()
    print("The following roles have no permissions or policies attached:")
    print("------------------------------------------------")
    for role in roles:
        print(role["RoleName"])
