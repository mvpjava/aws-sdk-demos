#!/bin/bash

# Check if the required number of parameters is provided
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <table-name> <region-name>"
  exit 1
fi

tableName=$1
regionName=$2

set -x

# Retrieve all of Alberts notes (search criteria specified by "-key-condition-expression") ...
aws dynamodb query \
  --table-name "$tableName" \
  --key-condition-expression "UserId = :user" \
  --expression-attribute-values '{":user": {"S": "Albert"}}' \
  --return-consumed-capacity TOTAL --output json

echo "Press any key to continue ..."
read anykey

# Same query but a consistent read (double the RCU)
aws dynamodb query \
  --table-name "$tableName" \
  --key-condition-expression "UserId = :user" \
  --expression-attribute-values '{":user": {"S": "Albert"}}' \
  --consistent-read \
  --return-consumed-capacity TOTAL --output json

echo "Press any key to continue ..."
read anykey

# Retrieve all of Alberts notes which have a NoteId grater than 3...
aws dynamodb query \
  --table-name "$tableName" \
  --key-condition-expression "UserId = :userId AND NoteId > :noteId" \
  --return-consumed-capacity TOTAL \
  --expression-attribute-values '{
    ":userId": {"S":"Albert"},
    ":noteId": {"N":"3"}
  }' \
  --output json

echo "Press any key to continue ..."
read anykey

#Scan the entire table!
aws dynamodb scan --table-name "$tableName" --return-consumed-capacity TOTAL --output json

echo "Press any key to continue ..."
read anykey

# Dont be fooled, still a full scan (even though there is a filter)!
# Will return "6  26" which means returned 6 records but there it took 26 RCU
aws dynamodb scan \
  --table-name "$tableName" \
  --filter-expression "Favorite = :value" \
  --return-consumed-capacity TOTAL \
  --expression-attribute-values '{
    ":value": {"S": "Yes"}
  }' \
  --output json

echo "Press any key to continue ..."
read anykey


# find Marie's favorite Note(s) with LSI  (more efficient than using sort key with added filter)
aws dynamodb query \
  --table-name "$tableName" \
  --index-name Favorite-LSI \
  --key-condition-expression "UserId = :user and Favorite = :favorite" \
  --expression-attribute-values '{":user": {"S": "Marie"}, ":favorite": {"S": "Yes"}}' \
  --return-consumed-capacity TOTAL \
  --output json

set *x

echo "Script is complete."
