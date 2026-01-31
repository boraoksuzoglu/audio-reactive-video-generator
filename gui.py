#!/usr/bin/env python3
"""
Audio Reactive Video Generator - Desktop GUI

A polished, creative-tool oriented desktop application for generating
audio-reactive videos with configurable visual effects.

Design: Dark industrial aesthetic with vibrant accent colors
"""

import os
import sys
import threading
import queue
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

import customtkinter as ctk
from tkinter import filedialog, messagebox
import numpy as np

from core.audio import AudioProcessor
from core.renderer import FrameRenderer
from core.video import VideoComposer
from core.effects import EffectConfig

# Configuration
FPS = 30
SUPPORTED_AUDIO = ("*.mp3", "*.wav", "*.flac", "*.ogg", "*.m4a", "*.aac", "*.aiff", "*.mp4", "*.webm")
SUPPORTED_IMAGE = ("*.png", "*.jpg", "*.jpeg", "*.webp", "*.bmp", "*.tiff", "*.gif")


class GradientFrame(ctk.CTkFrame):
    """A frame with gradient-like effect using layered frames."""

    def __init__(self, parent, colors, **kwargs):
        super().__init__(parent, **kwargs)
        self.colors = colors


class FileDropZone(ctk.CTkFrame):
    """Stylized file input zone with icon and drag-drop appearance."""

    def __init__(
        self,
        parent,
        label: str,
        icon: str,
        hint: str,
        variable: ctk.StringVar,
        filetypes: list,
        colors: Dict[str, str],
        is_save: bool = False,
        **kwargs
    ):
        super().__init__(
            parent,
            fg_color=colors['bg_card'],
            corner_radius=16,
            border_width=2,
            border_color=colors['border'],
            **kwargs
        )
        self.colors = colors
        self.variable = variable
        self.filetypes = filetypes
        self.is_save = is_save

        # Hover effect binding
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

        # Inner content
        inner = ctk.CTkFrame(self, fg_color='transparent')
        inner.pack(fill='both', expand=True, padx=20, pady=16)

        # Top row: icon + label
        top_row = ctk.CTkFrame(inner, fg_color='transparent')
        top_row.pack(fill='x')

        # Icon circle
        icon_frame = ctk.CTkFrame(
            top_row,
            width=40,
            height=40,
            fg_color=colors['accent_dim'],
            corner_radius=20
        )
        icon_frame.pack(side='left')
        icon_frame.pack_propagate(False)

        icon_label = ctk.CTkLabel(
            icon_frame,
            text=icon,
            font=ctk.CTkFont(size=18),
            text_color=colors['accent']
        )
        icon_label.place(relx=0.5, rely=0.5, anchor='center')

        # Label and hint
        text_frame = ctk.CTkFrame(top_row, fg_color='transparent')
        text_frame.pack(side='left', fill='x', expand=True, padx=(12, 0))

        title = ctk.CTkLabel(
            text_frame,
            text=label,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=colors['text'],
            anchor='w'
        )
        title.pack(anchor='w')

        subtitle = ctk.CTkLabel(
            text_frame,
            text=hint,
            font=ctk.CTkFont(size=11),
            text_color=colors['text_dim'],
            anchor='w'
        )
        subtitle.pack(anchor='w')

        # Browse button
        self.browse_btn = ctk.CTkButton(
            top_row,
            text="Browse",
            width=80,
            height=36,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=colors['bg_input'],
            hover_color=colors['border'],
            text_color=colors['text'],
            corner_radius=8,
            command=self._browse
        )
        self.browse_btn.pack(side='right')

        # File path display
        self.path_frame = ctk.CTkFrame(
            inner,
            fg_color=colors['bg_input'],
            corner_radius=8,
            height=38
        )
        self.path_frame.pack(fill='x', pady=(12, 0))
        self.path_frame.pack_propagate(False)

        self.path_label = ctk.CTkLabel(
            self.path_frame,
            textvariable=variable,
            font=ctk.CTkFont(family="SF Mono", size=11),
            text_color=colors['text_mono'],
            anchor='w'
        )
        self.path_label.pack(side='left', fill='x', expand=True, padx=12)

        # Clear button (shown when file is selected)
        self.clear_btn = ctk.CTkButton(
            self.path_frame,
            text="×",
            width=28,
            height=28,
            font=ctk.CTkFont(size=16),
            fg_color='transparent',
            hover_color=colors['error'],
            text_color=colors['text_dim'],
            corner_radius=4,
            command=self._clear
        )
        self.clear_btn.pack(side='right', padx=4)

        # Update placeholder
        self._update_display()
        variable.trace_add('write', lambda *_: self._update_display())

    def _on_enter(self, event):
        self.configure(border_color=self.colors['accent'])

    def _on_leave(self, event):
        self.configure(border_color=self.colors['border'])

    def _browse(self):
        if self.is_save:
            path = filedialog.asksaveasfilename(
                defaultextension=".mp4",
                filetypes=self.filetypes,
                initialfile=os.path.basename(self.variable.get()) or "output.mp4"
            )
        else:
            path = filedialog.askopenfilename(filetypes=self.filetypes)
        if path:
            self.variable.set(path)

    def _clear(self):
        self.variable.set("")

    def _update_display(self):
        path = self.variable.get()
        if path:
            # Show filename only
            filename = os.path.basename(path)
            self.path_label.configure(text_color=self.colors['text'])
        else:
            self.path_label.configure(text_color=self.colors['text_mono'])


