from urllib import response
"""iam-inactive-roles-report

This script is intended for enumerating all IAM roles to find those with no activity or no activity in since a given date.
Real handy for finding null IAM roles in a given AWS account.

Example:
        $ python3 iam-inactive-roles-report.py [--since YYYY-MM-DD] [--debug]
"""

import argparse
import boto3
import datetime
from progress.bar import Bar

def get_inactive_roles(debug,since):
    since_timestamp = datetime.datetime.strptime(since, '%Y-%m-%d').timestamp()

    roles = []
    client = boto3.client('iam')

    paginator = client.get_paginator('list_roles')
    roles_response = paginator.paginate().build_full_result()

    num_of_roles=len(roles_response['Roles'])+1
    bar = Bar('Processing roles:', max = num_of_roles)
    if num_of_roles > 50: print("This may take a while to process all", num_of_roles,"roles, please wait....")

    for count, role in enumerate(roles_response['Roles']):
        bar.next()

        role_info = client.get_role(
            RoleName=role['RoleName']
        )

        if "aws-service-role" not in role['Path']:
            if "LastUsedDate" in role_info['Role']['RoleLastUsed']:
                lastused_timestamp=role_info['Role']['RoleLastUsed']['LastUsedDate'].timestamp()
                if lastused_timestamp < since_timestamp:
                    if debug: print(role,"was last used before the target date")
                    roles.append(role)
                # There is a last used date
            else:
                # This role has no last used date meaning it has never been used
                if debug: print(role['RoleName'],"has never been used")
                roles.append(role)

    print()
    return roles


################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--since',  help='Role last use date in format YYYY-MM-DD', default="1970-01-01")
    parser.add_argument('--debug', type=bool, help='Extra debug options', default=False)
    args = parser.parse_args()

    roles = get_inactive_roles(args.debug, args.since)
    print("The following roles have no permissions or policies attached:")
    print("------------------------------------------------")
    for role in roles:
        print(role['RoleName'])
