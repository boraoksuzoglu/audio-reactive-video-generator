"""
Frame rendering module for generating audio-reactive visuals.
Applies dynamic effects to the image based on audio features.
No overlays - the image itself is transformed.
"""

import numpy as np
from PIL import Image
from typing import Tuple, Generator, Optional, Callable

from .effects import EffectConfig, ImageEffectsProcessor


class FrameRenderer:
    """Renders video frames with audio-reactive image effects."""

    def __init__(
        self,
        background_path: str,
        effect_config: Optional[EffectConfig] = None
    ):
        """
        Initialize the frame renderer.

        Args:
            background_path: Path to the PNG background image
            effect_config: Configuration for visual effects (defaults to 'energetic' preset)
        """
        self.background_path = background_path

        # Load the background image
        self.background = Image.open(background_path).convert('RGB')
        self.width, self.height = self.background.size

        # Initialize effects processor
        self.config = effect_config or EffectConfig.from_preset('energetic')
        self.effects = ImageEffectsProcessor(self.background, self.config)

    def set_effect_config(self, config: EffectConfig):
        """Update effect configuration."""
        self.config = config
        self.effects = ImageEffectsProcessor(self.background, config)

    def render_frame(
        self,
        audio_level: float,
        bass_level: float,
        frame_idx: int
    ) -> Image.Image:
        """
        Render a single frame with audio-reactive effects.

        Args:
            audio_level: Overall audio energy (0-1)
            bass_level: Low frequency energy (0-1)
            frame_idx: Current frame index

        Returns:
            PIL Image of the rendered frame
        """
        return self.effects.process_frame(audio_level, bass_level, frame_idx)

    def generate_frames(
        self,
        audio_data: np.ndarray,
        bass_data: np.ndarray,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Generator[np.ndarray, None, None]:
        """
        Generate all video frames as numpy arrays.

        Args:
            audio_data: Array of overall audio levels per frame (0-1)
            bass_data: Array of bass levels per frame (0-1)
            progress_callback: Optional callback(current, total) for progress updates

        Yields:
            Numpy arrays (H, W, 3) for each frame
        """
        total_frames = len(audio_data)

        for i in range(total_frames):
            frame = self.render_frame(
                audio_level=audio_data[i],
                bass_level=bass_data[i],
                frame_idx=i
            )
            yield np.array(frame)

            if progress_callback:
                progress_callback(i + 1, total_frames)

    def get_resolution(self) -> Tuple[int, int]:
        """Get the output resolution (width, height)."""
        return self.width, self.height
