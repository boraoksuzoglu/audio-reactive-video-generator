#!/usr/bin/env python3
"""
Build script for Audio Reactive Video Generator.
Creates standalone executables for macOS and Windows.
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path


APP_NAME = "Audio Reactive"
VERSION = "2.0.0"
ICON_PATH = "assets/icon.png"
MAIN_SCRIPT = "gui.py"


def get_platform():
    """Get current platform."""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "windows":
        return "windows"
    elif system == "linux":
        return "linux"
    return system


def clean_build():
    """Clean previous build artifacts."""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for d in dirs_to_clean:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"Cleaned {d}/")

    # Clean .spec files
    for f in Path(".").glob("*.spec"):
        f.unlink()
        print(f"Cleaned {f}")


def convert_icon_macos(png_path: str) -> str:
    """Convert PNG to ICNS for macOS."""
    icns_path = png_path.replace(".png", ".icns")

    if os.path.exists(icns_path):
        return icns_path

    # Create iconset directory
    iconset_dir = "assets/icon.iconset"
    os.makedirs(iconset_dir, exist_ok=True)

    # Generate different sizes using sips
    sizes = [16, 32, 64, 128, 256, 512]
    for size in sizes:
        # Standard resolution
        output = f"{iconset_dir}/icon_{size}x{size}.png"
        subprocess.run([
            "sips", "-z", str(size), str(size), png_path,
            "--out", output
        ], capture_output=True)

        # Retina resolution
        retina_size = size * 2
        if retina_size <= 1024:
            output_2x = f"{iconset_dir}/icon_{size}x{size}@2x.png"
            subprocess.run([
                "sips", "-z", str(retina_size), str(retina_size), png_path,
                "--out", output_2x
            ], capture_output=True)

    # Convert iconset to icns
    subprocess.run([
        "iconutil", "-c", "icns", iconset_dir,
        "-o", icns_path
    ], capture_output=True)

    # Cleanup iconset
    shutil.rmtree(iconset_dir)

    print(f"Created {icns_path}")
    return icns_path


def convert_icon_windows(png_path: str) -> str:
    """Convert PNG to ICO for Windows."""
    ico_path = png_path.replace(".png", ".ico")

    if os.path.exists(ico_path):
        return ico_path

    try:
        from PIL import Image
        img = Image.open(png_path)

        # Create ICO with multiple sizes
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        img.save(ico_path, format='ICO', sizes=sizes)
        print(f"Created {ico_path}")
        return ico_path
    except Exception as e:
        print(f"Warning: Could not create .ico file: {e}")
        return png_path


def build_macos():
    """Build macOS application bundle."""
    print("\n" + "="*50)
    print("Building for macOS...")
    print("="*50 + "\n")

    # Convert icon
    icon_path = convert_icon_macos(ICON_PATH)

    # PyInstaller command for macOS
    cmd = [
        "pyinstaller",
        "--name", APP_NAME,
        "--windowed",  # No console window
        "--onedir",    # Create a directory bundle
        "--icon", icon_path,
        "--add-data", "core:core",
        "--add-data", "assets:assets",
        "--hidden-import", "PIL._tkinter_finder",
        "--hidden-import", "sklearn.utils._typedefs",
        "--hidden-import", "sklearn.neighbors._partition_nodes",
        "--collect-all", "customtkinter",
        "--collect-all", "librosa",
        "--collect-all", "imageio",
        "--collect-all", "moviepy",
        "--collect-all", "imageio_ffmpeg",
        "--noconfirm",
        "--clean",
        MAIN_SCRIPT
    ]

    subprocess.run(cmd, check=True)

    # Create DMG with Applications folder symlink
    app_path = f"dist/{APP_NAME}.app"
    if os.path.exists(app_path):
        print(f"\n✓ macOS app created: {app_path}")

        # Create DMG with proper layout
        try:
            staging_dir = "dist/dmg-staging"
            dmg_path = f"dist/{APP_NAME}-{VERSION}-macOS.dmg"

            # Create staging directory
            os.makedirs(staging_dir, exist_ok=True)

            # Copy app to staging
            import shutil
            staging_app = f"{staging_dir}/{APP_NAME}.app"
            if os.path.exists(staging_app):
                shutil.rmtree(staging_app)
            shutil.copytree(app_path, staging_app)

            # Create Applications symlink
            subprocess.run([
                "ln", "-s", "/Applications",
                f"{staging_dir}/Applications"
            ], check=True)

            # Create DMG from staging
            subprocess.run([
                "hdiutil", "create", "-volname", APP_NAME,
                "-srcfolder", staging_dir,
                "-ov", "-format", "UDZO",
                dmg_path
            ], check=True)

            # Cleanup
            shutil.rmtree(staging_dir)

            print(f"✓ DMG created: {dmg_path}")
        except Exception as e:
            print(f"Note: DMG creation skipped ({e})")


def build_windows():
    """Build Windows executable."""
    print("\n" + "="*50)
    print("Building for Windows...")
    print("="*50 + "\n")

    # Convert icon
    icon_path = convert_icon_windows(ICON_PATH)

    # PyInstaller command for Windows
    cmd = [
        "pyinstaller",
        "--name", APP_NAME,
        "--windowed",  # No console window
        "--onefile",   # Single executable
        "--icon", icon_path,
        "--add-data", "core;core",
        "--add-data", "assets;assets",
        "--hidden-import", "PIL._tkinter_finder",
        "--hidden-import", "sklearn.utils._typedefs",
        "--hidden-import", "sklearn.neighbors._partition_nodes",
        "--collect-all", "customtkinter",
        "--collect-all", "librosa",
        "--collect-all", "imageio",
        "--collect-all", "moviepy",
        "--collect-all", "imageio_ffmpeg",
        "--noconfirm",
        "--clean",
        MAIN_SCRIPT
    ]

    subprocess.run(cmd, check=True)

    exe_path = f"dist/{APP_NAME}.exe"
    if os.path.exists(exe_path):
        print(f"\n✓ Windows executable created: {exe_path}")


def build_linux():
    """Build Linux executable."""
    print("\n" + "="*50)
    print("Building for Linux...")
    print("="*50 + "\n")

    cmd = [
        "pyinstaller",
        "--name", APP_NAME.lower().replace(" ", "-"),
        "--windowed",
        "--onefile",
        "--add-data", "core:core",
        "--add-data", "assets:assets",
        "--hidden-import", "PIL._tkinter_finder",
        "--hidden-import", "sklearn.utils._typedefs",
        "--hidden-import", "sklearn.neighbors._partition_nodes",
        "--collect-all", "customtkinter",
        "--collect-all", "librosa",
        "--collect-all", "imageio",
        "--collect-all", "moviepy",
        "--collect-all", "imageio_ffmpeg",
        "--noconfirm",
        "--clean",
        MAIN_SCRIPT
    ]

    subprocess.run(cmd, check=True)
    print(f"\n✓ Linux executable created in dist/")


def main():
    """Main build entry point."""
    print(f"""
╔══════════════════════════════════════════════════╗
║     Audio Reactive Video Generator - Builder     ║
║                    v{VERSION}                        ║
╚══════════════════════════════════════════════════╝
    """)

    # Parse arguments
    if len(sys.argv) > 1:
        action = sys.argv[1].lower()
    else:
        action = "build"

    if action == "clean":
        clean_build()
        return

    if action in ("build", "all"):
        plat = get_platform()

        # Clean first
        clean_build()

        if plat == "macos":
            build_macos()
        elif plat == "windows":
            build_windows()
        elif plat == "linux":
            build_linux()
        else:
            print(f"Unknown platform: {plat}")
            sys.exit(1)

        print("\n" + "="*50)
        print("Build complete!")
        print("="*50)

    elif action == "macos":
        clean_build()
        build_macos()

    elif action == "windows":
        clean_build()
        build_windows()

    elif action == "linux":
        clean_build()
        build_linux()

    else:
        print(f"""
Usage: python build.py [command]

Commands:
    build    Build for current platform (default)
    macos    Build macOS .app bundle
    windows  Build Windows .exe
    linux    Build Linux executable
    clean    Remove build artifacts
        """)


if __name__ == "__main__":
    main()
