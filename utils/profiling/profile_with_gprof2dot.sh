#!/bin/bash

# Check if required commands are available
if ! command -v python3 &> /dev/null; then
    echo "python3 could not be found. Please install Python 3."
    exit 1
fi

if ! python3 -c "import cProfile" &> /dev/null; then
    echo "cProfile module is not available in Python 3."
    exit 1
fi

if ! command -v gprof2dot &> /dev/null; then
    echo "gprof2dot could not be found. Please install gprof2dot. pip install gprof2dot"
    exit 1
fi

if ! command -v dot &> /dev/null; then
    echo "dot (Graphviz) could not be found. Please install Graphviz. sudo apt-get install graphviz"
    exit 1
fi

# Check if correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <python_file> <output_svg>"
    exit 1
fi

PYTHON_FILE=$1
OUTPUT_SVG=$2
PROFILE_OUTPUT="profile_output.pstats"

# Profile the Python script
python3 -m cProfile -o $PROFILE_OUTPUT $PYTHON_FILE

# Generate the SVG using gprof2dot and dot
gprof2dot -f pstats $PROFILE_OUTPUT | dot -Tsvg -o $OUTPUT_SVG

# Clean up the profile output file
rm $PROFILE_OUTPUT

echo "Profile SVG generated at $OUTPUT_SVG"