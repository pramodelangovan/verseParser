import argparse
import os
import shutil
import json


def parse_arguments():
    parser = argparse.ArgumentParser(description="Process input and output paths.")
    parser.add_argument("-i", "--input", type=str, required=True, help="Path to the input file")
    parser.add_argument("-o", "--output", type=str, required=True, help="Path to the output file")
    parser.add_argument("-m", "--metadata", type=bool, default=True, help="option to include metadata")
    parser.add_argument("-n", "--versename", type=bool, default=True, help="option to include verse names")
    return parser.parse_args()

def str_to_list(value):
    return value if isinstance(value, str) else ", ".join(value)

def process_content(content):
    data = json.load(content)
    out = ''
    if include_metadata:
        out += "\n".join([f"{prop}: {str_to_list(value).strip()}" for prop, value in data["properties"].items()])
        out += '\n\n'
    for lines in data['lyrics']['verse']:
        if include_versename:
            out += f"Verse: {lines['name']}\n"
        for line in lines['lines']:
            out += f"{line}\n"
        out += "\n"

    return out

def process_files(input_folder, output_folder):
    for root, dirs, files in os.walk(input_folder):
        # Replicate the directory structure in the output folder
        relative_path = os.path.relpath(root, input_folder)
        target_dir = os.path.join(output_folder, relative_path)
        os.makedirs(target_dir, exist_ok=True)

        for file in files:
            input_file_path = os.path.join(root, file)
            # Replace the file extension with .txt
            output_file_name = os.path.splitext(file)[0] + ".txt"
            output_file_path = os.path.join(target_dir, output_file_name)

            with open(input_file_path, 'r') as infile:
                content = infile.read()
                processed_content = process_content(content)
                with open(output_file_path, 'w') as outfile:
                    outfile.write(processed_content)



if __name__ == "__main__":
    args = parse_arguments()
    input_path = args.input
    output_path = args.output
    global include_metadata
    global include_versename

    metadata_flag = args.metadata
    versename_flag = args.versename

    if not os.path.isdir(input_path):
        print(f"Error: {input_path} is not a valid directory.")
    else:
        process_files(input_path, output_path)
        print(f"Processed files from {input_path} to {output_path}")

# ...existing code...
