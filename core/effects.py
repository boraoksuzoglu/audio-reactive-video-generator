"""
Audio-reactive image effects module.
Applies dynamic visual transformations to images based on audio features.
All effects modify the image itself - no overlays or separate elements.
"""

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import math


@dataclass
class EffectConfig:
    """Configuration for all visual effects."""

    # Scale pulsing (zoom in/out)
    scale_enabled: bool = True
    scale_intensity: float = 0.5  # 0-1
    scale_min: float = 1.0
    scale_max: float = 1.08

    # Camera shake / micro movement
    shake_enabled: bool = True
    shake_intensity: float = 0.4  # 0-1
    shake_max_pixels: int = 15

    # Glow / bloom
    glow_enabled: bool = True
    glow_intensity: float = 0.5  # 0-1
    glow_radius_min: int = 0
    glow_radius_max: int = 8

    # Color saturation
    saturation_enabled: bool = True
    saturation_intensity: float = 0.5  # 0-1
    saturation_min: float = 0.9
    saturation_max: float = 1.4

    # Contrast modulation
    contrast_enabled: bool = True
    contrast_intensity: float = 0.4  # 0-1
    contrast_min: float = 0.95
    contrast_max: float = 1.2

    # Brightness modulation
    brightness_enabled: bool = True
    brightness_intensity: float = 0.3  # 0-1
    brightness_min: float = 0.95
    brightness_max: float = 1.15

    # Hue shifting
    hue_enabled: bool = False
    hue_intensity: float = 0.3  # 0-1
    hue_max_shift: float = 15.0  # degrees

    # Vignette pulsing
    vignette_enabled: bool = True
    vignette_intensity: float = 0.5  # 0-1
    vignette_min: float = 0.0
    vignette_max: float = 0.4

    # Chromatic aberration
    chromatic_enabled: bool = True
    chromatic_intensity: float = 0.4  # 0-1
    chromatic_max_offset: int = 8

    # Motion blur on beats
    blur_enabled: bool = False
    blur_intensity: float = 0.3  # 0-1
    blur_max_radius: int = 3

    # Warp distortion
    warp_enabled: bool = False
    warp_intensity: float = 0.3  # 0-1
    warp_strength: float = 0.02

    @classmethod
    def from_preset(cls, preset_name: str) -> 'EffectConfig':
        """Create config from a named preset."""
        presets = {
            # Gentle, understated - good for acoustic/ambient
            'subtle': cls(
                scale_intensity=0.3, scale_max=1.04,
                shake_intensity=0.2, shake_max_pixels=8,
                glow_intensity=0.3, glow_radius_max=4,
                saturation_intensity=0.3, saturation_max=1.2,
                contrast_intensity=0.2, contrast_max=1.1,
                brightness_intensity=0.2, brightness_max=1.08,
                hue_enabled=False,
                vignette_intensity=0.3, vignette_max=0.25,
                chromatic_enabled=False,
                blur_enabled=False,
                warp_enabled=False
            ),
            # Balanced, dynamic - good for pop/rock
            'energetic': cls(
                scale_intensity=0.6, scale_max=1.10,
                shake_intensity=0.5, shake_max_pixels=18,
                glow_intensity=0.6, glow_radius_max=10,
                saturation_intensity=0.6, saturation_max=1.5,
                contrast_intensity=0.5, contrast_max=1.25,
                brightness_intensity=0.4, brightness_max=1.2,
                hue_enabled=True, hue_intensity=0.3,
                vignette_intensity=0.6, vignette_max=0.45,
                chromatic_enabled=True, chromatic_intensity=0.5,
                blur_enabled=False,
                warp_enabled=False
            ),
            # Bold, intense - good for EDM/metal
            'aggressive': cls(
                scale_intensity=0.8, scale_max=1.15,
                shake_intensity=0.7, shake_max_pixels=25,
                glow_intensity=0.8, glow_radius_max=15,
                saturation_intensity=0.8, saturation_max=1.7,
                contrast_intensity=0.7, contrast_max=1.4,
                brightness_intensity=0.6, brightness_max=1.3,
                hue_enabled=True, hue_intensity=0.5, hue_max_shift=25,
                vignette_intensity=0.8, vignette_max=0.6,
                chromatic_enabled=True, chromatic_intensity=0.7, chromatic_max_offset=12,
                blur_enabled=True, blur_intensity=0.5,
                warp_enabled=True, warp_intensity=0.4
            ),
            # Film-like, atmospheric - good for soundtracks
            'cinematic': cls(
                scale_intensity=0.4, scale_max=1.06,
                shake_intensity=0.25, shake_max_pixels=10,
                glow_intensity=0.5, glow_radius_max=6,
                saturation_intensity=0.4, saturation_min=0.85, saturation_max=1.15,
                contrast_intensity=0.5, contrast_min=0.9, contrast_max=1.3,
                brightness_intensity=0.35, brightness_min=0.9, brightness_max=1.1,
                hue_enabled=False,
                vignette_enabled=True, vignette_intensity=0.7, vignette_min=0.15, vignette_max=0.5,
                chromatic_enabled=True, chromatic_intensity=0.3, chromatic_max_offset=5,
                blur_enabled=False,
                warp_enabled=False
            ),
            # Dreamy, floaty - good for lo-fi/chillwave
            'dreamy': cls(
                scale_intensity=0.35, scale_max=1.05,
                shake_intensity=0.15, shake_max_pixels=6,
                glow_enabled=True, glow_intensity=0.75, glow_radius_max=12,
                saturation_intensity=0.5, saturation_min=0.8, saturation_max=1.3,
                contrast_intensity=0.3, contrast_min=0.9, contrast_max=1.15,
                brightness_intensity=0.4, brightness_min=0.95, brightness_max=1.15,
                hue_enabled=True, hue_intensity=0.25, hue_max_shift=12,
                vignette_enabled=True, vignette_intensity=0.5, vignette_min=0.1, vignette_max=0.35,
                chromatic_enabled=True, chromatic_intensity=0.35, chromatic_max_offset=6,
                blur_enabled=True, blur_intensity=0.2, blur_max_radius=2,
                warp_enabled=False
            ),
            # Retro VHS look - good for synthwave/80s
            'retro': cls(
                scale_intensity=0.4, scale_max=1.06,
                shake_intensity=0.35, shake_max_pixels=12,
                glow_enabled=True, glow_intensity=0.5, glow_radius_max=8,
                saturation_intensity=0.6, saturation_min=1.0, saturation_max=1.6,
                contrast_intensity=0.55, contrast_min=0.95, contrast_max=1.35,
                brightness_intensity=0.35, brightness_max=1.15,
                hue_enabled=True, hue_intensity=0.4, hue_max_shift=18,
                vignette_enabled=True, vignette_intensity=0.65, vignette_min=0.12, vignette_max=0.45,
                chromatic_enabled=True, chromatic_intensity=0.6, chromatic_max_offset=10,
                blur_enabled=False,
                warp_enabled=True, warp_intensity=0.25, warp_strength=0.015
            ),
            # Clean, minimal pulse - good for podcasts/speech
            'minimal': cls(
                scale_enabled=True, scale_intensity=0.25, scale_max=1.03,
                shake_enabled=False,
                glow_enabled=False,
                saturation_enabled=False,
                contrast_enabled=True, contrast_intensity=0.15, contrast_max=1.08,
                brightness_enabled=True, brightness_intensity=0.2, brightness_max=1.06,
                hue_enabled=False,
                vignette_enabled=True, vignette_intensity=0.25, vignette_max=0.2,
                chromatic_enabled=False,
                blur_enabled=False,
                warp_enabled=False
            ),
            # Psychedelic, trippy - good for experimental
            'psychedelic': cls(
                scale_intensity=0.7, scale_max=1.12,
                shake_intensity=0.5, shake_max_pixels=20,
                glow_enabled=True, glow_intensity=0.7, glow_radius_max=14,
                saturation_intensity=0.85, saturation_min=0.9, saturation_max=1.9,
                contrast_intensity=0.6, contrast_max=1.35,
                brightness_intensity=0.5, brightness_max=1.25,
                hue_enabled=True, hue_intensity=0.8, hue_max_shift=35,
                vignette_enabled=True, vignette_intensity=0.55, vignette_max=0.4,
                chromatic_enabled=True, chromatic_intensity=0.75, chromatic_max_offset=14,
                blur_enabled=True, blur_intensity=0.35,
                warp_enabled=True, warp_intensity=0.55, warp_strength=0.025
            ),
            # Punchy bass response - good for hip-hop/trap
            'bass': cls(
                scale_intensity=0.75, scale_max=1.12,
                shake_intensity=0.65, shake_max_pixels=22,
                glow_enabled=True, glow_intensity=0.55, glow_radius_max=10,
                saturation_intensity=0.5, saturation_max=1.4,
                contrast_intensity=0.65, contrast_min=0.92, contrast_max=1.35,
                brightness_intensity=0.55, brightness_max=1.22,
                hue_enabled=False,
                vignette_enabled=True, vignette_intensity=0.7, vignette_min=0.08, vignette_max=0.5,
                chromatic_enabled=True, chromatic_intensity=0.55, chromatic_max_offset=9,
                blur_enabled=True, blur_intensity=0.4, blur_max_radius=3,
                warp_enabled=False
            ),
            # Noir, moody - good for jazz/blues
            'noir': cls(
                scale_intensity=0.3, scale_max=1.04,
                shake_intensity=0.2, shake_max_pixels=8,
                glow_enabled=True, glow_intensity=0.4, glow_radius_max=5,
                saturation_enabled=True, saturation_intensity=0.5, saturation_min=0.6, saturation_max=0.95,
                contrast_intensity=0.6, contrast_min=0.85, contrast_max=1.4,
                brightness_intensity=0.35, brightness_min=0.85, brightness_max=1.05,
                hue_enabled=False,
                vignette_enabled=True, vignette_intensity=0.85, vignette_min=0.2, vignette_max=0.65,
                chromatic_enabled=False,
                blur_enabled=False,
                warp_enabled=False
            ),
        }
        return presets.get(preset_name, cls())

    @classmethod
    def get_preset_names(cls) -> list:
        """Get list of available preset names."""
        return ['subtle', 'energetic', 'aggressive', 'cinematic', 'dreamy', 'retro', 'minimal', 'psychedelic', 'bass', 'noir']

    @classmethod
    def get_preset_description(cls, preset_name: str) -> str:
        """Get description for a preset."""
        descriptions = {
            'subtle': 'Gentle, understated effects',
            'energetic': 'Balanced, dynamic response',
            'aggressive': 'Bold, intense visuals',
            'cinematic': 'Film-like atmosphere',
            'dreamy': 'Soft, ethereal glow',
            'retro': 'VHS / synthwave style',
            'minimal': 'Clean, subtle pulse',
            'psychedelic': 'Trippy, experimental',
            'bass': 'Punchy bass response',
            'noir': 'Dark, moody contrast',
        }
        return descriptions.get(preset_name, '')

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            'scale': {'enabled': self.scale_enabled, 'intensity': self.scale_intensity},
            'shake': {'enabled': self.shake_enabled, 'intensity': self.shake_intensity},
            'glow': {'enabled': self.glow_enabled, 'intensity': self.glow_intensity},
            'saturation': {'enabled': self.saturation_enabled, 'intensity': self.saturation_intensity},
            'contrast': {'enabled': self.contrast_enabled, 'intensity': self.contrast_intensity},
            'brightness': {'enabled': self.brightness_enabled, 'intensity': self.brightness_intensity},
            'hue': {'enabled': self.hue_enabled, 'intensity': self.hue_intensity},
            'vignette': {'enabled': self.vignette_enabled, 'intensity': self.vignette_intensity},
            'chromatic': {'enabled': self.chromatic_enabled, 'intensity': self.chromatic_intensity},
            'blur': {'enabled': self.blur_enabled, 'intensity': self.blur_intensity},
            'warp': {'enabled': self.warp_enabled, 'intensity': self.warp_intensity},
        }


