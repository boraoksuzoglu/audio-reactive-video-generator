"""
Audio processing module for extracting audio features.
Uses librosa to analyze audio files and extract energy levels
aligned to video frames.
"""

import numpy as np
import librosa
from dataclasses import dataclass
from typing import Tuple


@dataclass
class AudioFeatures:
    """Container for extracted audio features."""
    overall_energy: np.ndarray  # Overall RMS energy per frame (0-1)
    bass_energy: np.ndarray     # Low frequency energy per frame (0-1)
    mid_energy: np.ndarray      # Mid frequency energy per frame (0-1)
    high_energy: np.ndarray     # High frequency energy per frame (0-1)
    duration: float             # Audio duration in seconds
    frame_count: int            # Total number of frames


class AudioProcessor:
    """Processes audio files to extract frame-aligned audio features."""

    def __init__(self, audio_path: str, fps: int = 30):
        """
        Initialize the audio processor.

        Args:
            audio_path: Path to the audio file
            fps: Frames per second for the output video
        """
        self.audio_path = audio_path
        self.fps = fps
        self.y = None  # Audio time series
        self.sr = None  # Sample rate
        self.duration = None
        self.frame_count = None
        self._features = None

    def load(self) -> 'AudioProcessor':
        """
        Load the audio file and compute basic properties.

        Returns:
            self for method chaining
        """
        # Load audio file (librosa handles various formats)
        self.y, self.sr = librosa.load(self.audio_path, sr=None, mono=True)
        self.duration = librosa.get_duration(y=self.y, sr=self.sr)
        self.frame_count = int(np.ceil(self.duration * self.fps))
        return self

    def extract_features(self) -> AudioFeatures:
        """
        Extract all audio features for video generation.

        Returns:
            AudioFeatures object with all extracted data
        """
        if self.y is None:
            self.load()

        # Calculate hop length to align with video frames
        hop_length = int(self.sr / self.fps)

        # Compute STFT for frequency analysis
        n_fft = 2048
        stft = np.abs(librosa.stft(self.y, n_fft=n_fft, hop_length=hop_length))

        # Get frequency bins
        freqs = librosa.fft_frequencies(sr=self.sr, n_fft=n_fft)

        # Define frequency bands
        bass_mask = freqs < 250       # Bass: 0-250 Hz
        mid_mask = (freqs >= 250) & (freqs < 2000)  # Mid: 250-2000 Hz
        high_mask = freqs >= 2000     # High: 2000+ Hz

        # Extract energy per band
        bass_energy = np.sum(stft[bass_mask, :], axis=0)
        mid_energy = np.sum(stft[mid_mask, :], axis=0)
        high_energy = np.sum(stft[high_mask, :], axis=0)
        overall_energy = np.sum(stft, axis=0)

        # Normalize each band independently
        bass_energy = self._normalize_and_smooth(bass_energy)
        mid_energy = self._normalize_and_smooth(mid_energy)
        high_energy = self._normalize_and_smooth(high_energy)
        overall_energy = self._normalize_and_smooth(overall_energy)

        # Ensure correct frame count
        bass_energy = self._adjust_length(bass_energy)
        mid_energy = self._adjust_length(mid_energy)
        high_energy = self._adjust_length(high_energy)
        overall_energy = self._adjust_length(overall_energy)

        self._features = AudioFeatures(
            overall_energy=overall_energy,
            bass_energy=bass_energy,
            mid_energy=mid_energy,
            high_energy=high_energy,
            duration=self.duration,
            frame_count=self.frame_count
        )

        return self._features

    def _normalize_and_smooth(self, data: np.ndarray, window_size: int = 3) -> np.ndarray:
        """Normalize to 0-1 range and apply smoothing."""
        # Normalize
        data_min = np.min(data)
        data_max = np.max(data)
        if data_max - data_min > 1e-8:
            data = (data - data_min) / (data_max - data_min)
        else:
            data = np.zeros_like(data)

        # Apply smoothing to reduce jitter
        kernel = np.ones(window_size) / window_size
        data = np.convolve(data, kernel, mode='same')

        # Apply slight non-linear curve for more dynamic response
        data = np.power(data, 0.8)

        return data

    def _adjust_length(self, data: np.ndarray) -> np.ndarray:
        """Adjust array to match required frame count."""
        if len(data) > self.frame_count:
            return data[:self.frame_count]
        elif len(data) < self.frame_count:
            padding = np.zeros(self.frame_count - len(data))
            return np.concatenate([data, padding])
        return data

    def get_duration(self) -> float:
        """Get the audio duration in seconds."""
        if self.duration is None:
            self.load()
        return self.duration

    def get_frame_count(self) -> int:
        """Get the total number of video frames."""
        if self.frame_count is None:
            self.load()
        return self.frame_count

    def get_features(self) -> AudioFeatures:
        """Get extracted features (extract if not done yet)."""
        if self._features is None:
            return self.extract_features()
        return self._features

    # Legacy method for backward compatibility
    def extract_rms(self, bar_count: int = 32) -> np.ndarray:
        """
        Legacy method - returns overall energy repeated for bar_count columns.
        Kept for backward compatibility with CLI.
        """
        features = self.get_features()
        # Return 2D array for compatibility
        return np.column_stack([features.overall_energy] * bar_count)
