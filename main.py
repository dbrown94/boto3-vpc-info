import boto3
import logging
import botocore
from prettytable import PrettyTable

# Set up logging to capture errors and debug information
logging.basicConfig(level=logging.INFO)


def get_vpc_info():
    try:
        # Initialize AWS EC2 client
        ec2_client = boto3.client('ec2')

        # Retrieve VPC information
        response = ec2_client.describe_vpcs()
        vpcs = response['Vpcs']
        vpc_info = []

        # this is to Process each VPC
        for vpc in vpcs:
            vpc_details = {
                'VpcId': vpc['VpcId'],
                'CidrBlock': vpc['CidrBlock'],
                'Tags': ', '.join([tag['Key'] + '=' + tag['Value'] for tag in vpc.get('Tags', [])])
            }

            # don't forget to Retrieve and process subnets within the VPC
            vpc_details['Subnets'] = get_subnets(ec2_client, vpc['VpcId'])

            # Retrieve and process security groups associated with the VPC
            vpc_details['SecurityGroups'] = get_security_groups(ec2_client, vpc['VpcId'])

            # Append VPC details to the list
            vpc_info.append(vpc_details)

        return vpc_info

    except botocore.exceptions.ClientError as e:
        logging.error("Error occurred during AWS operation: %s", e.response['Error']['Message'])
        return []
    except Exception as e:
        logging.error("Unexpected error occurred: %s", str(e))
        return []


def get_subnets(ec2_client, vpc_id):
    subnets_details = []
    try:
        subnets_response = ec2_client.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
        subnets = subnets_response['Subnets']
        for subnet in subnets:
            subnet_details = {
                'SubnetId': subnet['SubnetId'],
                'CidrBlock': subnet['CidrBlock'],
                'AvailabilityZone': subnet['AvailabilityZone']
            }
            subnets_details.append(subnet_details)
    except botocore.exceptions.ClientError as e:
        logging.error("Error retrieving subnets: %s", e.response['Error']['Message'])
    except Exception as e:
        logging.error("Unexpected error retrieving subnets: %s", str(e))
    return subnets_details


def get_security_groups(ec2_client, vpc_id):
    security_groups_details = []
    try:
        security_groups_response = ec2_client.describe_security_groups(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
        security_groups = security_groups_response['SecurityGroups']
        for sg in security_groups:
            sg_details = {
                'GroupId': sg['GroupId'],
                'GroupName': sg['GroupName'],
                'Description': sg['Description'],
                'InboundRules': sg['IpPermissions'],
                'OutboundRules': sg['IpPermissionsEgress']
            }
            security_groups_details.append(sg_details)
    except botocore.exceptions.ClientError as e:
        logging.error("Error retrieving security groups: %s", e.response['Error']['Message'])
    except Exception as e:
        logging.error("Unexpected error retrieving security groups: %s", str(e))
    return security_groups_details


if __name__ == "__main__":
    vpc_info = get_vpc_info()

    # Display information using PrettyTable
    for vpc in vpc_info:
        print(f"VPC ID: {vpc['VpcId']}")
        print(f"CIDR Block: {vpc['CidrBlock']}")
        print(f"Tags: {vpc['Tags']}")

        # Display subnets in a table
        subnet_table = PrettyTable(['Subnet ID', 'CIDR Block', 'Availability Zone'])
        for subnet in vpc['Subnets']:
            subnet_table.add_row([subnet['SubnetId'], subnet['CidrBlock'], subnet['AvailabilityZone']])
        print("\nSubnets:")
        print(subnet_table)

        # Display security groups in a table
        sg_table = PrettyTable(['Group ID', 'Group Name', 'Description'])
        for sg in vpc['SecurityGroups']:
            sg_table.add_row([sg['GroupId'], sg['GroupName'], sg['Description']])
        print("\nSecurity Groups:")
        print(sg_table)
        print("------------------------------------\n")

