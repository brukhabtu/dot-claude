#!/usr/bin/env python3

import asyncio
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import Optional
from playwright.async_api import async_playwright

# JavaScript functions to be injected into the browser
TRANSCRIPT_FUNCTIONS = """
// Function to wait for an element to exist
function waitForElement(selector, timeout = 10000) {
    return new Promise((resolve, reject) => {
        const element = document.querySelector(selector);
        if (element) {
            resolve(element);
            return;
        }
        
        const observer = new MutationObserver((mutations, obs) => {
            const element = document.querySelector(selector);
            if (element) {
                obs.disconnect();
                resolve(element);
            }
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        setTimeout(() => {
            observer.disconnect();
            reject(new Error(`Element ${selector} not found within ${timeout}ms`));
        }, timeout);
    });
}

// Function to expand video description
async function expandDescription() {
    try {
        console.log('Looking for description expand button...');
        const expandBtn = await waitForElement("div#snippet.style-scope.ytd-text-inline-expander", 5000);
        expandBtn.click();
        console.log('Description expanded!');
        return true;
    } catch (error) {
        console.log('Could not find/click description expand button:', error.message);
        return false;
    }
}

// Function to show transcript
async function showTranscript() {
    try {
        console.log('Looking for transcript button...');
        const transcriptSection = await waitForElement("ytd-video-description-transcript-section-renderer", 5000);
        const button = transcriptSection.querySelector("button.yt-spec-button-shape-next");
        if (button) {
            button.click();
            console.log('Transcript button clicked!');
            await new Promise(resolve => setTimeout(resolve, 2000));
            return true;
        } else {
            throw new Error('Button not found within transcript section');
        }
    } catch (error) {
        console.log('Could not find/click transcript button:', error.message);
        return false;
    }
}

// Function to extract transcript
function extractYouTubeTranscript() {
    let transcript = '';
    
    const textElements = document.querySelectorAll('yt-formatted-string.segment-text');
    console.log(`Found ${textElements.length} text elements`);
    
    if (textElements.length === 0) {
        console.log('No transcript text elements found');
        return '';
    }
    
    textElements.forEach((element, index) => {
        const text = element.textContent.trim();
        if (text) {
            transcript += text + '\\n';
        }
    });
    
    return transcript.trim();
}

// Main function to do everything
async function getFullTranscript() {
    console.log('Starting transcript extraction process...');
    
    await expandDescription();
    
    const transcriptShown = await showTranscript();
    
    if (!transcriptShown) {
        console.log('Could not show transcript panel');
        return '';
    }
    
    console.log('Waiting for transcript to load...');
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    const transcript = extractYouTubeTranscript();
    console.log('Transcript length:', transcript.length);
    
    return transcript;
}

// Execute and return the transcript
(async () => {
    return await getFullTranscript();
})()
"""


async def extract_youtube_transcript(video_url: str, output_file: Optional[str] = None, headless: bool = True):
    """
    Extract transcript from a YouTube video.
    
    Args:
        video_url: YouTube video URL
        output_file: Optional output filename (will auto-generate if not provided)
        headless: Whether to run browser in headless mode
    
    Returns:
        Dictionary with success status and extracted data
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=headless,
            slow_mo=1000  # Slow down actions for debugging
        )
        
        try:
            page = await browser.new_page()
            
            # Navigate to the YouTube video
            print(f"Navigating to: {video_url}")
            await page.goto(video_url, wait_until='networkidle')
            
            # Wait for page to fully load
            await page.wait_for_timeout(3000)
            
            # Execute the transcript extraction in the browser
            print("Executing transcript extraction...")
            transcript = await page.evaluate(TRANSCRIPT_FUNCTIONS)
            
            if not transcript:
                raise Exception("No transcript found or extraction failed")
            
            # Get video title for filename if no output file specified
            if not output_file:
                title = await page.evaluate("""
                    () => {
                        const titleElement = document.querySelector('h1.ytd-watch-metadata yt-formatted-string');
                        return titleElement ? titleElement.textContent.trim() : 'youtube-transcript';
                    }
                """)
                
                # Clean filename
                clean_title = re.sub(r'[^\w\s-]', '', title)
                clean_title = re.sub(r'\s+', '-', clean_title).lower()
                output_file = f"{clean_title}.md"
            
            # Get video title for markdown
            video_title = await page.evaluate("""
                () => {
                    const titleElement = document.querySelector('h1.ytd-watch-metadata yt-formatted-string');
                    return titleElement ? titleElement.textContent.trim() : 'Unknown Title';
                }
            """)
            
            # Create markdown content with Obsidian properties (YAML frontmatter)
            markdown_content = f"""---
title: {video_title}
source: youtube
url: {video_url}
date_extracted: {datetime.now().strftime('%Y-%m-%d')}
time_extracted: {datetime.now().strftime('%H:%M:%S')}
tags:
  - youtube-transcript
  - video
---

# {video_title}

{transcript}
"""
            
            # Save to file
            Path(output_file).write_text(markdown_content, encoding='utf-8')
            print(f"Transcript saved to: {output_file}")
            print(f"Transcript length: {len(transcript.splitlines())} segments")
            
            return {
                "success": True,
                "file": output_file,
                "transcript": transcript,
                "title": video_title
            }
            
        except Exception as e:
            print(f"Error extracting transcript: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            await browser.close()


async def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python extract-yt-transcript.py <youtube-url> [output-file.md]")
        print('Example: python extract-yt-transcript.py "https://www.youtube.com/watch?v=VIDEO_ID" transcript.md')
        sys.exit(1)
    
    video_url = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = await extract_youtube_transcript(video_url, output_file)
    
    if result["success"]:
        print("✅ Success!")
        print(f"📁 File: {result['file']}")
        print(f"📝 Title: {result['title']}")
    else:
        print("❌ Failed!")
        print(f"Error: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())