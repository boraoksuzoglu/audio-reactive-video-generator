#!/usr/bin/env python3
"""
Audio Reactive Video Generator - CLI Interface

Generates an MP4 video with audio-reactive image effects
from an audio file and background image.

Usage:
    python main.py --audio audio/input.mp3 --image image/background.png --output output/output.mp4
"""

import argparse
import os
import sys
import time

from core.audio import AudioProcessor
from core.renderer import FrameRenderer
from core.video import VideoComposer
from core.effects import EffectConfig

# Configuration constants
FPS = 30


SUPPORTED_AUDIO = ('.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac', '.wma', '.aiff', '.mp4', '.webm')
SUPPORTED_IMAGE = ('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff', '.gif')


def validate_inputs(audio_path: str, image_path: str) -> bool:
    """Validate that input files exist and have correct formats."""
    errors = []

    if not os.path.exists(audio_path):
        errors.append(f"Audio file not found: {audio_path}")
    elif not audio_path.lower().endswith(SUPPORTED_AUDIO):
        errors.append(f"Unsupported audio format: {audio_path}")

    if not os.path.exists(image_path):
        errors.append(f"Image file not found: {image_path}")
    elif not image_path.lower().endswith(SUPPORTED_IMAGE):
        errors.append(f"Unsupported image format: {image_path}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return False

    return True


def print_progress(current: int, total: int, prefix: str = "Rendering"):
    """Print a progress bar to stdout."""
    percent = current / total * 100
    bar_length = 40
    filled = int(bar_length * current / total)
    bar = '=' * filled + '-' * (bar_length - filled)
    print(f"\r{prefix}: [{bar}] {percent:.1f}% ({current}/{total})", end='', flush=True)


def generate_video(
    audio_path: str,
    image_path: str,
    output_path: str,
    preset: str = 'energetic',
    verbose: bool = True
) -> str:
    """
    Generate an audio-reactive video.

    Args:
        audio_path: Path to input audio file
        image_path: Path to input image file
        output_path: Path for output MP4 file
        preset: Effect preset name ('subtle', 'energetic', 'aggressive', 'cinematic')
        verbose: Whether to print progress

    Returns:
        Path to the generated video
    """
    start_time = time.time()

    # Step 1: Process audio
    if verbose:
        print(f"Loading audio: {audio_path}")

    audio = AudioProcessor(audio_path, fps=FPS)
    audio.load()

    if verbose:
        print(f"  Duration: {audio.duration:.2f}s")
        print(f"  Frames: {audio.frame_count}")
        print("Extracting audio features...")

    features = audio.extract_features()

    # Step 2: Initialize renderer with effect preset
    if verbose:
        print(f"Loading background: {image_path}")
        print(f"Using effect preset: {preset}")

    effect_config = EffectConfig.from_preset(preset)
    renderer = FrameRenderer(
        background_path=image_path,
        effect_config=effect_config
    )

    width, height = renderer.get_resolution()
    if verbose:
        print(f"  Resolution: {width}x{height}")

    # Step 3: Render all frames
    if verbose:
        print("Rendering frames...")

    frames = []
    total_frames = features.frame_count

    for i in range(total_frames):
        frame = renderer.render_frame(
            audio_level=features.overall_energy[i],
            bass_level=features.bass_energy[i],
            frame_idx=i
        )
        frames.append(frame)

        if verbose and (i % 10 == 0 or i == total_frames - 1):
            print_progress(i + 1, total_frames, "Frames")

    if verbose:
        print()  # New line after progress bar

    # Step 4: Compose video
    if verbose:
        print("Composing video...")

    # Convert PIL images to numpy arrays
    import numpy as np
    frames_np = [np.array(f) for f in frames]

    composer = VideoComposer(
        audio_path=audio_path,
        output_path=output_path,
        fps=FPS
    )

    output = composer.compose(frames_np, audio.duration)

    # Print summary
    elapsed = time.time() - start_time
    if verbose:
        print(f"\nVideo generated successfully!")
        print(f"  Output: {output}")
        print(f"  Time: {elapsed:.1f}s")
        print(f"  Speed: {audio.duration / elapsed:.1f}x realtime")

    return output


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Generate audio-reactive video with image effects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Effect Presets:
    subtle      - Gentle, understated effects
    energetic   - Balanced, dynamic effects (default)
    aggressive  - Bold, intense effects
    cinematic   - Film-like, atmospheric effects
    dreamy      - Soft, ethereal glow
    retro       - VHS / synthwave style
    minimal     - Clean, subtle pulse
    psychedelic - Trippy, experimental
    bass        - Punchy bass response
    noir        - Dark, moody contrast

Supported Formats:
    Audio: MP3, WAV, FLAC, OGG, M4A, AAC, WMA, AIFF, MP4, WebM
    Image: PNG, JPG, JPEG, WebP, BMP, TIFF, GIF

Examples:
    python main.py --audio audio/input.mp3 --image image/background.png
    python main.py -a music.mp3 -i cover.png -o video.mp4 --preset aggressive
    python main.py -a track.m4a -i artwork.webp -o output.mp4 --preset retro
        """
    )

    parser.add_argument(
        '-a', '--audio',
        required=True,
        help='Path to input audio file'
    )
    parser.add_argument(
        '-i', '--image',
        required=True,
        help='Path to input background image'
    )
    parser.add_argument(
        '-o', '--output',
        default='output/output.mp4',
        help='Path for output MP4 video (default: output/output.mp4)'
    )
    parser.add_argument(
        '-p', '--preset',
        choices=['subtle', 'energetic', 'aggressive', 'cinematic', 'dreamy', 'retro', 'minimal', 'psychedelic', 'bass', 'noir'],
        default='energetic',
        help='Effect preset (default: energetic)'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress progress output'
    )

    args = parser.parse_args()

    # Validate inputs
    if not validate_inputs(args.audio, args.image):
        sys.exit(1)

    # Ensure output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        generate_video(
            audio_path=args.audio,
            image_path=args.image,
            output_path=args.output,
            preset=args.preset,
            verbose=not args.quiet
        )
    except KeyboardInterrupt:
        print("\nCancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
