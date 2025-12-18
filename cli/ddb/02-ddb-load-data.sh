#!/bin/bash

# Check if the required number of parameters is provided
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <table-name> <region-name>"
  exit 1
fi

tableName=$1
regionName=$2

echo "Writing data in a batch to DDB"

# Batch upload items from file
aws dynamodb batch-write-item --request-items file://request-items.json

echo "Script is complete."