class PresetCard(ctk.CTkFrame):
    """A clickable preset card with name and description."""

    def __init__(
        self,
        parent,
        preset_key: str,
        preset_name: str,
        description: str,
        colors: Dict[str, str],
        is_selected: bool = False,
        on_click=None,
        **kwargs
    ):
        super().__init__(
            parent,
            fg_color=colors['accent'] if is_selected else colors['bg_card'],
            corner_radius=12,
            border_width=2,
            border_color=colors['accent'] if is_selected else colors['border'],
            cursor="hand2",
            **kwargs
        )
        self.colors = colors
        self.preset_key = preset_key
        self.is_selected = is_selected
        self.on_click = on_click

        self.bind("<Button-1>", self._clicked)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

        inner = ctk.CTkFrame(self, fg_color='transparent')
        inner.pack(fill='both', expand=True, padx=12, pady=10)
        inner.bind("<Button-1>", self._clicked)

        self.name_label = ctk.CTkLabel(
            inner,
            text=preset_name,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=colors['bg_dark'] if is_selected else colors['text'],
            anchor='w'
        )
        self.name_label.pack(anchor='w')
        self.name_label.bind("<Button-1>", self._clicked)

        self.desc_label = ctk.CTkLabel(
            inner,
            text=description,
            font=ctk.CTkFont(size=10),
            text_color=colors['bg_card'] if is_selected else colors['text_dim'],
            anchor='w'
        )
        self.desc_label.pack(anchor='w')
        self.desc_label.bind("<Button-1>", self._clicked)

    def _clicked(self, event=None):
        if self.on_click:
            self.on_click(self.preset_key)

    def _on_enter(self, event):
        if not self.is_selected:
            self.configure(border_color=self.colors['accent'])

    def _on_leave(self, event):
        if not self.is_selected:
            self.configure(border_color=self.colors['border'])

    def set_selected(self, selected: bool):
        self.is_selected = selected
        if selected:
            self.configure(
                fg_color=self.colors['accent'],
                border_color=self.colors['accent']
            )
            self.name_label.configure(text_color=self.colors['bg_dark'])
            self.desc_label.configure(text_color=self.colors['bg_card'])
        else:
            self.configure(
                fg_color=self.colors['bg_card'],
                border_color=self.colors['border']
            )
            self.name_label.configure(text_color=self.colors['text'])
            self.desc_label.configure(text_color=self.colors['text_dim'])