class ImageEffectsProcessor:
    """Applies audio-reactive effects to images."""

    def __init__(self, base_image: Image.Image, config: EffectConfig):
        """
        Initialize the effects processor.

        Args:
            base_image: The original PNG image to transform
            config: Effect configuration
        """
        self.base_image = base_image.convert('RGB')
        self.config = config
        self.width, self.height = base_image.size

        # Pre-compute vignette mask for performance
        self._vignette_cache = {}

        # State for smooth interpolation
        self._prev_values = {}

    def _lerp(self, a: float, b: float, t: float) -> float:
        """Linear interpolation."""
        return a + (b - a) * t

    def _smooth_value(self, key: str, target: float, smoothing: float = 0.3) -> float:
        """Smooth a value over time to prevent jitter."""
        if key not in self._prev_values:
            self._prev_values[key] = target
        self._prev_values[key] = self._lerp(self._prev_values[key], target, smoothing)
        return self._prev_values[key]

    def _apply_scale(self, img: Image.Image, audio_level: float) -> Image.Image:
        """Apply scale pulsing effect."""
        if not self.config.scale_enabled:
            return img

        intensity = audio_level * self.config.scale_intensity
        scale = self._lerp(self.config.scale_min, self.config.scale_max, intensity)
        scale = self._smooth_value('scale', scale, 0.4)

        # Calculate new dimensions
        new_w = int(self.width * scale)
        new_h = int(self.height * scale)

        # Resize and crop to center
        scaled = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # Crop to original size from center
        left = (new_w - self.width) // 2
        top = (new_h - self.height) // 2
        return scaled.crop((left, top, left + self.width, top + self.height))

    def _apply_shake(self, img: Image.Image, audio_level: float, frame_idx: int) -> Image.Image:
        """Apply camera shake / micro movement."""
        if not self.config.shake_enabled:
            return img

        intensity = audio_level * self.config.scale_intensity
        max_offset = int(self.config.shake_max_pixels * intensity)

        if max_offset < 1:
            return img

        # Use frame index for pseudo-random but deterministic shake
        np.random.seed(frame_idx)
        offset_x = np.random.randint(-max_offset, max_offset + 1)
        offset_y = np.random.randint(-max_offset, max_offset + 1)

        # Smooth the shake
        offset_x = int(self._smooth_value('shake_x', offset_x, 0.5))
        offset_y = int(self._smooth_value('shake_y', offset_y, 0.5))

        # Create larger canvas and paste with offset
        canvas = Image.new('RGB', (self.width, self.height), (0, 0, 0))
        canvas.paste(img, (offset_x, offset_y))

        return canvas

    def _apply_glow(self, img: Image.Image, audio_level: float) -> Image.Image:
        """Apply glow/bloom effect."""
        if not self.config.glow_enabled:
            return img

        intensity = audio_level * self.config.glow_intensity
        radius = int(self._lerp(self.config.glow_radius_min, self.config.glow_radius_max, intensity))
        radius = int(self._smooth_value('glow', radius, 0.4))

        if radius < 1:
            return img

        # Create bloom by blurring and blending
        blurred = img.filter(ImageFilter.GaussianBlur(radius=radius))

        # Blend original with bloom
        blend_amount = min(0.3 * intensity, 0.4)
        return Image.blend(img, blurred, blend_amount)

    def _apply_saturation(self, img: Image.Image, audio_level: float) -> Image.Image:
        """Apply saturation modulation."""
        if not self.config.saturation_enabled:
            return img

        intensity = audio_level * self.config.saturation_intensity
        factor = self._lerp(self.config.saturation_min, self.config.saturation_max, intensity)
        factor = self._smooth_value('saturation', factor, 0.35)

        enhancer = ImageEnhance.Color(img)
        return enhancer.enhance(factor)

    def _apply_contrast(self, img: Image.Image, audio_level: float) -> Image.Image:
        """Apply contrast modulation."""
        if not self.config.contrast_enabled:
            return img

        intensity = audio_level * self.config.contrast_intensity
        factor = self._lerp(self.config.contrast_min, self.config.contrast_max, intensity)
        factor = self._smooth_value('contrast', factor, 0.35)

        enhancer = ImageEnhance.Contrast(img)
        return enhancer.enhance(factor)

    def _apply_brightness(self, img: Image.Image, audio_level: float) -> Image.Image:
        """Apply brightness modulation."""
        if not self.config.brightness_enabled:
            return img

        intensity = audio_level * self.config.brightness_intensity
        factor = self._lerp(self.config.brightness_min, self.config.brightness_max, intensity)
        factor = self._smooth_value('brightness', factor, 0.35)

        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(factor)

    def _apply_hue_shift(self, img: Image.Image, audio_level: float) -> Image.Image:
        """Apply hue shifting effect."""
        if not self.config.hue_enabled:
            return img

        intensity = audio_level * self.config.hue_intensity
        shift = self._lerp(0, self.config.hue_max_shift, intensity)
        shift = self._smooth_value('hue', shift, 0.3)

        if abs(shift) < 1:
            return img

        # Convert to HSV, shift hue, convert back
        img_array = np.array(img, dtype=np.float32)

        # Simple RGB to HSV and back with hue rotation
        # Normalize to 0-1
        img_array = img_array / 255.0

        # Apply hue rotation matrix
        angle = np.radians(shift)
        cos_a, sin_a = np.cos(angle), np.sin(angle)

        # Hue rotation matrix
        matrix = np.array([
            [0.213 + 0.787*cos_a - 0.213*sin_a, 0.715 - 0.715*cos_a - 0.715*sin_a, 0.072 - 0.072*cos_a + 0.928*sin_a],
            [0.213 - 0.213*cos_a + 0.143*sin_a, 0.715 + 0.285*cos_a + 0.140*sin_a, 0.072 - 0.072*cos_a - 0.283*sin_a],
            [0.213 - 0.213*cos_a - 0.787*sin_a, 0.715 - 0.715*cos_a + 0.715*sin_a, 0.072 + 0.928*cos_a + 0.072*sin_a]
        ])

        # Apply transformation
        result = np.dot(img_array.reshape(-1, 3), matrix.T).reshape(img_array.shape)
        result = np.clip(result * 255, 0, 255).astype(np.uint8)

        return Image.fromarray(result)

    def _get_vignette_mask(self, strength: float) -> Image.Image:
        """Get or create cached vignette mask."""
        key = round(strength, 2)
        if key not in self._vignette_cache:
            # Create radial gradient mask
            mask = Image.new('L', (self.width, self.height), 255)
            draw = ImageDraw.Draw(mask)

            center_x, center_y = self.width // 2, self.height // 2
            max_radius = math.sqrt(center_x**2 + center_y**2)

            # Draw concentric ellipses for vignette
            for i in range(int(max_radius), 0, -2):
                # Calculate alpha based on distance from center
                ratio = i / max_radius
                if ratio > 0.5:
                    alpha = int(255 * (1 - strength * ((ratio - 0.5) / 0.5) ** 1.5))
                else:
                    alpha = 255

                draw.ellipse([
                    center_x - i, center_y - i * self.height // self.width,
                    center_x + i, center_y + i * self.height // self.width
                ], fill=alpha)

            self._vignette_cache[key] = mask

        return self._vignette_cache[key]

    def _apply_vignette(self, img: Image.Image, audio_level: float) -> Image.Image:
        """Apply vignette pulsing effect."""
        if not self.config.vignette_enabled:
            return img

        # Invert: stronger audio = less vignette (more visibility)
        intensity = (1 - audio_level) * self.config.vignette_intensity
        strength = self._lerp(self.config.vignette_min, self.config.vignette_max, intensity)
        strength = self._smooth_value('vignette', strength, 0.3)

        if strength < 0.05:
            return img

        mask = self._get_vignette_mask(strength)

        # Apply vignette by darkening edges
        black = Image.new('RGB', (self.width, self.height), (0, 0, 0))
        return Image.composite(img, black, mask)

    def _apply_chromatic_aberration(self, img: Image.Image, audio_level: float) -> Image.Image:
        """Apply chromatic aberration on peaks."""
        if not self.config.chromatic_enabled:
            return img

        intensity = audio_level * self.config.chromatic_intensity
        offset = int(self._lerp(0, self.config.chromatic_max_offset, intensity))
        offset = int(self._smooth_value('chromatic', offset, 0.4))

        if offset < 1:
            return img

        # Split into RGB channels
        r, g, b = img.split()

        # Offset red and blue channels in opposite directions
        r_shifted = Image.new('L', (self.width, self.height), 0)
        b_shifted = Image.new('L', (self.width, self.height), 0)

        r_shifted.paste(r, (offset, 0))
        b_shifted.paste(b, (-offset, 0))

        return Image.merge('RGB', (r_shifted, g, b_shifted))

    def _apply_motion_blur(self, img: Image.Image, audio_level: float) -> Image.Image:
        """Apply motion blur on strong beats."""
        if not self.config.blur_enabled:
            return img

        # Only apply on high audio levels
        if audio_level < 0.6:
            return img

        intensity = (audio_level - 0.6) / 0.4 * self.config.blur_intensity
        radius = int(self._lerp(0, self.config.blur_max_radius, intensity))

        if radius < 1:
            return img

        return img.filter(ImageFilter.BoxBlur(radius))

    def _apply_warp(self, img: Image.Image, audio_level: float, frame_idx: int) -> Image.Image:
        """Apply subtle warp distortion."""
        if not self.config.warp_enabled:
            return img

        intensity = audio_level * self.config.warp_intensity
        strength = self.config.warp_strength * intensity

        if strength < 0.001:
            return img

        img_array = np.array(img)

        # Create displacement map
        y_coords, x_coords = np.mgrid[0:self.height, 0:self.width]

        # Sinusoidal warp based on position and frame
        phase = frame_idx * 0.1
        x_displacement = np.sin(y_coords * 0.02 + phase) * strength * self.width
        y_displacement = np.cos(x_coords * 0.02 + phase) * strength * self.height

        # Apply displacement
        new_x = np.clip(x_coords + x_displacement, 0, self.width - 1).astype(int)
        new_y = np.clip(y_coords + y_displacement, 0, self.height - 1).astype(int)

        result = img_array[new_y, new_x]
        return Image.fromarray(result)

    def process_frame(
        self,
        audio_level: float,
        bass_level: float,
        frame_idx: int
    ) -> Image.Image:
        """
        Process a single frame with all enabled effects.

        Args:
            audio_level: Overall audio energy (0-1)
            bass_level: Low frequency energy (0-1) - used for stronger impacts
            frame_idx: Current frame index for deterministic effects

        Returns:
            Processed image
        """
        # Start with a copy of the base image
        img = self.base_image.copy()

        # Use bass level for impact effects, overall for color effects
        impact = max(audio_level, bass_level * 1.2)  # Bass has more punch
        impact = min(impact, 1.0)

        # Apply effects in order (order matters for visual quality)
        # 1. Geometric transforms first
        img = self._apply_scale(img, impact)
        img = self._apply_shake(img, impact, frame_idx)
        img = self._apply_warp(img, impact, frame_idx)

        # 2. Color adjustments
        img = self._apply_saturation(img, audio_level)
        img = self._apply_contrast(img, audio_level)
        img = self._apply_brightness(img, impact)
        img = self._apply_hue_shift(img, audio_level)

        # 3. Post-processing effects
        img = self._apply_glow(img, impact)
        img = self._apply_chromatic_aberration(img, impact)
        img = self._apply_motion_blur(img, impact)
        img = self._apply_vignette(img, audio_level)

        return img
