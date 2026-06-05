"""
Video processing utilities for autonomousMOVIEMAKER.
"""

import asyncio
import logging
import shutil
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

async def concatenate_videos(video_paths: List[Path], output_path: Path) -> Path:
    """
    Concatenate multiple video files into a single video file using ffmpeg.
    
    Args:
        video_paths: List of Paths to video files to concatenate.
        output_path: Path where the merged video should be saved.
        
    Returns:
        Path to the concatenated video file.
    """
    if not video_paths:
        raise ValueError("No video clips provided for concatenation")
        
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Filter only existing paths
    existing_paths = [p for p in video_paths if p.exists()]
    if not existing_paths:
        raise FileNotFoundError("None of the provided video clip paths exist on disk.")
        
    # Check if we are dealing with mock/text files (for testing)
    is_mock = any(p.suffix == ".txt" for p in existing_paths)
    if is_mock:
        with open(output_path, "w", encoding="utf-8") as out:
            out.write("MOCK CONCATENATED VIDEO\n")
            out.write("========================\n")
            for i, p in enumerate(existing_paths):
                out.write(f"\nClip {i+1} ({p.name}):\n")
                try:
                    out.write(p.read_text())
                except Exception:
                    out.write(f"[Binary/Non-text data from {p.name}]\n")
        logger.info(f"Successfully compiled mock clips into {output_path}")
        return output_path

    # Check if ffmpeg is available
    if not shutil.which("ffmpeg"):
        raise RuntimeError(
            "ffmpeg command not found on the system. "
            "Please install ffmpeg (e.g., 'sudo apt install ffmpeg') to enable video compilation."
        )
        
    # Create temp directory for inputs list file
    temp_dir = output_path.parent / "temp_concat"
    temp_dir.mkdir(parents=True, exist_ok=True)
    list_file_path = temp_dir / "ffmpeg_concat_list.txt"
    
    try:
        # Write list file for ffmpeg concat demuxer
        with open(list_file_path, "w", encoding="utf-8") as f:
            for path in existing_paths:
                # ffmpeg requires escaping single quotes in filenames
                escaped_path = str(path.absolute()).replace("'", "'\\''")
                f.write(f"file '{escaped_path}'\n")
                
        # Run ffmpeg command
        # -y: overwrite output files without asking
        # -f concat: use the concat demuxer
        # -safe 0: allow unsafe paths (absolute paths, etc.)
        # -c copy: stream copy the codecs without re-encoding (extremely fast!)
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_file_path.absolute()),
            "-c", "copy",
            str(output_path.absolute())
        ]
        
        logger.info(f"Running ffmpeg concatenation command: {' '.join(cmd)}")
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            err_msg = stderr.decode().strip()
            logger.error(f"ffmpeg failed with return code {process.returncode}: {err_msg}")
            raise RuntimeError(f"ffmpeg video concatenation failed: {err_msg}")
            
        logger.info(f"Successfully concatenated {len(existing_paths)} clips into {output_path}")
        return output_path
        
async def create_video_from_image(image_path: Path, output_path: Path, duration: float = 5.0, fps: int = 24) -> Path:
    """
    Create a video clip from a single image using ffmpeg.
    Useful as a fallback or for animating stills.
    """
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # If mock, just copy
    if image_path.suffix == ".txt":
        output_path.write_text(f"MOCK VIDEO FROM IMAGE: {image_path.name}\nDuration: {duration}s")
        return output_path

    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg not found")

    # Command to create a video from a single image with a slight zoom effect (Ken Burns)
    # -loop 1: loop the input image
    # -t: duration
    # -vf: video filter for scale and zoom
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(image_path.absolute()),
        "-vf", f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,zoompan=z='min(zoom+0.001,1.5)':d={int(duration*fps)}:s=1920x1080",
        "-c:v", "libx264",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        str(output_path.absolute())
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        logger.error(f"ffmpeg failed: {stderr.decode()}")
        # Fallback to simple static video if zoompan fails
        cmd_simple = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(image_path.absolute()),
            "-c:v", "libx264",
            "-t", str(duration),
            "-pix_fmt", "yuv420p",
            "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
            str(output_path.absolute())
        ]
        process = await asyncio.create_subprocess_exec(*cmd_simple)
        await process.communicate()

    return output_path