class EffectControl(ctk.CTkFrame):
    """Compact effect toggle with intensity slider."""

    def __init__(
        self,
        parent,
        label: str,
        enabled_var: ctk.BooleanVar,
        intensity_var: ctk.DoubleVar,
        colors: Dict[str, str],
        **kwargs
    ):
        super().__init__(parent, fg_color='transparent', **kwargs)
        self.colors = colors

        # Main row
        row = ctk.CTkFrame(self, fg_color='transparent')
        row.pack(fill='x')

        # Toggle
        self.switch = ctk.CTkSwitch(
            row,
            text="",
            variable=enabled_var,
            width=36,
            height=18,
            switch_width=32,
            switch_height=16,
            fg_color=colors['bg_input'],
            progress_color=colors['accent'],
            button_color=colors['text_dim'],
            button_hover_color=colors['text']
        )
        self.switch.pack(side='left')

        # Label
        self.label = ctk.CTkLabel(
            row,
            text=label,
            font=ctk.CTkFont(size=12),
            text_color=colors['text'],
            anchor='w'
        )
        self.label.pack(side='left', padx=(8, 0))

        # Value
        self.value_label = ctk.CTkLabel(
            row,
            text=f"{int(intensity_var.get() * 100)}%",
            font=ctk.CTkFont(family="SF Mono", size=10),
            text_color=colors['accent'],
            width=35,
            anchor='e'
        )
        self.value_label.pack(side='right')

        # Slider
        self.slider = ctk.CTkSlider(
            self,
            from_=0,
            to=1,
            variable=intensity_var,
            height=12,
            fg_color=colors['bg_input'],
            progress_color=colors['accent'],
            button_color=colors['accent'],
            button_hover_color=colors['accent_hover'],
            button_length=12,
            command=self._on_change
        )
        self.slider.pack(fill='x', pady=(6, 0))

        self.intensity_var = intensity_var

    def _on_change(self, value):
        self.value_label.configure(text=f"{int(value * 100)}%")


