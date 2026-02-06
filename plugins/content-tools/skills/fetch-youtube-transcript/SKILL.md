---
name: fetch-youtube-transcript
description: Download YouTube video transcripts as readable text files. Use when extracting transcripts from videos for analysis, documentation, or content review.
argument-hint: <video-url-or-id> [--output DIR] [--language LANG]
---

# YouTube Transcript Download Skill

## Purpose

Download transcripts from YouTube videos as readable text files with timestamps. This skill wraps the `youtube-transcript-api` tool with a simple interface for quick transcript extraction.

## Usage

```bash
/fetch-youtube-transcript <video-url-or-id> [--output DIR] [--language LANG]
```

## Arguments

### Required

- **`<video-url-or-id>`**: YouTube video URL or video ID
  - Full URLs: `https://www.youtube.com/watch?v=VIDEO_ID`
  - Short URLs: `https://youtu.be/VIDEO_ID`
  - Video ID only: `VIDEO_ID` (11 characters)
  - URLs with timestamps and query parameters are supported

### Optional

- **`--output DIR`**: Output directory for transcript files
  - Default: `.work/transcripts/`
  - Directory will be created if it doesn't exist
  - Transcript saved as `VIDEO_ID.txt`

- **`--language LANG`**: Preferred transcript language code
  - Default: Auto-select (usually English if available)
  - Examples: `en`, `es`, `fr`, `de`, `ja`
  - Falls back to auto-generated if manual transcript unavailable

## Execution Instructions for Claude Code

When the user invokes `/fetch-youtube-transcript`, follow these steps:

### 1. Parse Arguments

Extract the video URL/ID and optional parameters from the user's command:

```python
# Example argument parsing logic
import re
from pathlib import Path

def parse_args(args_string):
    """Parse /fetch-youtube-transcript arguments."""
    parts = args_string.split()

    if not parts:
        return None, None, None, "Error: Video URL or ID required"

    video_url = parts[0]
    output_dir = ".work/transcripts"
    language = None

    # Parse optional flags
    i = 1
    while i < len(parts):
        if parts[i] == "--output" and i + 1 < len(parts):
            output_dir = parts[i + 1]
            i += 2
        elif parts[i] == "--language" and i + 1 < len(parts):
            language = parts[i + 1]
            i += 2
        else:
            i += 1

    return video_url, output_dir, language, None
```

### 2. Construct Command

Build the `uvx` command to run the transcript fetcher:

```bash
uvx --from youtube-transcript-api \
  python scripts/fetch-youtube-transcript.py \
  "<video-url>" \
  --output "<output-dir>"
```

If language is specified, add `--language <lang>`.

**Important**:
- The script is bundled with this plugin at `scripts/fetch-youtube-transcript.py`
- Quote the video URL to handle special characters
- Use the full path to the script in the plugin cache directory

### 3. Execute Command

Run the command using the Bash tool with appropriate error handling:

```python
# Construct full command
cmd_parts = [
    "uvx --from youtube-transcript-api",
    "python scripts/fetch-youtube-transcript.py",
    f'"{video_url}"',
    f"--output {output_dir}"
]

if language:
    cmd_parts.append(f"--language {language}")

command = " ".join(cmd_parts)

# Execute via Bash tool
# The script will handle all video ID extraction and error cases
```

### 4. Handle Output

The script outputs structured information on success:

```
✅ Transcript downloaded successfully!

Video: 4_2j5wgt_ds
File: .work/transcripts/4_2j5wgt_ds.txt
Entries: 851
```

Parse this output and report to the user:
- Confirm successful download
- Show the output file location
- Indicate the number of transcript entries

### 5. Handle Errors

The script returns non-zero exit codes and error messages for failures:

**Common error scenarios:**

1. **Invalid URL format**
   ```
   ❌ Error: Invalid YouTube URL or video ID
   ```
   Report: "The provided URL or video ID is invalid. Please provide a valid YouTube URL or 11-character video ID."

