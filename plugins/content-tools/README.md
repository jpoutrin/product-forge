# Content Tools Plugin

Content extraction and processing utilities for developers working with various content sources.

## Overview

This plugin provides skills for extracting and processing content from external sources like videos, podcasts, articles, and more. Each skill wraps robust extraction tools with a simple, user-friendly interface.

## Skills

### fetch-youtube-transcript

Download YouTube video transcripts as readable text files with timestamps.

**Usage:**
```
/fetch-youtube-transcript <video-url-or-id> [--output DIR] [--language LANG]
```

**Use cases:**
- Extract transcripts for analysis or documentation
- Create text versions of video content
- Review video content without watching
- Generate training data or research materials

## Future Roadmap

Planned skills for content extraction:

- **podcast-transcript**: Extract transcripts from podcast episodes
- **article-extract**: Clean extraction of article text from web pages
- **rss-fetch**: Fetch and parse RSS/Atom feeds
- **pdf-extract**: Extract text and structure from PDF documents

## Implementation

All skills in this plugin follow the Product Forge skill pattern:
- Simple, focused interfaces
- Robust error handling
- Clear success/failure messages
- Consistent argument parsing

Content extraction is powered by specialized Python tools run via `uvx` for dependency isolation.
