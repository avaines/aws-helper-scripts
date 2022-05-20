"""ebs-vol-to-instance-report

This script is intended for enumerating a given list of EBS volumes and returning a statement of what instances they are connected to and their encryption status.

Example:
        $ python3 ebs-vol-to-instance-report.py
"""

import boto3

def get_ec2_instance_name(instance_id):
    client = boto3.client('ec2')
    try:
        response = client.describe_instances(
            InstanceIds=[instance_id]
        )

        name_tag=[tag for tag in response['Reservations'][0]['Instances'][0]['Tags'] if tag["Key"] == "Name"]

        return(name_tag[0]['Value'])
    except:
        return("no name")


# 1) is it attached to anything
def get_volume_info(volume):
    ec2 = boto3.resource('ec2')

    try:
        volume_obj = ec2.Volume(volume)

        # Does this instance have an attached instance?
        if isinstance(volume_obj.attachments, list):
            if len(volume_obj.attachments)>0:
                attachments = []
                encrypted_status = 'encrypted' if volume_obj.encrypted else 'not encrypted'
                for attachment in volume_obj.attachments:
                    # Lookup the ec2 instance name

                    attachments.append( "%s (%s)" % (attachment['InstanceId'], get_ec2_instance_name(attachment['InstanceId'])) )

                return ( "%s is %s and attached to %s" % (volume, encrypted_status, ", ".join(attachments)) )

            # It's not attached to anything
        else:
            if isinstance(volume_obj.tags, list):
                # It has tags
                return ( "%s is %s and isn't attached to anything but has a name tag to %s" % (volume, encrypted_status, ", ".join(attachments)) )

            else:
                # This volume doesnt have any instance attachments or a name tag. Good luck figuring this one out.
                return( "%s isn't attached to anything and doesn't have a name tag" % (volume) )

    except:
        return ("%s doesn't seem to exist" % (volume))


################################
if __name__ == "__main__":

    report_file = open("ebs-vols-report.txt", "a")
    with open('ebs-vols.txt', 'r') as file:
        for line in file:
            vol_data = get_volume_info(line.rstrip())
            print( vol_data )
            report_file.write(vol_data + "\n")

report_file.close()

