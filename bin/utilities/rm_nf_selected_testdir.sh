#!/bin/bash
# written by : Gemini 2.5 Pro, date  2025-05-01


# --- Configuration ---
# Directory depth where the pattern should be searched for.
# 3 corresponds to the typical Nextflow work dir structure: ./<hash_prefix>/<hash_suffix>/<file>
SEARCH_DEPTH=3

# --- Script Logic ---

# Function to print usage instructions
usage() {
  echo "Usage: $0 \"<file_pattern>\""
  echo "  Example: $0 \"*.sqlite\""
  echo "  Example: $0 \"*.command.err\""
  echo ""
  echo "  This script searches for files matching <file_pattern> within subdirectories"
  echo "  (specifically at depth $SEARCH_DEPTH, e.g., ./ab/cdef1234/your_file)"
  echo "  inside the current directory (expected to be the Nextflow 'work' directory)."
  echo "  It identifies the unique top-level directories (e.g., ./ab) containing these files"
  echo "  and prompts before removing them entirely."
  echo "  WARNING: Removing top-level directories deletes ALL tasks within them."
}

# Check if a file pattern argument is provided
if [ -z "$1" ]; then
  echo "Error: No file pattern provided."
  usage
  exit 1
fi

FILE_PATTERN="$1"
echo "Searching for pattern: \"$FILE_PATTERN\" at depth $SEARCH_DEPTH in the current directory..."

# Use find to locate files matching the pattern at the specified depth
# Extract the first-level directory (e.g., ./fc) for each found file
# Get the unique list of these directories
# Use -print0 and read -d '' for safe handling of filenames with special characters
mapfile -t unique_top_dirs < <(find . -mindepth $SEARCH_DEPTH -maxdepth $SEARCH_DEPTH -name "$FILE_PATTERN" -type f -print0 | \
                                xargs -0 -I {} dirname {} | \
                                cut -d '/' -f 1,2 | \
                                sort -u)

# Check if any directories were found
if [ ${#unique_top_dirs[@]} -eq 0 ]; then
  echo "No top-level directories found containing files matching \"$FILE_PATTERN\" at depth $SEARCH_DEPTH."
  exit 0
fi

# Display the found directories and the warning
echo ""
echo "---------------------------------------------------------------------"
echo "WARNING: The following top-level directories contain files matching"
echo "         \"$FILE_PATTERN\" in their subdirectories."
echo "         Confirming removal will DELETE THESE ENTIRE DIRECTORIES"
echo "         and all Nextflow task data within them."
echo "---------------------------------------------------------------------"
printf "  %s\n" "${unique_top_dirs[@]}" # Print each directory on a new line
echo "---------------------------------------------------------------------"
echo "Total directories to be removed: ${#unique_top_dirs[@]}"
echo ""

# Ask for confirmation
read -p "Proceed with removing ALL listed directories and their contents? (Type 'yes' to confirm): " confirm

# Check confirmation
if [[ "${confirm,,}" == "yes" ]]; then # Convert input to lowercase for case-insensitive comparison
  echo "--- Starting removal process ---"
  removed_count=0
  error_count=0
  for dir_path in "${unique_top_dirs[@]}"; do
    if [ -d "$dir_path" ]; then
      echo "Removing: $dir_path"
      rm -r "$dir_path"
      if [ $? -eq 0 ]; then
        echo "Successfully removed $dir_path"
        ((removed_count++))
      else
        echo "ERROR removing $dir_path"
        ((error_count++))
      fi
    else
      echo "Skipping: '$dir_path' not found or not a directory (might have been removed already)."
    fi
  done
  echo "--- Removal process complete ---"
  echo "Successfully removed: $removed_count directories."
  if [ $error_count -gt 0 ]; then
      echo "Errors encountered: $error_count"
  fi
else
  echo "Aborted. No directories were removed."
  exit 0
fi

exit 0
