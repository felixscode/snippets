#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <number_of_sessions> <pyhton_interpreter> <python_file>"
    exit 1
fi

# Get the number of sessions and the Python file from the arguments
NUM_SESSIONS=$1
PYTHON_INTERPRETER=$2
PYTHON_FILE=$3

# Check if the Python file exists
if [ ! -f "$PYTHON_FILE" ]; then
    echo "Error: Python file '$PYTHON_FILE' not found!"
    exit 1
fi

# Check if the Python interpreter exists
if ! command -v "$PYTHON_INTERPRETER" &> /dev/null; then
    echo "Error: Python interpreter '$PYTHON_INTERPRETER' not found!"
    exit 1
fi

# Start the specified number of screen sessions and run the Python file in each
for i in $(seq 1 $NUM_SESSIONS); do
    screen -dmS "session_$i" bash -c "$PYTHON_INTERPRETER $PYTHON_FILE; exec bash"
    echo "Started screen session 'session_$i' running '$PYTHON_FILE'"
done

echo "All $NUM_SESSIONS screen sessions started."