2. **No transcript available**
   ```
   ❌ Error: No transcript found for video
   Could not retrieve a transcript for the video ID
   ```
   Report: "No transcript is available for this video. The creator may have disabled transcripts."

3. **Video unavailable**
   ```
   ❌ Error: Video unavailable or private
   ```
   Report: "The video is unavailable, private, or has been deleted."

4. **Network errors**
   ```
   ❌ Error: Network request failed
   ```
   Report: "Failed to connect to YouTube. Please check your internet connection."

5. **Invalid output directory**
   ```
   ❌ Error: Cannot create output directory
   ```
   Report: "Failed to create output directory. Please check permissions."

### 6. Report Success

On successful execution, provide a clear summary:

```
✅ Transcript downloaded successfully!

📹 Video ID: 4_2j5wgt_ds
📄 File: .work/transcripts/4_2j5wgt_ds.txt
📊 Entries: 851 transcript segments

You can now read the transcript file or use it for analysis.
```

## Output Format

Transcripts are saved as plain text files with the following format:

```
[00:00] Welcome to this video about Product Forge!
[00:15] Today we'll be exploring how to build custom Claude Code plugins.
[00:32] First, let's talk about the plugin architecture.
...
```

Each line contains:
- **Timestamp**: `[MM:SS]` format for easy navigation
- **Text**: The spoken content at that timestamp

The format is designed for:
- Easy reading and searching
- Simple parsing if needed for analysis
- Clear temporal context

## Examples

### Example 1: Basic Usage

Download a transcript using a full YouTube URL:

