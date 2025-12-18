#!/usr/bin/env python3
"""
DynamoDB Document Interface Example - boto3 resource API

DESCRIPTION:
This example demonstrates how to use the DynamoDB document interface (resource API) to:
- Create a table with partition key (PK) and sort key (SK)
- Add items with 2 additional attributes
- Query and scan the table
- Clean up by deleting the table

The document interface provides a higher-level abstraction that automatically handles
data type conversions and provides a more Pythonic way to work with DynamoDB.

USAGE EXAMPLES:
 Basic execution:
   python document_interface.py

TABLE SCHEMA:
- Table Name: Students-Document
- Partition Key: StudentId (String)
- Sort Key: CourseId (String)
- Attributes: StudentName (String), Grade (Number)
"""

import boto3
import time
from botocore.exceptions import ClientError

def main():
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
    
    table_name = 'Students-Document'
    
    print("DynamoDB Document Interface Demo")
    print("=" * 40)
    
    try:
        print("Creating table with PK and SK...")
        
        # Get back a Table object instead of low-level dict of TableDescription, thus more object oriented 
        # thus can do table.<methods>
        table = dynamodb.create_table(
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
        table.wait_until_exists()
        print("Table is now active")
        
        input(" Press any key to ... Add items to table with automatic type conversion")

        print("Adding items to table...")
        
        # Notice absence of {'S': 'STU001'} in Pythons list of dictionaries
        items = [
            {
                'StudentId': 'STU001',
                'CourseId': 'CS101',
                'StudentName': 'Alice Johnson',
                'Grade': 85
            },
            {
                'StudentId': 'STU001',
                'CourseId': 'MATH201',
                'StudentName': 'Alice Johnson',
                'Grade': 92
            },
            {
                'StudentId': 'STU002',
                'CourseId': 'CS101',
                'StudentName': 'Bob Smith',
                'Grade': 78
            }
        ]
        
        for item in items:
            table.put_item(Item=item)  # easier than low-level (no need to spacift table name)
            print(f"Added: {item['StudentId']} - {item['CourseId']}")
        
        input(" Press any key to ... Query items for StudentId 'STU001'")
        
        from boto3.dynamodb.conditions import Key
        
        # No ExpressionAttributeValues dict
        response = table.query(
            KeyConditionExpression=Key('StudentId').eq('STU001')
        )
        
        # Now returned Python dict with Python data types (not DDB attribute types)
        print(f"Found {response['Count']} items:")
        for item in response['Items']:
            print(f"  - {item['StudentName']}: {item['CourseId']} (Grade: {item['Grade']})")

        
        input(" Press any key to ... Querying STU001's CS101 course")

        # No ExpressionAttributeValues dict
        response = table.query(
            KeyConditionExpression=Key('StudentId').eq('STU001') & Key('CourseId').eq('CS101')
        )
        
        for item in response['Items']:
            print(f"  - {item['StudentName']}: {item['CourseId']} (Grade: {item['Grade']})")
        
        input(" Press any key to ... Scan all items")
        
        response = table.scan()
        
        print(f"Total items: {response['Count']}")
        for item in response['Items']:
            print(f"  - {item['StudentId']}: {item['StudentName']} - {item['CourseId']} (Grade: {item['Grade']})")
        
    except ClientError as e:
        print(f"Error: {e}")
    
    finally:
        # Clean up - delete table
        try:
            input(" Press any key to Deleting table '{table_name}'...")
            table.delete()
            print("Table deletion initiated")
            
            # Wait for table to be deleted
            table.wait_until_not_exists()
            print("Table successfully deleted")
            
        except ClientError as e:
            print(f"Error deleting table: {e}")

if __name__ == "__main__":
    main()







########################################################################################
########################################  Notes ########################################
########################################################################################

"""

# No ExpressionAttributeValues dict is required for 'simple' equality (automatically converts Python types to DynamoDB types)
response = table.query(
  KeyConditionExpression=Key('StudentId').eq('STU001')
)

# but can still use it if you want to write a string expression yourself, for example with functions like begins_with, or when combining multiple conditions
# The values are plain Python types, not wrapped in {'S': ...}
Example:
from boto3.dynamodb.conditions import Key

response = table.query(
    KeyConditionExpression="StudentId = :sid AND begins_with(CourseId, :prefix)",
    ExpressionAttributeValues={
        ':sid': 'STU001',
        ':prefix': 'CS'
    }
)


When you use the high-level (Document) interface in boto3 (i.e., dynamodb.Table(...).query(...)), the response is a Python dictionary, 
but the attribute values are already converted to native Python types. for oow-level it is still a python dict but with Attribute values 
in DDB attribute format

items = [
    {
        'StudentId': 'STU001',
        'CourseId': 'CS101',
        'StudentName': 'Alice Johnson',
        'Grade': 85
    },
    {
        'StudentId': 'STU001',
        'CourseId': 'MATH201',
        'StudentName': 'Alice Johnson',
        'Grade': 92
    },
    {
        'StudentId': 'STU002',
        'CourseId': 'CS101',
        'StudentName': 'Bob Smith',
        'Grade': 78
    }
]

"""
