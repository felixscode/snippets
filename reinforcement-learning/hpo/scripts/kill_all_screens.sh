#!/bin/bash

# Check if a regex pattern is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <regex_pattern>"
    exit 1
fi

PATTERN=$1

# List all screen sessions and filter by the given pattern
screen -ls | grep -E "$PATTERN" | awk '{print $1}' | while read -r session_id; do
    # Kill each matching screen session
    screen -S "$session_id" -X quit
    echo "Killed screen session: $session_id"
done