#!/usr/bin/env python3
"""
Wrapper script to bypass molecule 25.x schema validation issue.
This script simply calls molecule and lets the shell script handle schema validation errors.
The actual workaround is in the GitHub Actions workflow which falls back to individual commands.
"""
import sys
import subprocess

if __name__ == '__main__':
    # Get command line arguments (skip script name)
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    # Simply call molecule - the shell script will handle schema validation errors
    # by falling back to individual commands if this fails
    try:
        result = subprocess.run(['molecule'] + args, check=False)
        sys.exit(result.returncode)
    except FileNotFoundError:
        print("Error: molecule command not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error running molecule: {e}", file=sys.stderr)
        sys.exit(1)
