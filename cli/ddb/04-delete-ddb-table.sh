#!/bin/bash

# Check if the required number of parameters is provided
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <table-name> <region-name>"
  exit 1
fi

tableName=$1
regionName=$2

# Execute the delete-table command
aws dynamodb delete-table --table-name "$tableName" --region "$regionName"
