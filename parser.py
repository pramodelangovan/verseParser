"""
Verse Parser - Business Logic

This module contains all the file processing and parsing logic.
"""

import argparse
import json
import os

import chardet


def is_metadata_file(filename):
    """Filter out macOS and Windows metadata files"""
    metadata_patterns = {
        '.DS_Store',
        '.TemporaryItems',
        '.Spotlight-V100',
        '.Trashes',
        '.AppleDouble',
        '.AppleDB',
        'Thumbs.db'
    }
    # Check if filename matches metadata patterns
    if filename in metadata_patterns:
        return True
    # Check for ._* resource fork files
    if filename.startswith('._'):
        return True
    return False


def is_json_file(filename):
    """Check if file is a JSON file"""
    return filename.lower().endswith('.json')


def detect_encoding(file_path):
    """Detect the encoding of a file"""
    try:
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
            return result['encoding']
    except Exception as e:
        print(f"Error detecting encoding: {e}")
    return "utf-8"


def str_to_list(value):
    """Convert list to comma-separated string if needed"""
    return value if isinstance(value, str) else ", ".join(value)


def process_content(content, include_metadata=True, include_versename=True):
    """Process JSON content and return formatted text

    Args:
        content: File object containing JSON content
        include_metadata: Whether to include metadata properties
        include_versename: Whether to include verse names

    Returns:
        Formatted string with processed lyrics
    """
    data = json.load(content)
    out = ''

    if include_metadata:
        out += "\n".join([f"{prop}: {str_to_list(value).strip()}"
                         for prop, value in data["properties"].items()])
        out += '\n\n'

    for lines in data['lyrics']['verse']:
        if include_versename:
            out += f"Verse: {lines['name']}\n"
        for line in lines['lines']:
            out += f"{line}\n"
        out += "\n"

    return out


def process_files(input_folder, output_folder, include_metadata=True, include_versename=True):
    """Process all JSON files from input folder to output folder

    Args:
        input_folder: Path to input directory with JSON files
        output_folder: Path to output directory for text files
        include_metadata: Whether to include metadata properties
        include_versename: Whether to include verse names

    Returns:
        Number of files processed
    """
    file_count = 0

    for root, dirs, files in os.walk(input_folder):
        # Replicate the directory structure in the output folder
        relative_path = os.path.relpath(root, input_folder)
        target_dir = os.path.join(output_folder, relative_path)
        os.makedirs(target_dir, exist_ok=True)

        for file in files:
            # Skip metadata files and non-JSON files
            if is_metadata_file(file) or not is_json_file(file):
                continue

            input_file_path = os.path.join(root, file)
            # Replace the file extension with .txt
            output_file_name = os.path.splitext(file)[0] + ".txt"
            output_file_path = os.path.join(target_dir, output_file_name)

            # Detect encoding of the input file
            encoding = detect_encoding(input_file_path)

            with open(input_file_path, 'r', encoding=encoding) as infile:
                processed_content = process_content(infile, include_metadata, include_versename)
                with open(output_file_path, 'w', encoding=encoding) as outfile:
                    outfile.write(processed_content)

            file_count += 1

    return file_count


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Process JSON verse files to text format.")
    parser.add_argument("-i", "--input", type=str, required=True, help="Path to the input directory")
    parser.add_argument("-o", "--output", type=str, required=True, help="Path to the output directory")
    parser.add_argument("-m", "--metadata", type=bool, default=True, help="Include metadata")
    parser.add_argument("-n", "--versename", type=bool, default=True, help="Include verse names")
    return parser.parse_args()


def main():
    """Command line interface for the parser"""
    args = parse_arguments()
    input_path = args.input
    output_path = args.output
    metadata_flag = args.metadata
    versename_flag = args.versename

    # Create the output folder if it does not exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    if not os.path.isdir(input_path):
        print(f"Error: {input_path} is not a valid directory.")
        return

    file_count = process_files(input_path, output_path, metadata_flag, versename_flag)
    print(f"Processed {file_count} file(s) from {input_path} to {output_path}")


if __name__ == "__main__":
    main()
