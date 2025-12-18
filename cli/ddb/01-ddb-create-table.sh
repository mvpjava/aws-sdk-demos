#!/bin/bash

# Check if the required number of parameters is provided
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <table-name> <region-name>"
  exit 1
fi

tableName=$1
regionName=$2

# Execute the create-table command
# Would be better to have it read from .json file since more readable....
# aws dynamodb create-table --cli-input-json file://notestable.json --region us-west-2
aws dynamodb create-table \
  --table-name "$tableName" \
  --attribute-definitions AttributeName=UserId,AttributeType=S AttributeName=NoteId,AttributeType=N AttributeName=Favorite,AttributeType=S \
  --key-schema AttributeName=UserId,KeyType=HASH AttributeName=NoteId,KeyType=RANGE \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
  --local-secondary-indexes "IndexName=Favorite-LSI,KeySchema=[{AttributeName=UserId,KeyType=HASH},{AttributeName=Favorite,KeyType=RANGE}],Projection={ProjectionType=ALL}" \
  --region "$regionName"

echo "Waiting for feedback that table has been created ..."
# Check the status of the create-table operation (optional)
aws dynamodb wait table-exists --table-name "$tableName" --region "$regionName"

# List all tables in the region
aws dynamodb list-tables --region "$regionName"

# Add 2 items
aws dynamodb put-item \
  --table-name "$tableName" \
  --item '{
    "UserId": {"S": "Andy"},
    "NoteId": {"N": "42"},
    "Notes": {"S": "I love AWS!"},
    "Favorite": {"S": "Yes"}
  }'


# Execute the update-table command to change RCU and WCU
aws dynamodb update-table \
  --table-name "$tableName" \
  --provisioned-throughput ReadCapacityUnits=18,WriteCapacityUnits=8 \
  --region "$regionName"

echo "script complete."