class AudioReactiveApp(ctk.CTk):
    """Main application window with distinctive design."""

    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("AUDIO REACTIVE")
        self.geometry("720x980")
        self.minsize(680, 900)
        self.resizable(True, True)

        # Color scheme - Midnight with Electric Cyan
        self.colors = {
            'bg_dark': '#050508',
            'bg_card': '#0d0d12',
            'bg_input': '#16161d',
            'border': '#252530',
            'border_hover': '#353545',
            'text': '#f0f0f5',
            'text_dim': '#6a6a7a',
            'text_mono': '#8888a0',
            'accent': '#00f0ff',
            'accent_hover': '#00c8d8',
            'accent_dim': '#0a2a2f',
            'success': '#00ff9d',
            'error': '#ff3860',
            'warning': '#ffb020',
            'purple': '#a855f7',
            'pink': '#ec4899',
        }

        # Apply dark theme
        ctk.set_appearance_mode("dark")
        self.configure(fg_color=self.colors['bg_dark'])

        # State
        self.audio_path = ctk.StringVar()
        self.image_path = ctk.StringVar()
        self.output_path = ctk.StringVar(value="output/output.mp4")
        self.is_rendering = False
        self.progress_queue = queue.Queue()
        self.current_preset = 'energetic'

        # Effect variables
        self._init_effect_variables()

        # Build UI
        self._create_ui()

        # Progress monitor
        self._check_progress()

    def _init_effect_variables(self):
        """Initialize all effect control variables."""
        self.effects = {
            'scale': {'enabled': ctk.BooleanVar(value=True), 'intensity': ctk.DoubleVar(value=0.5)},
            'shake': {'enabled': ctk.BooleanVar(value=True), 'intensity': ctk.DoubleVar(value=0.4)},
            'glow': {'enabled': ctk.BooleanVar(value=True), 'intensity': ctk.DoubleVar(value=0.5)},
            'saturation': {'enabled': ctk.BooleanVar(value=True), 'intensity': ctk.DoubleVar(value=0.5)},
            'contrast': {'enabled': ctk.BooleanVar(value=True), 'intensity': ctk.DoubleVar(value=0.4)},
            'brightness': {'enabled': ctk.BooleanVar(value=True), 'intensity': ctk.DoubleVar(value=0.3)},
            'hue': {'enabled': ctk.BooleanVar(value=False), 'intensity': ctk.DoubleVar(value=0.3)},
            'vignette': {'enabled': ctk.BooleanVar(value=True), 'intensity': ctk.DoubleVar(value=0.5)},
            'chromatic': {'enabled': ctk.BooleanVar(value=True), 'intensity': ctk.DoubleVar(value=0.4)},
            'blur': {'enabled': ctk.BooleanVar(value=False), 'intensity': ctk.DoubleVar(value=0.3)},
            'warp': {'enabled': ctk.BooleanVar(value=False), 'intensity': ctk.DoubleVar(value=0.3)},
        }

    def _create_ui(self):
        """Build the complete interface."""
        # Scrollable main container with hidden scrollbar
        self.main = ctk.CTkScrollableFrame(
            self,
            fg_color='transparent',
            scrollbar_fg_color='transparent',
            scrollbar_button_color=self.colors['bg_card'],
            scrollbar_button_hover_color=self.colors['border']
        )
        self.main.pack(fill='both', expand=True, padx=28, pady=24)

        # Make scrollbar thinner and more subtle
        self.main._scrollbar.configure(width=8)

        self._create_header()
        self._create_file_section()
        self._create_presets_section()
        self._create_effects_section()
        self._create_action_section()

    def _create_header(self):
        """Create distinctive header."""
        header = ctk.CTkFrame(self.main, fg_color='transparent')
        header.pack(fill='x', pady=(0, 28))

        # Left side: Logo + Title
        left = ctk.CTkFrame(header, fg_color='transparent')
        left.pack(side='left')

        # Animated bars logo
        logo = ctk.CTkFrame(left, fg_color='transparent')
        logo.pack(side='left')

        bars = [8, 14, 24, 18, 30, 22, 14, 10, 18, 26, 12, 8]
        bar_colors = [self.colors['accent'], self.colors['purple'], self.colors['accent'],
                     self.colors['pink'], self.colors['accent'], self.colors['purple'],
                     self.colors['accent'], self.colors['pink'], self.colors['accent'],
                     self.colors['purple'], self.colors['accent'], self.colors['pink']]

        for i, (h, c) in enumerate(zip(bars, bar_colors)):
            bar = ctk.CTkFrame(
                logo,
                width=4,
                height=h,
                fg_color=c,
                corner_radius=2
            )
            bar.pack(side='left', padx=1, anchor='s')

        # Title stack
        titles = ctk.CTkFrame(left, fg_color='transparent')
        titles.pack(side='left', padx=(16, 0))

        main_title = ctk.CTkLabel(
            titles,
            text="AUDIO REACTIVE",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=self.colors['text']
        )
        main_title.pack(anchor='w')

        sub_title = ctk.CTkLabel(
            titles,
            text="VIDEO GENERATOR",
            font=ctk.CTkFont(family="SF Mono", size=11),
            text_color=self.colors['accent']
        )
        sub_title.pack(anchor='w')

        # Right side: Version badge
        version = ctk.CTkLabel(
            header,
            text="v2.0",
            font=ctk.CTkFont(family="SF Mono", size=10, weight="bold"),
            text_color=self.colors['text_dim'],
            fg_color=self.colors['bg_card'],
            corner_radius=6,
            padx=10,
            pady=4
        )
        version.pack(side='right')

    def _create_file_section(self):
        """Create file inputs section."""
        # Section label
        section_label = ctk.CTkLabel(
            self.main,
            text="INPUT / OUTPUT",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.colors['text_dim']
        )
        section_label.pack(anchor='w', pady=(0, 12))

        # Audio input
        self.audio_zone = FileDropZone(
            self.main,
            label="Audio File",
            icon="♪",
            hint="MP3, WAV, FLAC, M4A, OGG, AAC, AIFF",
            variable=self.audio_path,
            filetypes=[("Audio Files", " ".join(SUPPORTED_AUDIO))],
            colors=self.colors
        )
        self.audio_zone.pack(fill='x', pady=(0, 10))

        # Image input
        self.image_zone = FileDropZone(
            self.main,
            label="Background Image",
            icon="◐",
            hint="PNG, JPG, WebP, BMP, TIFF, GIF",
            variable=self.image_path,
            filetypes=[("Image Files", " ".join(SUPPORTED_IMAGE))],
            colors=self.colors
        )
        self.image_zone.pack(fill='x', pady=(0, 10))

        # Output
        self.output_zone = FileDropZone(
            self.main,
            label="Output Video",
            icon="▶",
            hint="MP4 (H.264 + AAC)",
            variable=self.output_path,
            filetypes=[("Video Files", "*.mp4")],
            colors=self.colors,
            is_save=True
        )
        self.output_zone.pack(fill='x', pady=(0, 24))

    def _create_presets_section(self):
        """Create presets selection grid."""
        # Section label
        section_label = ctk.CTkLabel(
            self.main,
            text="STYLE PRESETS",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.colors['text_dim']
        )
        section_label.pack(anchor='w', pady=(0, 12))

        # Presets container
        presets_frame = ctk.CTkFrame(self.main, fg_color='transparent')
        presets_frame.pack(fill='x', pady=(0, 24))

        # Grid of presets (2 rows x 5 columns)
        presets = [
            ('subtle', 'Subtle', 'Gentle & understated'),
            ('energetic', 'Energetic', 'Balanced & dynamic'),
            ('aggressive', 'Aggressive', 'Bold & intense'),
            ('cinematic', 'Cinematic', 'Film-like atmosphere'),
            ('dreamy', 'Dreamy', 'Soft & ethereal'),
            ('retro', 'Retro', 'VHS / Synthwave'),
            ('minimal', 'Minimal', 'Clean & subtle'),
            ('psychedelic', 'Psychedelic', 'Trippy & wild'),
            ('bass', 'Bass', 'Punchy low-end'),
            ('noir', 'Noir', 'Dark & moody'),
        ]

        self.preset_cards = {}
        row_frame = None

        for i, (key, name, desc) in enumerate(presets):
            if i % 5 == 0:
                row_frame = ctk.CTkFrame(presets_frame, fg_color='transparent')
                row_frame.pack(fill='x', pady=(0, 8))

            card = PresetCard(
                row_frame,
                preset_key=key,
                preset_name=name,
                description=desc,
                colors=self.colors,
                is_selected=(key == self.current_preset),
                on_click=self._select_preset
            )
            card.pack(side='left', fill='x', expand=True, padx=(0 if i % 5 == 0 else 6, 0))
            self.preset_cards[key] = card

    def _create_effects_section(self):
        """Create effects controls panel."""
        # Section header with toggle
        header = ctk.CTkFrame(self.main, fg_color='transparent')
        header.pack(fill='x', pady=(0, 12))

        section_label = ctk.CTkLabel(
            header,
            text="EFFECT CONTROLS",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.colors['text_dim']
        )
        section_label.pack(side='left')

        # Collapsible hint
        hint = ctk.CTkLabel(
            header,
            text="Fine-tune individual effects",
            font=ctk.CTkFont(size=10),
            text_color=self.colors['text_mono']
        )
        hint.pack(side='right')

        # Effects card
        effects_card = ctk.CTkFrame(
            self.main,
            fg_color=self.colors['bg_card'],
            corner_radius=16,
            border_width=1,
            border_color=self.colors['border']
        )
        effects_card.pack(fill='x', pady=(0, 24))

        effects_inner = ctk.CTkFrame(effects_card, fg_color='transparent')
        effects_inner.pack(fill='x', padx=20, pady=18)

        # 3-column grid
        cols_frame = ctk.CTkFrame(effects_inner, fg_color='transparent')
        cols_frame.pack(fill='x')

        col1 = ctk.CTkFrame(cols_frame, fg_color='transparent')
        col1.pack(side='left', fill='both', expand=True)

        col2 = ctk.CTkFrame(cols_frame, fg_color='transparent')
        col2.pack(side='left', fill='both', expand=True, padx=20)

        col3 = ctk.CTkFrame(cols_frame, fg_color='transparent')
        col3.pack(side='left', fill='both', expand=True)

        # Define effects per column
        col1_effects = [
            ('scale', 'Pulse Zoom'),
            ('shake', 'Camera Shake'),
            ('glow', 'Bloom'),
            ('blur', 'Motion Blur'),
        ]

        col2_effects = [
            ('saturation', 'Saturation'),
            ('contrast', 'Contrast'),
            ('brightness', 'Brightness'),
            ('hue', 'Hue Shift'),
        ]

        col3_effects = [
            ('vignette', 'Vignette'),
            ('chromatic', 'Color Split'),
            ('warp', 'Distortion'),
        ]

        self.effect_widgets = {}

        for key, name in col1_effects:
            ctrl = EffectControl(col1, name, self.effects[key]['enabled'],
                                self.effects[key]['intensity'], self.colors)
            ctrl.pack(fill='x', pady=(0, 12))
            self.effect_widgets[key] = ctrl

        for key, name in col2_effects:
            ctrl = EffectControl(col2, name, self.effects[key]['enabled'],
                                self.effects[key]['intensity'], self.colors)
            ctrl.pack(fill='x', pady=(0, 12))
            self.effect_widgets[key] = ctrl

        for key, name in col3_effects:
            ctrl = EffectControl(col3, name, self.effects[key]['enabled'],
                                self.effects[key]['intensity'], self.colors)
            ctrl.pack(fill='x', pady=(0, 12))
            self.effect_widgets[key] = ctrl

    def _create_action_section(self):
        """Create generate button and progress."""
        # Generate button with gradient-like effect
        self.generate_btn = ctk.CTkButton(
            self.main,
            text="✦  GENERATE VIDEO",
            font=ctk.CTkFont(size=17, weight="bold"),
            height=58,
            corner_radius=14,
            fg_color=self.colors['accent'],
            hover_color=self.colors['accent_hover'],
            text_color=self.colors['bg_dark'],
            command=self._start_generation
        )
        self.generate_btn.pack(fill='x', pady=(0, 16))

        # Progress section
        progress_card = ctk.CTkFrame(
            self.main,
            fg_color=self.colors['bg_card'],
            corner_radius=14,
            border_width=1,
            border_color=self.colors['border']
        )
        progress_card.pack(fill='x')

        progress_inner = ctk.CTkFrame(progress_card, fg_color='transparent')
        progress_inner.pack(fill='x', padx=18, pady=16)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            progress_inner,
            height=8,
            corner_radius=4,
            fg_color=self.colors['bg_input'],
            progress_color=self.colors['accent']
        )
        self.progress_bar.pack(fill='x', pady=(0, 12))
        self.progress_bar.set(0)

        # Status row
        status_row = ctk.CTkFrame(progress_inner, fg_color='transparent')
        status_row.pack(fill='x')

        self.status_label = ctk.CTkLabel(
            status_row,
            text="Ready to generate",
            font=ctk.CTkFont(family="SF Mono", size=12),
            text_color=self.colors['text_dim'],
            anchor='w'
        )
        self.status_label.pack(side='left')

        # Open button (hidden initially)
        self.open_btn = ctk.CTkButton(
            status_row,
            text="Open ↗",
            width=80,
            height=30,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors['success'],
            hover_color='#00d884',
            text_color=self.colors['bg_dark'],
            corner_radius=6,
            command=self._open_output
        )

    def _select_preset(self, preset_key: str):
        """Handle preset selection."""
        self.current_preset = preset_key

        # Update card visuals
        for key, card in self.preset_cards.items():
            card.set_selected(key == preset_key)

        # Apply preset values
        config = EffectConfig.from_preset(preset_key)

        # Update all effect variables
        effect_map = {
            'scale': ('scale_enabled', 'scale_intensity'),
            'shake': ('shake_enabled', 'shake_intensity'),
            'glow': ('glow_enabled', 'glow_intensity'),
            'saturation': ('saturation_enabled', 'saturation_intensity'),
            'contrast': ('contrast_enabled', 'contrast_intensity'),
            'brightness': ('brightness_enabled', 'brightness_intensity'),
            'hue': ('hue_enabled', 'hue_intensity'),
            'vignette': ('vignette_enabled', 'vignette_intensity'),
            'chromatic': ('chromatic_enabled', 'chromatic_intensity'),
            'blur': ('blur_enabled', 'blur_intensity'),
            'warp': ('warp_enabled', 'warp_intensity'),
        }

        for key, (en_attr, int_attr) in effect_map.items():
            self.effects[key]['enabled'].set(getattr(config, en_attr))
            self.effects[key]['intensity'].set(getattr(config, int_attr))

        # Update slider labels
        for key, widget in self.effect_widgets.items():
            value = self.effects[key]['intensity'].get()
            widget.value_label.configure(text=f"{int(value * 100)}%")

    def _build_effect_config(self) -> EffectConfig:
        """Build EffectConfig from current UI state."""
        return EffectConfig(
            scale_enabled=self.effects['scale']['enabled'].get(),
            scale_intensity=self.effects['scale']['intensity'].get(),
            shake_enabled=self.effects['shake']['enabled'].get(),
            shake_intensity=self.effects['shake']['intensity'].get(),
            glow_enabled=self.effects['glow']['enabled'].get(),
            glow_intensity=self.effects['glow']['intensity'].get(),
            saturation_enabled=self.effects['saturation']['enabled'].get(),
            saturation_intensity=self.effects['saturation']['intensity'].get(),
            contrast_enabled=self.effects['contrast']['enabled'].get(),
            contrast_intensity=self.effects['contrast']['intensity'].get(),
            brightness_enabled=self.effects['brightness']['enabled'].get(),
            brightness_intensity=self.effects['brightness']['intensity'].get(),
            hue_enabled=self.effects['hue']['enabled'].get(),
            hue_intensity=self.effects['hue']['intensity'].get(),
            vignette_enabled=self.effects['vignette']['enabled'].get(),
            vignette_intensity=self.effects['vignette']['intensity'].get(),
            chromatic_enabled=self.effects['chromatic']['enabled'].get(),
            chromatic_intensity=self.effects['chromatic']['intensity'].get(),
            blur_enabled=self.effects['blur']['enabled'].get(),
            blur_intensity=self.effects['blur']['intensity'].get(),
            warp_enabled=self.effects['warp']['enabled'].get(),
            warp_intensity=self.effects['warp']['intensity'].get(),
        )

    def _validate_inputs(self) -> bool:
        """Validate inputs before generation."""
        errors = []

        audio = self.audio_path.get()
        if not audio:
            errors.append("Select an audio file")
        elif not os.path.exists(audio):
            errors.append("Audio file not found")

        image = self.image_path.get()
        if not image:
            errors.append("Select a background image")
        elif not os.path.exists(image):
            errors.append("Image file not found")

        output = self.output_path.get()
        if not output:
            errors.append("Specify an output path")

        if errors:
            messagebox.showerror("Missing Input", "\n".join(errors))
            return False
        return True

    def _start_generation(self):
        """Start video generation."""
        if self.is_rendering:
            return

        if not self._validate_inputs():
            return

        self.is_rendering = True
        self.generate_btn.configure(state='disabled', text="⟳  GENERATING...")
        self.open_btn.pack_forget()
        self.progress_bar.set(0)
        self.status_label.configure(text="Starting...", text_color=self.colors['text'])

        # Ensure output directory
        output_dir = os.path.dirname(self.output_path.get())
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Start render thread
        thread = threading.Thread(target=self._render_thread, daemon=True)
        thread.start()

    def _render_thread(self):
        """Background rendering thread."""
        try:
            audio_path = self.audio_path.get()
            image_path = self.image_path.get()
            output_path = self.output_path.get()
            effect_config = self._build_effect_config()

            # Load audio
            self.progress_queue.put(("status", "Loading audio..."))
            self.progress_queue.put(("progress", 0.05))

            audio = AudioProcessor(audio_path, fps=FPS)
            audio.load()
            features = audio.extract_features()

            self.progress_queue.put(("status", f"Analyzing {audio.duration:.1f}s audio..."))
            self.progress_queue.put(("progress", 0.1))

            # Init renderer
            self.progress_queue.put(("status", "Preparing effects..."))
            self.progress_queue.put(("progress", 0.15))

            renderer = FrameRenderer(
                background_path=image_path,
                effect_config=effect_config
            )

            # Render frames
            total_frames = features.frame_count
            frames = []

            for i in range(total_frames):
                frame = renderer.render_frame(
                    audio_level=features.overall_energy[i],
                    bass_level=features.bass_energy[i],
                    frame_idx=i
                )
                frames.append(np.array(frame))

                if i % 5 == 0:
                    progress = 0.15 + (0.65 * (i / total_frames))
                    self.progress_queue.put(("progress", progress))
                    self.progress_queue.put(("status", f"Rendering frame {i+1}/{total_frames}"))

            # Compose video
            self.progress_queue.put(("status", "Encoding video..."))
            self.progress_queue.put(("progress", 0.85))

            composer = VideoComposer(
                audio_path=audio_path,
                output_path=output_path,
                fps=FPS
            )
            composer.compose(frames, audio.duration)

            self.progress_queue.put(("complete", output_path))

        except Exception as e:
            self.progress_queue.put(("error", str(e)))

    def _check_progress(self):
        """Monitor progress queue."""
        try:
            while True:
                msg_type, msg_data = self.progress_queue.get_nowait()

                if msg_type == "progress":
                    self.progress_bar.set(msg_data)
                elif msg_type == "status":
                    self.status_label.configure(text=msg_data)
                elif msg_type == "complete":
                    self.is_rendering = False
                    self.progress_bar.set(1.0)
                    self.status_label.configure(text="✓ Complete!", text_color=self.colors['success'])
                    self.generate_btn.configure(state='normal', text="✦  GENERATE VIDEO")
                    self.open_btn.pack(side='right')
                elif msg_type == "error":
                    self.is_rendering = False
                    self.progress_bar.set(0)
                    self.status_label.configure(text=f"Error: {msg_data[:40]}...", text_color=self.colors['error'])
                    self.generate_btn.configure(state='normal', text="✦  GENERATE VIDEO")
                    messagebox.showerror("Error", msg_data)

        except queue.Empty:
            pass

        self.after(50, self._check_progress)

    def _open_output(self):
        """Open output video."""
        output = self.output_path.get()
        if os.path.exists(output):
            if sys.platform == 'darwin':
                os.system(f'open "{output}"')
            elif sys.platform == 'win32':
                os.startfile(output)
            else:
                os.system(f'xdg-open "{output}"')


def main():
    app = AudioReactiveApp()
    app.mainloop()


if __name__ == '__main__':
    main()
