"""
Video composition module for creating the final MP4 output.
Uses moviepy to combine rendered frames with the original audio.
"""

import os
import sys
import tempfile
import numpy as np
from typing import Callable, Optional
from moviepy import VideoClip, AudioFileClip


def get_writable_temp_dir():
    """Get a writable temp directory that works in bundled apps."""
    # For bundled macOS apps, the cwd might be read-only
    # Use system temp directory instead
    temp_dir = tempfile.gettempdir()

    # Create a subdirectory for our app
    app_temp = os.path.join(temp_dir, "audio-reactive-video")
    if not os.path.exists(app_temp):
        os.makedirs(app_temp, exist_ok=True)

    return app_temp


class VideoComposer:
    """Composes video from frames and audio."""

    def __init__(
        self,
        audio_path: str,
        output_path: str,
        fps: int = 30
    ):
        """
        Initialize the video composer.

        Args:
            audio_path: Path to the audio file
            output_path: Path for the output MP4
            fps: Frames per second
        """
        self.audio_path = audio_path
        self.output_path = output_path
        self.fps = fps

        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def compose(
        self,
        frames: list,
        duration: float,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> str:
        """
        Compose video from pre-rendered frames.

        Args:
            frames: List of numpy arrays (H, W, 3) representing each frame
            duration: Total video duration in seconds
            progress_callback: Optional callback(stage, progress) for updates

        Returns:
            Path to the output video file
        """
        if progress_callback:
            progress_callback("composing", 0.0)

        frames_array = frames if isinstance(frames, list) else list(frames)

        def make_frame(t):
            """Get frame at time t."""
            frame_idx = int(t * self.fps)
            frame_idx = min(frame_idx, len(frames_array) - 1)
            return frames_array[frame_idx]

        # Create video clip from frames
        video = VideoClip(make_frame, duration=duration)

        # Load and attach audio
        audio = AudioFileClip(self.audio_path)
        video = video.with_audio(audio)

        if progress_callback:
            progress_callback("encoding", 0.3)

        # Get writable temp directory for moviepy's temp files
        temp_dir = get_writable_temp_dir()
        temp_audiofile = os.path.join(temp_dir, "temp_audio.m4a")

        # Write the final video
        video.write_videofile(
            self.output_path,
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile=temp_audiofile,
            logger=None  # Suppress moviepy's verbose output
        )

        # Cleanup
        audio.close()
        video.close()

        if progress_callback:
            progress_callback("complete", 1.0)

        return self.output_path

    def compose_streaming(
        self,
        frame_generator,
        duration: float,
        resolution: tuple,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> str:
        """
        Compose video by streaming frames (lower memory usage).

        Args:
            frame_generator: Generator yielding numpy arrays
            duration: Total video duration in seconds
            resolution: Tuple of (width, height)
            progress_callback: Optional callback(stage, progress)

        Returns:
            Path to the output video file
        """
        # For streaming, we need to collect frames first since moviepy
        # needs random access. For true streaming, would need different approach.
        frames = list(frame_generator)
        return self.compose(frames, duration, progress_callback)
