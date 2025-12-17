#!/usr/bin/env python3
"""
S3 Resource API Example - High-Level boto3 Operations

DESCRIPTION:
This script demonstrates how to use the high-level boto3 resource API to perform basic S3 operations.
It creates an S3 bucket with a random suffix, uploads a sample object, and lists all objects
in the bucket using the resource's objects collection with a for loop.


USAGE EXAMPLES:
1. Basic execution:
   python s3_resource_example.py

OUTPUT:
The script will display:
- Bucket creation confirmation
- Object upload status
- List of all objects in the bucket with metadata

COMPARISON WITH CLIENT API:
- Resource API is more object-oriented
- Client API provides more granular control and access to all AWS API features
- Resource API abstracts away some complexity but may have fewer features
"""

import boto3
import sys
import random
import string
from botocore.exceptions import ClientError

def main():
    # Specify AWS region
    region = 'eu-west-2'
    
    # Initialize S3 resource with region
    s3_resource = boto3.resource('s3', region_name=region)
    
    # Generate random suffix for bucket name (must be globally unique)
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    bucket_name = f'my-demo-bucket-resource-{random_suffix}'
    
    try:
        print(f"Creating bucket: {bucket_name} in region: {region}")
        
        if region == 'us-east-1':
            bucket = s3_resource.create_bucket(Bucket=bucket_name)
        else:
            bucket = s3_resource.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        print(f"Bucket '{bucket_name}' created successfully")
        
        # Upload a sample object for demonstration
        print("Uploading sample object...")
        bucket.put_object(
            Key='sample-file.txt',
            Body=b'Hello from S3 resource example!'
        )
        print("Sample object uploaded")
        
        # List objects in bucket using for loop (high-level resource API)
        print(f"\nListing objects in bucket '{bucket_name}':")
        
        # Using the bucket's objects collection with for loop
        for obj in bucket.objects.all():
            print(f"  - Key: {obj.key}")
            print(f"  - Storage Class: {obj.storage_class}")
            print(f"    Size: {obj.size} bytes")
            print(f"    Last Modified: {obj.last_modified}")
            print()
            
    except ClientError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()