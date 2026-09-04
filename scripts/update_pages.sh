#!/bin/bash

# Check for required commands
if ! command -v pdftk &> /dev/null; then
    echo "Error: 'pdftk' is required but it's not installed."
    exit 1
fi

# Usage: ./update_pages.sh <start_page> <directory_path_1> <directory_path_2> ... <directory_path_n>

# Set a page key in a myst.yml, in priority order:
#   1. replace the value of an existing entry, keeping its indentation;
#   2. uncomment a commented-out placeholder (e.g. the dividers' "# first_page:");
#   3. insert a new entry directly under the top-level "project:" key.
# Every myst.yml here has "project:" at the start of a line and indents its
# children by two spaces, which is what case 3 assumes.
set_page_key() {
    local yaml_file=$1
    local key=$2
    local value=$3

    if grep -qE "^[[:space:]]*${key}:" "$yaml_file"; then
        sed -i.bak -E "s/^([[:space:]]*)${key}:.*/\1${key}: ${value}/" "$yaml_file"
    elif grep -qE "^[[:space:]]*#[[:space:]]*${key}:" "$yaml_file"; then
        sed -i.bak -E "s/^([[:space:]]*)#[[:space:]]*${key}:.*/\1${key}: ${value}/" "$yaml_file"
    elif grep -qE "^project:" "$yaml_file"; then
        awk -v key="$key" -v value="$value" '
            { print }
            !inserted && /^project:[[:space:]]*$/ { print "  " key ": " value; inserted = 1 }
        ' "$yaml_file" > "${yaml_file}.tmp" && mv "${yaml_file}.tmp" "$yaml_file"
    else
        echo "Error: no top-level 'project:' key in '$yaml_file'. Cannot set $key."
        return 1
    fi
}

current_page=$1  # First argument is the start page
shift            # Shift to remove the first argument, so now $@ contains the list of directories

# Iterate over all provided base directories
for BASE_DIR in "$@"; do
    # Check if the base directory exists
    if [ ! -d "$BASE_DIR" ]; then
        echo "Base directory '$BASE_DIR' not found. Skipping."
        continue
    fi

    echo "Processing base directory: $BASE_DIR"

    # Iterate over all subdirectories in the base directory
    for folder in "$BASE_DIR"/; do
        yaml_file="${folder}myst.yml"

        # Check if the YAML file exists in the current folder
        if [ ! -f "$yaml_file" ]; then
            echo "YAML file '$yaml_file' not found in folder '$folder'. Skipping."
            continue
        fi

        # Find PDF files in the current folder
        pdf_files=("$folder"*.pdf)

        # Check if there are no PDFs or multiple PDFs
        if [ ${#pdf_files[@]} -eq 0 ]; then
            echo "No PDF files found in folder '$folder'. Skipping."
            continue
        elif [ ${#pdf_files[@]} -gt 1 ]; then
            echo "Error: Multiple PDF files found in folder '$folder'. Only one PDF is allowed. Skipping."
            continue
        fi

        # Get the single PDF file
        pdf_file="${pdf_files[0]}"

        # Get the number of pages in the PDF using pdftk
        num_pages=$(pdftk "$pdf_file" dump_data | grep NumberOfPages | awk '{print $2}')
        
        if [ -z "$num_pages" ]; then
            echo "Error counting pages in $pdf_file."
            continue
        fi

        # Calculate first and last page
        first_page=$current_page
        last_page=$((current_page + num_pages - 1))
        current_page=$((current_page + num_pages))

        # Update first_page and last_page, adding them if they are missing
        echo "Processing $pdf_file in $yaml_file: first_page=$first_page, last_page=$last_page"

        # last_page first: each inserted key goes directly under "project:", so
        # setting it first leaves the pair in first_page/last_page order.
        set_page_key "$yaml_file" last_page "$last_page"
        set_page_key "$yaml_file" first_page "$first_page"

        echo "YAML file '$yaml_file' in folder '$folder' updated successfully!"
    done
done

