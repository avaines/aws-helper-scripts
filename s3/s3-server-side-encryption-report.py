"""s3-server-side-encryption-report

This script is intended for enumerating all S3 buckets to find out the staus of server-side encryption

Example:
        $ python s3-server-side-encryption-report.py
"""

import boto3
from progress.bar import Bar

def get_buckets():
    s3 = boto3.client('s3')
    buckets=s3.list_buckets()
    return [ b["Name"] for b in buckets['Buckets'] ]


def get_bucket_encryption_state(buckets):
    client = boto3.client('s3')
    bucket_encryption_status = {}

    bar = Bar('Processing buckets:', max = len(buckets) )

    for bucket in buckets:
        bar.next()
        try:
            response = client.get_bucket_encryption(
                Bucket=bucket
            )

            bucket_encryption_status[bucket] = response['ServerSideEncryptionConfiguration']['Rules'][0]['ApplyServerSideEncryptionByDefault']['SSEAlgorithm']

        except client.exceptions.ClientError:  # There is probably some more strict checking that could be done on top of this.
            bucket_encryption_status[bucket] = "None"

    return bucket_encryption_status



    # paginator = client.get_paginator('list_roles')
    # roles_response = paginator.paginate().build_full_result()

    # num_of_roles=len(roles_response['Roles'])+1
    # bar = Bar('Processing roles:', max = num_of_roles)
    # if num_of_roles > 50: print("This may take a while to process all", num_of_roles,"roles, please wait....")

    # for count, role in enumerate(roles_response['Roles']):
    #     bar.next()

    #     attached_policies = client.list_attached_role_policies(
    #         RoleName=role['RoleName']
    #     )

    #     if role['RoleName'] == "AmazonSSMRoleForAutomationAssumeQuickSetup":
    #         print()

    #     if len(attached_policies['AttachedPolicies']) == 0:
    #         roles.append(role)

    # print()
    # return roles


################################
if __name__ == "__main__":
    bucket_encryption_status = get_bucket_encryption_state( get_buckets() )

    print()
    print("Bucket encryption report:")

    for bucket in bucket_encryption_status.items():
        print( "%s, %s" % (bucket[0], bucket[1]) )
