#!/usr/bin/env python3
# written by: Gemini 2025-05-01
import sys
import argparse
import re



def clean_and_write_list(input_file_path, output_file_path):
    """
    Reads a file containing a list representation (e.g., "[/path/a, /path/b]"),
    cleans it, and writes a newline-separated list to the output file.
    """
    try:
        with open(input_file_path, 'r') as infile:
            content = infile.read().strip()

        # Remove leading/trailing brackets using regex
        content = re.sub(r'^\s*\[|\]\s*$', '', content)

        # Split by comma, trim whitespace from each item, filter out empty strings
        cleaned_paths = [path.strip() for path in content.split(',') if path.strip()]

        with open(output_file_path, 'w') as outfile:
            for path in cleaned_paths:
                outfile.write(path + '\n')

        print(f"Successfully wrote {len(cleaned_paths)} paths to {output_file_path}")

    except FileNotFoundError:
        print(f"Error: Input file not found: {input_file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file {input_file_path}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean Nextflow list file representation.")
    parser.add_argument("-i", "--input", required=True, help="Input file containing the list representation.")
    parser.add_argument("-o", "--output", required=True, help="Output file for newline-separated paths.")
    args = parser.parse_args()

    clean_and_write_list(args.input, args.output)
