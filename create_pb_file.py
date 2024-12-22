#!/usr/bin/env python3

# Created by ChatGPT from
# The prompt requested a Python script to:
# Input and Output:
# * Read keywords and their replacement values from a file (VARFILE).
# * Substitute those keywords in an input file (permission-boundary-sample.json) with their corresponding values.
# * Write the modified content to an output file (OUTFILE).
#
# Additional Features:
# * Remove all text starting with // on any line.
# * Remove blank lines left behind after processing but preserve other whitespace.
# * Perform substitutions only for whole-word matches of the keywords.
#
# Execution:
# * Accept VARFILE and OUTFILE as command-line arguments.
# * Ensure robust error handling for missing files.
# * The final script meets these requirements while ensuring compatibility and clarity. Let me know if further details are needed!


import sys
import re

# Ensure correct number of arguments
if len(sys.argv) != 3:
    print("Usage: python3 script.py INFILE VARFILE OUTFILE")
    sys.exit(1)

INFILE = "permission-boundary-sample.json"
VARFILE = sys.argv[1]
OUTFILE = sys.argv[2]

# Load substitutions from VARFILE
substitutions = {}
try:
    with open(VARFILE, 'r') as varfile:
        for line in varfile:
            line = line.strip()
            if "=" in line:
                key, value = map(str.strip, line.split("=", 1))
                substitutions[key] = value
except FileNotFoundError:
    print(f"Error: VARFILE '{VARFILE}' not found.")
    sys.exit(1)

# Perform substitutions
try:
    with open(INFILE, 'r') as infile, open(OUTFILE, 'w') as outfile:
        blank_line = False
        for line in infile:
            # Remove comments starting with //
            line = re.sub(r"//.*", "", line)
            if not line.strip():
                if not blank_line:
                    outfile.write("\n")  # Write a single blank line
                    blank_line = True
                continue
            blank_line = False
            for key, value in substitutions.items():
                # Replace whole words matching the key
                line = re.sub(rf"\b{re.escape(key)}\b", value, line)
            outfile.write(line)
except FileNotFoundError:
    print(f"Error: INFILE '{INFILE}' not found.")
    sys.exit(1)

print(f"Substitution complete. Output written to '{OUTFILE}'.")
