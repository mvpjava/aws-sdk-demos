#!/usr/bin/env python3
"""
S3 Client API Example - Low-Level boto3 Operations

DESCRIPTION:
This script demonstrates how to use the low-level boto3 client API to perform basic S3 operations.
It creates an S3 bucket with a random suffix, uploads a sample object, and lists all objects
in the bucket using the list_objects_v2 function with a for loop.

USAGE EXAMPLES:
1. Basic execution:
   python s3_client_example.py

OUTPUT:
The script will display:
- Bucket creation confirmation
- Object upload status
- Detailed list of all objects in the bucket with metadata
"""

import boto3
import sys
import random
import string
from botocore.exceptions import ClientError

def main():
    region = 'eu-west-2'
    
    # Initialize S3 client with region
    s3_client = boto3.client('s3', region_name=region)
    
    # Generate random suffix for bucket name (must be globally unique)
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    bucket_name = f'my-demo-bucket-client-{random_suffix}'
    
    try:
        # Create S3 bucket
        print(f"Creating bucket: {bucket_name} in region: {region}")
        
        if region == 'us-east-1':
            # us-east-1 doesn't need CreateBucketConfiguration
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            # Other regions need LocationConstraint
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        print(f"Bucket '{bucket_name}' created successfully")
        
        # Upload a sample object for demonstration
        print("Uploading sample object...")
        s3_client.put_object(
            Bucket=bucket_name,
            Key='sample-file.txt',
            Body=b'Hello from S3 client example!'
        )
        print("Sample object uploaded")
        
        # List objects in bucket using list_objects_v2
        print(f"\nListing objects in bucket '{bucket_name}':")
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        
        if 'Contents' in response:
            for obj in response['Contents']:
                print(f"  - Key: {obj['Key']}")
                print(f"  - Storage Class: {obj['StorageClass']}")
                print(f"    Size: {obj['Size']} bytes")
                print(f"    Last Modified: {obj['LastModified']}")
                print()
        else:
            print("  No objects found in bucket")
            
    except ClientError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


"""
Example of the reposnce object returned by s3_client.list_objects_v2(..)
{
    'IsTruncated': False,
     # Contents is a list of dictionaries
    'Contents': [
        {
            'Key': 'example-file.txt',
            'LastModified': datetime.datetime(2023, 1, 1, 12, 0, 0, tzinfo=tzutc()),
            'ETag': '"9a0364b9e99bb480dd4a5a6a7e8f3e",  # The ETag of the object
            'Size': 1024,  # Size of the object in bytes
            'StorageClass': 'STANDARD',
            'Owner': {
                'DisplayName': 'owner-name',
                'ID': 'owner-id'
            }
        },
        {
           # You can have multiple objects here
        }
    ],
    'Name': 'your-bucket-name',
    'Prefix': '',
    'MaxKeys': 1000,
    'CommonPrefixes': [],
    'EncodingType': 'url',
    'Delimiter': ''
}
"""