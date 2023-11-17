# youwhisper
`youwhisper` is a versatile, Python-based video/audio transcription mini-tool that uses `yt-dlp` and `whisperx` (or `openai-whisper`, depending on the configuration) to create a single-command transcription pipeline to transcribe audio from online video sources using `yt-dlp` and then passing the downloaded audio on to either `whisper` or `whisperx` for audio transcribing. Transcribed text comes out the other end, by default to `.txt` and `.srt` files.

(Full list of `yt-dlp` supported online platforms [here](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md#:~:text=URL%3A%20https%3A%2F%2Fgithub.com%2Fyt))

Simply put, `youwhisper` a handy all-in-one CLI tool for creating accurate subtitles and text transcripts from online video and audio sources with a single, simple command. I.e.:

```bash
youwhisper <Video-URL>
```

or:

```bash
youwhisper -l fi <Video-URL> 
```

For transcriptions where the spoken language is Finnish (`fi`). Program defaults to English (`en`). You can use the `-l` or `--lang` switch for all the available languages that `openai-whisper` or `whisperx` supports and/or modify the `youwhisper.ini` to suit your needs for the program's default transcription language.

`youwhisper` runs in both Linux environments as well as in Windows using Git Bash.

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

If you're willing to take the risk of blind-installing either `whisperx` or `openai-whisper` locally, you can do so with either of the following commands:

**WhisperX:**
```bash
pip install git+https://github.com/m-bain/whisperx.git --upgrade
```
(**although I highly recommend you look at the `conda` install instructions from the [WhisperX project page](https://github.com/m-bain/whisperX#setup-%EF%B8%8F)**)

**OpenAI Whisper (via `pip`):**
```bash
pip install -U openai-whisper
```

**OR**

**OpenAI Whisper (latest cutting-edge git):**
```bash
pip install git+https://github.com/openai/whisper.git 
```

### **(Optional) Adding `youwhisper` to your `~/.bash_aliases`**

If you have installed WhisperX (or Whisper) into a `conda` environment following the [instructions on WhisperX's project page](https://github.com/m-bain/whisperX) (which is usually the recommended method in many use scenarios, so that you don't collide with dependencies and end up with a broken Python environment), you might need to add a function to your `~/.bash_aliases` file that activates the `whisperx` environment before the script is run, here's an example on how to do it:

```bash
# `youwhisper` /// download and auto-whisper process
function youwhisper() {
    conda activate whisperx
    python $HOME/youwhisper/youwhisper.py "$@"
    conda deactivate
}
```
(Note that in the function above, it's assumed that your `youwhisper` is located at `$HOME/youwhisper/` (a.k.a. underneath the user's home directory, in a sub-directory named `youwhisper`.)

## Usage

Run `youwhisper` with the URL of the video from the supported streaming platform:
```bash
./youwhisper.py <Video-URL>
```
This uses the default language set in the `youwhisper.ini` config file, which is English (`en`) by default.

You can specify the transcription language with i.e.:

```bash
./youwhisper.py <Video-URL> [-l <Language-Code>]
```

Or, if you added `youwhisper` to your `~/.bash_aliases`, you can just use:

```bash
youwhisper <Video-URL> [-l <Language-Code>]
```

## Configuration (`youwhisper.ini`):

Adjust settings like transcription model, language, and output formats in the youwhisper.ini file to tailor the tool to your needs. Here's an example configuration of the `youwhisper.ini`:

```
[whisper]
executable = whisper
model = large-v3
language = en
output_formats = all
```
Configuring youwhisper.ini: A Step-by-Step Guide

1. `executable`:

    - This specifies the transcription tool to be used.
    - In this example, `whisperx` is set as the executable, meaning `youwhisper` will use WhisperX for transcription.
    - If you have `openai-whisper` installed instead you can replace `whisperx` with `whisper` or the path to the `openai-whisper` executable.

2. `model`:

    - This determines the specific model of WhisperX or openai-whisper to be used for transcription.
    - `large-v2` is (at the writing of this) the most current model that WhisperX supports
    - `large-v3` is the default recommendation when using Whisper (Nov 2023)
    - You can select different models depending on your accuracy requirements and resource availability (e.g., `base`, `small`, `medium`, `large`, or preferably `large-v2` with WhisperX. At the time of writing this, `openai-whisper` has `large-v3` available).

3. `language`:

    - This sets the language for transcription.
    - The example uses `en` for English.
    - You can change this to any supported language code as per your requirement (e.g., `fi` for Finnish, `es` for Spanish, `de` for German, etc).

4. `output_formats`:

    - This defines the formats in which the transcribed output will be saved.
    - The default is to output to all available formats
    - You can specify different or additional formats supported by WhisperX or openai-whisper, separating them with commas (e.g., `srt`, `txt`, `json`).

By customizing these settings, you can make youwhisper fit perfectly into your workflow, whether you're a content creator, researcher, or anyone in need of quick and accurate transcriptions out of online videos.

## Dependencies

- `yt-dlp` -- For audio extraction from various video streaming platforms.
- `whisperx` (or alternatively, `openai-whisper`) -- For converting audio into textual and subtitle formats.

## Contributing

- Contributions to enhance youwhisper are always welcome! Feel free to report issues, suggest features, or submit pull requests.
- Feel free to star the repo, share feedback, or participate in discussions if this project seems to be of any interest!

## Changelog
- `v1.05` - bug fixes, additional checks
- `v1.04` - added safety checks to see that `yt-dlp` and/or `whisper` or `whisperx` is installed before running, also added helpers to guide through the install process, should something be missing.
- `v1.00` (Nov 17, 2023)

## Todo
- (Maybe) add the option to use the Whisper API via OpenAI's API instead of a local model, for those with less local compute and access to OpenAI's API
- (Maybe) OpenAI API-based local summaries on the transcripts, possible online translation pipelines (i.e. via OpenAI API)

## License

`youwhisper` is made available under the MIT License. See the [LICENSE](LICENSE) file for more details.
All the other required dependencies have their own corresponding licenses. See their licenses from their corresponding repositories.

## About

Written by FlyingFathead, alongside my co-pilot, ChaosWhisperer.
- GitHub: https://github.com/FlyingFathead/
- `youwhisper` repo @ https://github.com/FlyingFathead/youwhisper/

## External links

- `whisperX` - https://github.com/m-bain/whisperX
- `openai-whisper` - https://github.com/openai/whisper
- `yt-dlp` - https://github.com/yt-dlp/yt-dlp

