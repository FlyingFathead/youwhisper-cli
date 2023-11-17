#!/usr/bin/env python3
# youwhisper // v.1.05 // Nov 17 2023
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

def download_audio(video_url):
    command = ['yt-dlp', '--extract-audio', '--audio-format', 'mp3', video_url]
    output, exit_code = run_command(command)
    if exit_code != 0:
        return None

    # Regex to find the filename in yt-dlp's output
    match = re.search(r'\[ExtractAudio\] Destination: (.+\.mp3)', output)
    if match:
        audio_file = match.group(1).strip()
        if os.path.isfile(audio_file):
            return audio_file

    return None

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
    parser.add_argument('-l', '--language', '--lang', help='language for transcription', default=None)

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
    video_url = args.video_url

    # If language argument is provided, override the language in config
    if args.language:
        config['language'] = args.language

    print_horizontal_line()
    print(f"::: Downloading audio from URL: {video_url} ...")
    print_horizontal_line()
    audio_file = download_audio(video_url)

    if audio_file:
        print_horizontal_line()
        print(f"::: Transcribing audio file: {audio_file} ...")
        print_horizontal_line()
        success, output_files = transcribe_audio(audio_file, config)
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
