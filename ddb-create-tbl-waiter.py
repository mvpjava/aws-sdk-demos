#!/usr/bin/env python3

"""
Purpose

Demonstrate creating a DynamoDB table with a simple primary key and waiting for it to be created.
"""

import boto3
from botocore.exceptions import ClientError


def create_table_and_wait(dynamodb_client, table_name):
    """
    Creates a DynamoDB table with a string primary key called 'id' and waits for creation.
    
    :param dynamodb_client: A Boto3 DynamoDB client
    :param table_name: The name of the table to create
    """
    try:
        print(f"Creating DynamoDB table: {table_name}")
        
        # Create table with minimal configuration
        response = dynamodb_client.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'  # Primary key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'  # String
                }
            ],
            BillingMode='PAY_PER_REQUEST'  # On-demand billing (no need to specify capacity)
        )
        
        print(f"Table creation initiated. Status: {response['TableDescription']['TableStatus']}")
        
        # Wait for table to be created
        print("Waiting for table to be created...")
        waiter = dynamodb_client.get_waiter('table_exists')
        waiter.wait(
            TableName=table_name,
            WaiterConfig={
                'Delay': 2,  # Check every 2 seconds
                'MaxAttempts': 30  # Wait up to 60 seconds
            }
        )
        
        print(f"Table '{table_name}' has been created successfully!")
        
        # Get final table status
        table_info = dynamodb_client.describe_table(TableName=table_name)
        print(f"Table status: {table_info['Table']['TableStatus']}")
        print(f"Table ARN: {table_info['Table']['TableArn']}")
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceInUseException':
            print(f"Table '{table_name}' already exists!")
        else:
            print(f"Error creating table: {e.response['Error']['Message']}")
        raise


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Create a DynamoDB table and wait for it to be ready')
    parser.add_argument('table_name', help='Name of the DynamoDB table to create')
    parser.add_argument('--region', default='us-east-1', help='AWS region (default: us-east-1)')
    
    args = parser.parse_args()
    
    # Create DynamoDB client
    dynamodb_client = boto3.client('dynamodb', region_name=args.region)
    
    try:
        create_table_and_wait(dynamodb_client, args.table_name)
    except ClientError:
        print("Exiting due to error.")


if __name__ == "__main__":
    main()