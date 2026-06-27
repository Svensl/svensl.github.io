#!/usr/bin/env python3
"""
compress_mp4.py

Compresses MP4 files to a resolution/bitrate suitable for viewing on a
computer screen over the web. Defaults to 720p (1280x720) with H.264 video
and AAC audio, which is a widely-supported, reasonable balance of quality and
file size for desktop web playback.

Requirements:
    - ffmpeg must be installed and available on your PATH.
      (Linux: `sudo apt install ffmpeg`, macOS: `brew install ffmpeg`,
       Windows: download from https://ffmpeg.org and add to PATH.)

Notes / assumptions:
    - 720p is treated as "good enough for a computer screen." 1080p is offered
      as an option for higher fidelity; 480p for smaller files.
    - Videos already smaller than the target height are NOT upscaled (this only
      wastes space). They are re-encoded at the target quality instead.
    - CRF (Constant Rate Factor) is used rather than a fixed bitrate, so quality
      is consistent and file size adapts to content complexity.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# Map of friendly names to target heights. Width is computed to preserve aspect
# ratio (-2 keeps it divisible by 2, required by H.264).
RESOLUTIONS = {
    "480p": 480,
    "720p": 720,
    "1080p": 1080,
}

# CRF: lower = higher quality/larger file. 23 is the x264 default; 20-24 is a
# common "visually good" range for web. preset trades encode speed for size.
DEFAULT_CRF = 23
DEFAULT_PRESET = "medium"


def check_ffmpeg() -> None:
    """Exit early with a clear message if ffmpeg is not installed."""
    if shutil.which("ffmpeg") is None:
        sys.exit(
            "Error: ffmpeg not found on PATH. Install it first "
            "(e.g. 'sudo apt install ffmpeg' or 'brew install ffmpeg')."
        )


def find_mp4_files(location: Path, recursive: bool) -> list[Path]:
    """Return a list of .mp4 files at the given location.

    If location is a single file, returns just that file. If it's a directory,
    returns the .mp4 files inside it (recursively if requested).
    """
    if location.is_file():
        return [location] if location.suffix.lower() == ".mp4" else []
    pattern = "**/*.mp4" if recursive else "*.mp4"
    # case-insensitive: glob both lower and upper just in case the FS is case-sensitive
    files = set(location.glob(pattern))
    files |= set(location.glob(pattern.replace("mp4", "MP4")))
    return sorted(files)


def compress_file(
    src: Path, dst: Path, target_height: int, crf: int, preset: str
) -> bool:
    """Compress a single file with ffmpeg. Returns True on success.

    The scale filter downscales only when the source is taller than the target
    (min(ih, target) prevents upscaling), preserving aspect ratio.
    """
    scale_filter = f"scale=-2:'min(ih,{target_height})'"
    cmd = [
        "ffmpeg",
        "-y",                      # overwrite output if it exists
        "-i", str(src),
        "-vf", scale_filter,
        "-c:v", "libx264",
        "-crf", str(crf),
        "-preset", preset,
        "-c:a", "aac",
        "-b:a", "128k",            # 128 kbps AAC is transparent enough for web
        "-movflags", "+faststart", # enables progressive download/streaming
        str(dst),
    ]
    print(f"Compressing: {src.name} -> {dst.name}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  Failed: {src.name}", file=sys.stderr)
        # ffmpeg prints diagnostics to stderr; show the last lines for context.
        tail = "\n".join(result.stderr.strip().splitlines()[-5:])
        print(f"  ffmpeg said:\n{tail}", file=sys.stderr)
        return False
    return True


def human_size(num_bytes: int) -> str:
    """Format a byte count in human-readable units."""
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compress MP4 files for web viewing on a computer screen."
    )
    parser.add_argument(
        "location",
        nargs="?",
        help="Path to an MP4 file or a folder of MP4 files. "
        "If omitted, you'll be prompted.",
    )
    parser.add_argument(
        "-r", "--resolution",
        choices=RESOLUTIONS.keys(),
        default="720p",
        help="Target resolution (default: 720p).",
    )
    parser.add_argument(
        "--crf", type=int, default=DEFAULT_CRF,
        help=f"Quality, lower=better/bigger (default: {DEFAULT_CRF}).",
    )
    parser.add_argument(
        "--preset", default=DEFAULT_PRESET,
        help=f"x264 speed/size preset (default: {DEFAULT_PRESET}).",
    )
    parser.add_argument(
        "--recursive", action="store_true",
        help="Search subfolders when location is a directory.",
    )
    parser.add_argument(
        "-o", "--outdir",
        help="Output folder (default: a 'compressed' folder beside the source).",
    )
    args = parser.parse_args()

    check_ffmpeg()

    # Prompt for the location if not supplied on the command line.
    location_str = args.location or input("Enter the path to a video file or folder: ").strip()
    # Strip surrounding quotes that drag-and-drop terminals often add.
    location_str = location_str.strip("'\"")
    location = Path(location_str).expanduser()

    if not location.exists():
        sys.exit(f"Error: path does not exist: {location}")

    files = find_mp4_files(location, args.recursive)
    if not files:
        sys.exit("No .mp4 files found at that location.")

    # Decide where outputs go.
    if args.outdir:
        outdir = Path(args.outdir).expanduser()
    else:
        base = location if location.is_dir() else location.parent
        outdir = base / "compressed"
    outdir.mkdir(parents=True, exist_ok=True)

    target_height = RESOLUTIONS[args.resolution]
    print(f"Found {len(files)} file(s). Target: {args.resolution}, "
          f"CRF {args.crf}, preset {args.preset}.\n")

    succeeded = 0
    for src in files:
        dst = outdir / f"{src.stem}_{args.resolution}.mp4"
        # Skip if we'd overwrite the source itself.
        if dst.resolve() == src.resolve():
            print(f"Skipping {src.name}: output would overwrite input.")
            continue
        if compress_file(src, dst, target_height, args.crf, args.preset):
            succeeded += 1
            before, after = src.stat().st_size, dst.stat().st_size
            ratio = (1 - after / before) * 100 if before else 0
            print(f"  Done: {human_size(before)} -> {human_size(after)} "
                  f"({ratio:.0f}% smaller)\n")

    print(f"Finished: {succeeded}/{len(files)} file(s) compressed into {outdir}")


if __name__ == "__main__":
    main()
