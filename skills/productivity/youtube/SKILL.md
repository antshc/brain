---
name: youtube
description: Fetch YouTube video transcripts, metadata, and downloads using yt-dlp. Use when the user shares a YouTube URL, or asks to download, transcribe, or get the title, metadata, subtitles, video, or audio for a YouTube video or playlist.
---

# YouTube

Fetch transcripts, metadata, video, and audio from YouTube through `yt-dlp`, the one tool this skill wraps for every operation below.


## Install

Run only when the user explicitly runs `/youtube install`.

Confirm `yt-dlp` is not on PATH before installation:

```
yt-dlp --version
```

Install `yt-dlp`:

- Linux: `python3 -m pip install --user -U yt-dlp`
- Windows (PowerShell): `py -m pip install -U yt-dlp`

`ffmpeg` merges separate video/audio streams and extracts audio; only needed for the format-merging and audio-extraction operations below. Package-manager installs need elevated privileges you should not assume, so hand the command to the user instead of running it yourself:

- Linux: `sudo apt-get install -y ffmpeg` (Debian/Ubuntu) or the distro's equivalent.
- Windows: `winget install ffmpeg` or `choco install ffmpeg`.

Done when `yt-dlp --version` and, if needed, `ffmpeg -version` both succeed.

## Common operations

### Download video
```
# 720p + subtitles if available (default)
yt-dlp -f "bestvideo[height<=720]+bestaudio/best[height<=720]" --write-sub --write-auto-sub --sub-lang en -o "%(title)s.%(ext)s" "URL"

# Best quality
yt-dlp -f best -o "%(title)s.%(ext)s" "URL"

# Specific format (mp4)
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]" -o "%(title)s.%(ext)s" "URL"

# Audio only (mp3)
yt-dlp -x --audio-format mp3 -o "%(title)s.%(ext)s" "URL"
```

### Get full metadata (JSON)
```
yt-dlp --dump-json "URL"
```
Pipe through `python3 -c "import sys,json; d=json.load(sys.stdin); print({k:d[k] for k in ('title','description','duration','uploader','upload_date')})"` to narrow the fields.

### Download transcript/subtitles
```
# Auto-generated English subtitles
yt-dlp --write-auto-sub --skip-download --sub-lang en -o "output_name" "URL"

# Manual subtitles, when available
yt-dlp --write-sub --skip-download --sub-lang en -o "output_name" "URL"
```

### List available subtitles
```
yt-dlp --list-subs "URL"
```


### Download playlist
```
yt-dlp -o "%(playlist_title)s/%(title)s.%(ext)s" "PLAYLIST_URL"
```

## Output patterns

- `%(title)s` — video title
- `%(ext)s` — file extension
- `%(id)s` — video ID
- `%(uploader)s` — channel name
- `%(upload_date)s` — upload date (YYYYMMDD)
- `%(playlist_title)s` — playlist name
- `%(playlist_index)s` — position in playlist

## Gotchas

- **Always quote the URL.** YouTube URLs carry `&`, `?`, and `=`; unquoted, bash backgrounds the command at the first `&` and PowerShell can still mis-tokenize it. Quote on every OS, not just the ones where it visibly breaks.
- **`yt-dlp` writes real paths on both OSes.** `-o` templates use forward slashes even on Windows; `yt-dlp` translates them, so don't rewrite them to backslashes.
- **Subtitle files are VTT, not plain text.** They carry timestamp lines and cue markup — extract with the script in Troubleshooting rather than reading them raw.

## Troubleshooting

### 403 errors / SABR streaming

YouTube frequently changes its streaming format. On a 403:

1. Update first: `yt-dlp -U`
2. Try the TV client: `yt-dlp --extractor-args "youtube:player_client=tv" "URL"`
3. List formats to diagnose: `yt-dlp -F "URL"`

### Processing VTT transcripts to plain text

VTT files carry timestamp and cue-position lines. Strip them with a cross-platform script rather than a shell-specific pipeline:

```python
import re
import sys

path = sys.argv[1]
seen = set()
out = []
with open(path, encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\n")
        if re.match(r"^\d", line) or line.startswith(("WEBVTT", "Kind:", "Language:")) or not line.strip():
            continue
        text = re.sub(r"<[^>]*>", "", line)
        if text not in seen:
            seen.add(text)
            out.append(text)
print("\n".join(out))
```

Run it with `python3 script.py file.en.vtt > transcript.txt` on Linux or `py script.py file.en.vtt > transcript.txt` on Windows.
