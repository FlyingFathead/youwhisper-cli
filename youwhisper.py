#!/usr/bin/env python3
# youwhisper // v.1.101 // Nov 23 2023
# by FlyingFathead (https://github.com/FlyingFathead)
# addtional ghostwriting by ChaosWhisperer

import subprocess
import shutil
import sys
import os
import re
import configparser
import argparse
import glob
import time
import json
import urllib.parse

# print term width horizontal line
def print_horizontal_line(character='-'):
    terminal_width = shutil.get_terminal_size().columns
    line = character * terminal_width
    print(line, flush=True)

# check if `yt-dlp` is installed
def check_yt_dlp_installed():
    try:
        subprocess.run(['yt-dlp', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    
# check if `whisper` or `whisperx` is installed
def check_whisper_installed():
    for command in ['whisper', 'whisperx']:
        try:
            subprocess.run([command, '-h'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    return False

def download_info_json(video_url):
    command = ['yt-dlp', '--skip-download', '--write-info-json', video_url]
    output, exit_code = run_command(command)

    if exit_code != 0:
        print(f"yt-dlp command failed with exit code {exit_code}")
        print("Command output:")
        print(output)  # Print the output for debugging
        return None

    # Check if the info JSON file exists in the current directory
    possible_info_files = glob.glob('*.info.json')
    if possible_info_files:
        return possible_info_files[0]

    return None

# create info file
def create_info_text_file(json_file):
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            video_info = json.load(file)

        # Define the info filename
        info_filename = f"{os.path.splitext(json_file)[0]}.info.txt"

        # Extract the basic information
        video_url = video_info.get('webpage_url', 'N/A')
        title = video_info.get('title', 'N/A')
        upload_date = video_info.get('upload_date', 'N/A')
        description = video_info.get('description', 'N/A')

        # Create the initial info text
        info_text = f"Video URL: {video_url}\n"
        info_text += f"Title: {title}\n"
        info_text += f"Upload Date: {upload_date}\n"
        info_text += f"Description: {description}\n"

        # Extract additional information
        uploader = video_info.get('uploader', 'N/A')
        view_count = video_info.get('view_count', 'N/A')
        like_count = video_info.get('like_count', 'N/A')
        duration = video_info.get('duration', 'N/A')
        tags = video_info.get('tags', [])

        # Format tags as a comma-separated string
        tags_string = ', '.join(tags) if tags else 'None'

        # Add the additional information to the info text
        info_text += f"Uploader: {uploader}\n"
        info_text += f"View Count: {view_count}\n"
        info_text += f"Like Count: {like_count}\n"
        info_text += f"Duration: {duration} seconds\n"
        info_text += f"Tags: {tags_string}\n"

        # Save the info text to the info file
        with open(info_filename, 'w', encoding='utf-8') as file:
            file.write(info_text)

        return info_filename
    except Exception as e:
        print(f"[ERROR] Error creating info text file: {str(e)}")
        return None

def load_config():
    # Get the directory of the current script file
    script_dir = os.path.dirname(os.path.realpath(__file__))
    config_file = os.path.join(script_dir, 'youwhisper.ini')

    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Configuration file {config_file} not found.")

    config = configparser.ConfigParser()
    config.read(config_file)

    if 'whisper' not in config:
        raise ValueError(f"'whisper' section not found in {config_file}.")

    # Print the default language from the config file
    print_horizontal_line()
    print(f"::: Default language set in 'youwhisper.ini' configuration file: {config['whisper']['language']}")

    # Load and print the create_info_file configuration
    create_info_file = config.getboolean('whisper', 'create_info_file', fallback=True)
    create_info_file_str = str(create_info_file)  # Convert boolean to string
    print(f"::: Create info file setting: {'Yes' if create_info_file else 'No'}")

    # Add the create_info_file option to the configuration dictionary as a string
    config['whisper']['create_info_file'] = create_info_file_str

    return config['whisper']

def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True)
    output = ""
    while True:
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break
        if line:
            print(line, end='', flush=True)
            output += line

    return output, process.poll()

def download_audio(video_url, create_info_file):
    command = ['yt-dlp', '--extract-audio', '--audio-format', 'mp3', video_url]
    if create_info_file:
        command.append('--write-info-json')
    output, exit_code = run_command(command)

    # Regex to find the filename in yt-dlp's output
    match = re.search(r'\[ExtractAudio\] Destination: (.+\.mp3)', output)
    if match:
        audio_file = match.group(1).strip()
        if os.path.isfile(audio_file):
            return audio_file
    else:
        # Handle case where file already exists
        already_downloaded_match = re.search(r'has already been downloaded', output)
        if already_downloaded_match:
            # Extract the filename from the output message
            file_name_match = re.search(r'(.+)\.mp3 has already been downloaded', output)
            if file_name_match:
                audio_file = file_name_match.group(1).strip() + '.mp3'
                if os.path.isfile(audio_file):
                    return audio_file

    return None

# extract the video info from the json
def extract_info_from_json(json_file):
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            video_info = json.load(file)

        video_url = video_info.get('webpage_url', 'N/A')
        title = video_info.get('title', 'N/A')
        upload_date = video_info.get('upload_date', 'N/A')
        description = video_info.get('description', 'N/A')

        return video_url, title, upload_date, description
    except Exception as e:
        print(f"Error extracting info from JSON: {str(e)}")
        return None, None, None, None

def transcribe_audio(audio_file, config):
    # Split the output formats into a list and trim whitespace
    formats = [fmt.strip() for fmt in config['output_formats'].split(',')]

    # Check if multiple formats are specified and print a warning
    if len(formats) > 1:
        print("[WARNING] Multiple formats selected in `youwhisper.ini`:", ', '.join(formats), 
              "-- Whisper currently doesn't support selecting multiple individual formats in a single run. Reverting to `all`, which outputs all transcription formats at once.")

        # Set to generate all formats
        formats = ['all']

    # Start building the command
    command = [config['executable'], '--model', config['model'], '--language', config['language']]
    
    # Add each format as a separate --output_format argument
    for fmt in formats:
        command.extend(['--output_format', fmt])

    # Add the audio file at the end of the command
    command.append(audio_file)

    # Print the command for verification
    print("Executing command:", ' '.join(command))

    # Record the time before running the command
    start_time = time.time()

    # Execute the command
    output, exit_code = run_command(command)

    # Record the time after running the command
    end_time = time.time()

    # Prepare the expected output files list
    output_files = []
    audio_file_dir = os.path.dirname(os.path.realpath(audio_file))

    # Check all files in the directory where the audio file is located
    for file in os.listdir(audio_file_dir):
        full_path = os.path.join(audio_file_dir, file)
        if os.path.isfile(full_path):
            file_creation_time = os.path.getmtime(full_path)
            # Check if the file was created/modified after the Whisper command was run
            if start_time <= file_creation_time <= end_time:
                output_files.append(file)

    # Determine success based on the exit code of the Whisper command
    return exit_code == 0, output_files

def main():

    # Set up argparse
    # If no arguments are provided, print the usage and exit

    parser = argparse.ArgumentParser(description='youwhisper: Audio Transcription Tool')
    parser.add_argument('video_url', help='URL of the online video to transcribe')
    parser.add_argument('-l', '--language', '--lang', help='language for transcription', default='en')

    # Parse arguments
    args = parser.parse_args()

    # If no video URL is provided, print the usage and exit
    if not args.video_url:
        parser.print_help()
        sys.exit(1)

    # check for yt-dlp installation
    if not check_yt_dlp_installed():
        print("Error: yt-dlp is not installed. Please install it using 'pip install yt-dlp --upgrade'")
        sys.exit(1)

    # check for whisper or whisperx installation
    if not check_whisper_installed():
        print("Error: Neither whisperx nor openai-whisper is installed. Please install one of them using:")
        print("'pip install git+https://github.com/m-bain/whisperx.git --upgrade' for whisperx")
        print("or 'pip install -U openai-whisper' for openai-whisper")
        sys.exit(1)

    # load configs and args
    config = load_config()

    # Parse arguments
    args = parser.parse_args()

    # If language argument is provided, override the language in config
    if args.language:
        config['language'] = args.language
        # Debug print statement to check if the language is overwritten
        print(f"::: Language overridden by command line argument: {config['language']}")
    else:
        print(f"::: No language argument provided, using default: {config['language']}")

    video_url = args.video_url

    # Print the language that will be used for transcription
    # print_horizontal_line()
    print(f"::: Language for transcription: {config['language']}")
    print(f"::: Downloading audio from URL: {video_url} ...")
    print_horizontal_line()

    # Download audio and potentially the info JSON
    audio_file = download_audio(video_url, config['create_info_file'])

    # Download info JSON file
    info_json_file = download_info_json(video_url)

    output_files = []  # Initialize output_files

    if info_json_file:
        # Extract info from JSON
        video_url, title, upload_date, description = extract_info_from_json(info_json_file)

        if video_url:
            # Create info text file
            info_file = create_info_text_file(info_json_file)
            if info_file:
                output_files.append(info_file)
                
                # Print success message
                print_horizontal_line()
                print("::: Info extraction and text file creation completed successfully.")
                print_horizontal_line()
            else:
                print_horizontal_line()
                print("[ERROR] Info text file creation failed.")
                print_horizontal_line()
                sys.exit(1)
        else:
            print_horizontal_line()
            print("[ERROR] Info extraction failed.")
            print_horizontal_line()
            sys.exit(1)
    else:
        print_horizontal_line()
        print("[ERROR] Info JSON download failed or file not found.")
        print_horizontal_line()
        sys.exit(1)

    if audio_file:
        print_horizontal_line()
        print(f"::: Transcribing audio file: {audio_file} ...")
        print_horizontal_line()
        success, output_files = transcribe_audio(audio_file, config)

        if config['create_info_file']:
            json_file = audio_file.replace('.mp3', '.info.json')
            info_file = create_info_text_file(json_file)
            # info_file = create_info_text_file(json_file, os.path.splitext(audio_file)[0])
            output_files.append(info_file)

        if success:
            print_horizontal_line()
            print("::: Transcription completed successfully. Created files:")
            for file in output_files:
                print(f" - {file}")
            print_horizontal_line()
        else:
            print_horizontal_line()
            print("[ERROR] Transcription failed.")
            print_horizontal_line()
            sys.exit(1)
    else:
        print_horizontal_line()
        print("[ERROR] Download failed or file not found.")
        print_horizontal_line()
        sys.exit(1)

if __name__ == "__main__":
    main()
