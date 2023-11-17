# youwhisper
`youwhisper` is a versatile transcription script/mini-tool that combines the functionality of `yt-dlp` and `whisperx`. It allows for efficient downloading and transcribing of audio from various video streaming platforms, making it an invaluable resource for creating accurate subtitles and text transcripts with a single, simple command.

## Features

- **Versatile Streaming Platform Support:** Utilizes `yt-dlp` for downloading a local audio copy from a wide range of video streaming platforms, not just YouTube.
- **Advanced Transcription Capabilities:** Leverages `whisperx` for high-quality audio transcription into text and subtitles.
- **Customizable Output:** Supports all the transcription output formats that `whisperx` or `openai-whisper` supports, including `.srt` (subtitles) and `.txt` (plain text).
- **User-Friendly Configuration:** Easy configuration adjustments via the `youwhisper.ini` file, accommodating different user preferences and requirements.

## Installation

1. To get started with `youwhisper`, clone the repository and set up the environment.
```bash
git clone https://github.com/FlyingFathead/youwhisper.git
cd youwhisper
```

To run `youwhisper`, you need `yt-dlp` and either Whisper or WhisperX installed.

2. Install `yt-dlp` (via `pip`)
```bash
pip install yt-dlp
```

3. Install i.e. either `whisperx` or `openai-whisper`.

This is where things might get a bit complicated; it's highly suggested to take a look at the installation instructions on the [WhisperX project page](https://github.com/m-bain/whisperX#setup-%EF%B8%8F) and follow them step by step.

## Adding `youwhisper` to your `~/.bash_aliases`

If you have installed WhisperX into a `conda` environment following the [instructions on WhisperX's project page](https://github.com/m-bain/whisperX) (which is usually the recommended method), you might need to add a function to your `~/.bash_aliases` file that activates the `whisperx` environment before the script is run, here's an example on how to do it:

```bash
# `youwhisper` /// download and auto-whisper process
function youwhisper() {
    conda activate whisperx
    python $HOME/youwhisper/youwhisper.py "$1"
    conda deactivate
}
```
(Note that in the function above, it's assumed that your `youwhisper` is located at `$HOME/youwhisper/` (a.k.a. underneath the user's home directory, in a sub-directory named `youwhisper`.)

## Usage

Run `youwhisper` with the URL of the video from the supported streaming platform:
```bash
./youwhisper.py <Video-URL>
```

Or, if you added `youwhisper` to your `~/.bash_aliases`, you can just use:

```bash
youwhisper <Video-URL>
```

## Configuration

Adjust settings like transcription model, language, and output formats in the youwhisper.ini file to tailor the tool to your needs.

## Dependencies

- `yt-dlp`: For audio extraction from various video streaming platforms.
- `whisperx` (or alternatively, `openai-whisper`): For converting audio into textual and subtitle formats.

## Contributing

Contributions to enhance youwhisper are always welcome! Feel free to report issues, suggest features, or submit pull requests.

## License

`youwhisper` is made available under the MIT License. See the [LICENSE](LICENSE) file for more details.
All the other required dependencies have their own corresponding licenses. See their licenses from their corresponding repositories.

## External links

- `whisperX` - https://github.com/m-bain/whisperX
- `openai-whisper` - https://github.com/openai/whisper
- `yt-dlp` - https://github.com/yt-dlp/yt-dlp