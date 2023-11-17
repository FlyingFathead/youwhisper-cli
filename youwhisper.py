#!/usr/bin/env python3
# youwhisper // v.1.01 // Nov 17 2023
# by FlyingFathead (https://github.com/FlyingFathead)
# addtional ghostwriting by ChaosWhisperer

import subprocess
import shutil
import sys
import os
import re
import configparser

# print term width horizontal line
def print_horizontal_line(character='-'):
    terminal_width = shutil.get_terminal_size().columns
    line = character * terminal_width
    print(line, flush=True)

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

def download_audio(youtube_url):
    command = ['yt-dlp', '--extract-audio', '--audio-format', 'mp3', youtube_url]
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
    # Split the output formats into a list
    formats = config['output_formats'].split(', ')
    
    # Start building the command
    command = [config['executable'], '--model', config['model'], '--language', config['language']]
    
    # Add each format as a separate --output_format argument
    for fmt in formats:
        command.extend(['--output_format', fmt.strip()])

    # Add the audio file at the end of the command
    command.append(audio_file)

    output, exit_code = run_command(command)

    # Prepare the expected output files list
    output_files = []
    if exit_code == 0:
        base_filename = os.path.splitext(audio_file)[0]
        for fmt in formats:
            fmt_extension = fmt.strip()
            output_files.append(f"{base_filename}.{fmt_extension}")

    return exit_code == 0, output_files

def main():
    # check for cli arguments
    if len(sys.argv) < 2:
        print("Usage: youwhisper <Video-URL>")
        sys.exit(1)
    
    # load configs and args
    config = load_config()
    youtube_url = sys.argv[1]

    print_horizontal_line()
    print(f"Downloading audio from URL: {youtube_url} ...")
    print_horizontal_line()
    audio_file = download_audio(youtube_url)

    if audio_file:
        print_horizontal_line()
        print(f"Transcribing audio file: {audio_file} ...")
        print_horizontal_line()
        success, output_files = transcribe_audio(audio_file, config)
        if success:
            print_horizontal_line()
            print("Transcription completed successfully. Created files:")
            for file in output_files:
                print(f" - {file}")
            print_horizontal_line()
        else:
            print_horizontal_line()
            print("Transcription failed.")
            print_horizontal_line()
            sys.exit(1)
    else:
        print_horizontal_line()
        print("Download failed or file not found.")
        print_horizontal_line()
        sys.exit(1)

if __name__ == "__main__":
    main()