```bash
/fetch-youtube-transcript "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

Result:
- Transcript saved to `.work/transcripts/dQw4w9WgXcQ.txt`
- Auto-selected language (usually English)

### Example 2: Custom Output Directory

Save transcript to a specific directory:

```bash
/fetch-youtube-transcript "https://youtu.be/dQw4w9WgXcQ" --output ./transcripts
```

Result:
- Transcript saved to `./transcripts/dQw4w9WgXcQ.txt`
- Directory created if it doesn't exist

### Example 3: Specific Language

Request a Spanish transcript:

```bash
/fetch-youtube-transcript "dQw4w9WgXcQ" --language es
```

Result:
- Spanish transcript if available
- Falls back to auto-generated Spanish if manual unavailable
- Error if Spanish not available at all

### Example 4: Video ID Only

Use just the video ID:

```bash
/fetch-youtube-transcript "dQw4w9WgXcQ"
```

Result:
- Same as full URL
- Simpler syntax for known video IDs

## Error Handling

### Validation Errors

**Missing URL:**
```bash
/fetch-youtube-transcript
```
Response: "Error: Video URL or ID required. Usage: /fetch-youtube-transcript <video-url-or-id> [--output DIR]"

**Invalid URL format:**
```bash
/fetch-youtube-transcript "not-a-youtube-url"
```
Response: "Error: Invalid YouTube URL or video ID. Please provide a valid YouTube URL or 11-character video ID."

### API Errors

**No transcript available:**
- The video creator has disabled transcripts
- Automatic captions are disabled
- Video is too new (transcripts not yet generated)

Response: "No transcript available for this video. The creator may have disabled transcripts or automatic captions."

**Video unavailable:**
- Video is private or unlisted
- Video has been deleted
- Video is region-restricted

Response: "Video is unavailable. It may be private, deleted, or region-restricted."

### Network Errors

**Connection failed:**
- Internet connection issues
- YouTube API temporarily unavailable

Response: "Failed to connect to YouTube. Please check your internet connection and try again."

**Rate limiting:**
- Too many requests in short time
- YouTube API quota exceeded

Response: "Request rate limited. Please wait a moment and try again."

## Implementation Tips for Claude Code

### Argument Parsing

The script expects arguments in this order:
```bash
python script.py <video_url> [--output DIR] [--language LANG]
```

Parse the user's `/fetch-youtube-transcript` command to extract these values:
- Strip the `/fetch-youtube-transcript` prefix
- Extract the first argument as video URL
- Look for `--output` flag and next argument
- Look for `--language` flag and next argument

### Error Detection

Monitor the exit code and stderr:
- Exit code 0 = Success
- Exit code 1 = Error (check stderr for details)

Common error patterns in stderr:
- `"Invalid YouTube URL"` → URL validation failed
- `"No transcript found"` → Transcripts disabled
- `"Video unavailable"` → Private/deleted video
- `"Network"` → Connection issues

### Path Handling

The script is bundled with this plugin at `scripts/fetch-youtube-transcript.py` (relative to the plugin directory).

Claude Code will resolve this path automatically when executing from the plugin context.

Output directory handling:
- Relative paths are relative to current working directory
- Absolute paths work as expected
- Default `.work/transcripts/` is relative to current directory

### User Communication

**Be conversational:** Don't just dump the raw script output. Parse it and present it naturally:

Instead of:
```
✅ Transcript downloaded successfully!
Video: 4_2j5wgt_ds
File: .work/transcripts/4_2j5wgt_ds.txt
```

Say:
```
I've downloaded the transcript for video 4_2j5wgt_ds.
The file is saved at .work/transcripts/4_2j5wgt_ds.txt with 851 transcript entries.
```

**Provide context:** If the user might want to do something with the transcript, suggest next steps:

```
Transcript downloaded successfully! You can now:
- Read the file to review the content
- Search for specific topics or keywords
- Use it as reference material
- Process it further with other tools
```

**Handle errors gracefully:** Don't just report the error, explain what it means and what to do:

Instead of:
```
❌ Error: No transcript found
```

Say:
```
This video doesn't have a transcript available. This usually means the creator
disabled automatic captions. Unfortunately, there's no transcript to download.
```

### Working Directory

The script path is relative to the plugin directory and Claude Code handles path resolution automatically.

Output directory considerations:
- Relative paths are relative to current working directory
- Default `.work/transcripts/` will be created relative to where the command is run
- Use absolute paths if you need transcripts in a specific location

### Testing Verification

Before reporting success, verify:
1. Exit code is 0
2. Output file exists at expected path
3. Output file has content (size > 0)

This prevents false positives from script failures.

## Technical Details

### Dependencies

The skill uses `youtube-transcript-api` via `uvx`:
- No installation required
- Isolated execution environment
- Automatic dependency management

### Script Location

The Python script is bundled with the plugin at `scripts/fetch-youtube-transcript.py` (relative to plugin directory).

### Supported URL Formats

The script handles these YouTube URL formats:
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/watch?v=VIDEO_ID&t=123s`
- `https://m.youtube.com/watch?v=VIDEO_ID`
- `VIDEO_ID` (11 characters)

### Language Codes

Common language codes for `--language`:
- `en` - English
- `es` - Spanish
- `fr` - French
- `de` - German
- `ja` - Japanese
- `ko` - Korean
- `zh` - Chinese
- `pt` - Portuguese
- `ru` - Russian
- `ar` - Arabic

Full list: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes

### Output File Naming

Files are named using the video ID:
- Video ID extracted from URL
- Extension: `.txt`
- Example: `dQw4w9WgXcQ.txt`

This ensures:
- Unique filenames per video
- Easy to identify source video
- No special character issues

## Limitations

- Requires internet connection to YouTube
- Only works with public videos or unlisted videos with link
- Requires video to have transcripts enabled (manual or automatic)
- Cannot bypass region restrictions
- Subject to YouTube API rate limits
- Language availability depends on video creator settings

## Future Enhancements

Potential improvements for future versions:
- Batch download multiple videos from a playlist
- Merge transcripts from multiple videos
- Format conversion (SRT, VTT, JSON)
- Translation of transcripts
- Timestamp filtering (download specific time ranges)
- Integration with video analysis tools
