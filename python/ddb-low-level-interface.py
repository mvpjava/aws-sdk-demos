#!/usr/bin/env python3
"""
DynamoDB Low-Level Interface Example - boto3 client API

DESCRIPTION:
This example demonstrates how to use the DynamoDB low-level interface (client API) to:
- Create a table with partition key (PK) and sort key (SK)
- Add items with 2 additional attributes
- Query and scan the table
- Clean up by deleting the table

The low-level interface provides direct access to DynamoDB API operations and requires
you to specify data types explicitly (e.g., 'S' for String, 'N' for Number).

KEY FEATURES:
- Uses boto3.client('dynamodb') for low-level operations
- Explicit data type specification required
- Direct mapping to DynamoDB API
- Full control over all DynamoDB features
- More verbose but most flexible approach

USAGE EXAMPLES:
 Basic execution:
   python low_level_interface.py

TABLE SCHEMA:
- Table Name: Students-LowLevel
- Partition Key: StudentId (String)
- Sort Key: CourseId (String)
- Attributes: StudentName (String), Grade (Number)

OUTPUT:
- Table creation status
- Item insertion confirmations
- Query results showing all items
- Table deletion confirmation
"""

import boto3
import time
from botocore.exceptions import ClientError

def main():
    # Initialize DynamoDB client (low-level interface)
    dynamodb = boto3.client('dynamodb', region_name='eu-west-2')
    
    table_name = 'Students-LowLevel'
    
    print("DynamoDB Low-Level Interface Demo")
    print("=" * 40)
    
    try:
        # 1. Create table with partition key and sort key
        print("1. Creating table with PK and SK...")
        
        response = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'StudentId',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'CourseId',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'StudentId',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'CourseId',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        print(f"Table '{table_name}' creation initiated")
        
        print("Waiting for table to become active...")
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=table_name)
        print("Table is now active")
        
        input(" Press any key to ... Add items to table.")
        
        items = [
            {
                'StudentId': {'S': 'STU001'},
                'CourseId': {'S': 'CS101'},
                'StudentName': {'S': 'Sam Johnson'},
                'Grade': {'N': '85'}
            },
            {
                'StudentId': {'S': 'STU001'},
                'CourseId': {'S': 'MATH201'},
                'StudentName': {'S': 'Sam Johnson'},
                'Grade': {'N': '92'}
            },
            {
                'StudentId': {'S': 'STU002'},
                'CourseId': {'S': 'CS101'},
                'StudentName': {'S': 'Bob Molson'},
                'Grade': {'N': '78'}
            }
        ]
        
        for item in items:
            dynamodb.put_item(
                TableName=table_name,
                Item=item
            )
            student_id = item['StudentId']['S']  
            course_id = item['CourseId']['S']
            print(f"Added: {student_id} - {course_id}")
        
        input(" Press any key to ... Querying items for StudentId 'STU001'")
        
        response = dynamodb.query(
            TableName=table_name,
            KeyConditionExpression='StudentId = :student_id', 
            ExpressionAttributeValues={
                ':student_id': {'S': 'STU001'}
            }
        )
        
        print(f"Found {response['Count']} items:")
        for item in response['Items']:
            student_name = item['StudentName']['S']
            course_id = item['CourseId']['S']
            grade = item['Grade']['N']
            print(f"  - {student_name}: {course_id} (Grade: {grade})")

        
        input(" Press any key to ... Scan all items in table.")

        response = dynamodb.scan(TableName=table_name)
        
        print(f"Total items: {response['Count']}")
        for item in response['Items']:
            student_id = item['StudentId']['S']
            course_id = item['CourseId']['S']
            student_name = item['StudentName']['S']
            grade = item['Grade']['N']
            print(f"  - {student_id}: {student_name} - {course_id} (Grade: {grade})")
        
    except ClientError as e:
        print(f"Error: {e}")
    
    finally:
        # Clean up - delete table
        try:
            input(" Press any key to ... Delete table '{table_name}'")

            dynamodb.delete_table(TableName=table_name)
            waiter = dynamodb.get_waiter('table_not_exists')
            waiter.wait(TableName=table_name)
            print("Table successfully deleted")
            
        except ClientError as e:
            print(f"Error deleting table: {e}")

if __name__ == "__main__":
    main()


########################################################################################
########################################  Notes ########################################
########################################################################################

# Explaination for line of code "student_id = item['StudentId']['S']"
    # item['StudentId'] → {'S': 'STU001'}
    # ['S'] → extract the string value
    # Result → 'STU001'

"""

# Can only use partition key + sort key in 'KeyConditionExpression'
# and can perform logic like examples (not show below but would then also need to include attributes in ExpressionAttributeValues)...
# KeyConditionExpression='StudentId = :sid AND CourseId = :cid'
# KeyConditionExpression='StudentId = :sid AND begins_with(CourseId, :prefix)'
# KeyConditionExpression='StudentId = :sid AND CourseId BETWEEN :c1 AND :c2'

        response = dynamodb.query(
            TableName=table_name,
            KeyConditionExpression='StudentId = :student_id', 
            ExpressionAttributeValues={
                ':student_id': {'S': 'STU001'}
            }
        )
"""

"""

The response object once performing a "dynamodb.query" looks like this ..

response = {
    'Items': [
        {
            'StudentId': {'S': 'STU001'},
            'CourseId': {'S': 'CS101'},
            'StudentName': {'S': 'Sam Johnson'},
            'Grade': {'N': '85'}
        },
        {
            'StudentId': {'S': 'STU001'},
            'CourseId': {'S': 'MATH201'},
            'StudentName': {'S': 'Sam Johnson'},
            'Grade': {'N': '92'}
        }
    ],
    'Count': 2,
    'ScannedCount': 2,
    'ResponseMetadata': {
        'RequestId': 'example-request-id',
        'HTTPStatusCode': 200,
        'HTTPHeaders': {
            'content-type': 'application/x-amz-json-1.0',
            'date': 'Mon, 18 Dec 2025 12:00:00 GMT'
        },
        'RetryAttempts': 0
    }
}


Why use low-level?
1) full control if needed 
2) Access to ResponseMetadata (Low-level client gives full HTTP response headers, request IDs, retries, throttling info)
3) work with binary data
"""
