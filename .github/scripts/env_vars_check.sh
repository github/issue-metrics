#!/bin/bash

# Find all test_*.py files
files=$(find . -name "test_*.py")
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Loop through each file
for file in $files; do
     # Search for instances of get_env_vars() with no arguments
     result=$(grep -n "get_env_vars()" "$file")

     # If any instances are found, print the file name and line number
     if [ -n "$result" ]; then
         echo "Found in $file:"
         echo "$result"
         echo -e "${RED}ERROR: get_env_vars() should always set test=True in test*.py files.${NC}"
         exit 1
     fi
done
echo -e "   ${GREEN}PASS:${NC} All test*.py files call get_env_vars() with test=True."
