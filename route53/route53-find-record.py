from urllib import response
"""route53-find-record

This script is intended for enumerating all Route53 zones and finding all records matching a provided IP or other target address.

Example:
        $ python3 iam-inactive-roles-report.py [--since YYYY-MM-DD] [--debug]
"""

import argparse
import boto3
import json
from progress.bar import Bar

def get_route53_zones(debug):
    client = boto3.client('route53')

    paginator = client.get_paginator('list_hosted_zones')
    zones_response = paginator.paginate().build_full_result()

    return zones_response['HostedZones']

def get_matching_records(debug, zoneid, target):
    client = boto3.client('route53')
    matches=[]
    paginator = client.get_paginator('list_resource_record_sets')
    zone_response = paginator.paginate(
        HostedZoneId=zoneid
    ).build_full_result()

    for record in zone_response['ResourceRecordSets']:
        if 'ResourceRecords' in record:
            for resourcerecord in record['ResourceRecords']:
                if resourcerecord['Value'] == target:
                    matches.append(record)

    return matches

################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--target',  help='Target ip or record', required=True)
    parser.add_argument('--debug', type=bool, help='Extra debug options', default=False)
    parser.add_argument('--silent', type=bool, help='Disable progress bar, handy for post processing like jq', default=False)

    args = parser.parse_args()
    zone_data=[]

    zones = get_route53_zones(args.debug)
    bar = Bar('Processing roles:', max = len(zones))

    for zone in zones:
        if args.silent == False: bar.next()

        zoneid = zone['Id'].split("/")[-1]

        matches = get_matching_records(args.debug, zoneid, args.target)
        if matches != []: zone_data.append(matches)

print(json.dumps(zone_data))