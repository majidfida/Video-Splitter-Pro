# Video Splitter Pro

**Last Updated: 2025-06-03**

Video Splitter Pro is a Gradio-based tool for slicing large videos into uniform clips—ideal for preparing datasets to train AI video models (e.g., Hunyuan Video, Wan Video). Simply point to an input folder, set split parameters, and click "Process."

---

## 🆕 Updates (2025-06-03)

* **v2.1.0**:

  * Added an optional **FFmpeg Folder** input in the UI to explicitly specify the path to `ffmpeg.exe` and `ffprobe.exe`.
  * Updated segmenting logic to ensure each clip is exactly the specified duration (e.g., 1.000s), dropping any leftover milliseconds at the end.
  * Enhanced error handling when `ffmpeg` or `ffprobe` are not found; now prompts user to point to the correct FFmpeg folder.
  * Added a **Custom Caption** textbox in the UI; writes a `.txt` file next to each output clip containing the provided caption.
  * Improved mapping to drop unsupported data/timecode streams, preserving only video and optional audio.
  * Supports both copying original streams (no re-encode) and re-encoding with GPU-accelerated NVENC for H.264/H.265 when available.

---

## Features

* **Exact-length slicing:** Split into custom-length clips (default 3 s, configurable). Now guarantees each output is exactly N.000 s, discarding any trailing fraction.
* **Flexible encoding:** Choose resolution, frame rate (16, 18, 23.976, 24, 25, 29.97, 30, 50, 60, or custom), and orientation (portrait/landscape).
* **Multiple codecs:** H.264/H.265 (NVENC if CUDA is available), VP9, AV1; CRF or bitrate control.
* **Audio options:** Keep original audio (`-map 0:a? -c:a copy`) or drop audio; handles files with or without audio seamlessly.
* **GPU acceleration:** Toggle CUDA for NVENC encoding when available.
* **Custom captions:** When a caption is entered, a `.txt` file with the same basename is created alongside each clip.
* **Explicit FFmpeg path:** Optional "FFmpeg Folder" field to point to the exact folder containing `ffmpeg.exe` and `ffprobe.exe`.
* **Stop mid-process:** A Stop button halts splitting immediately.
* **Cross-platform:** Runs on Windows/Linux/macOS if FFmpeg is installed.

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/videosplitter-pro.git
   cd videosplitter-pro
   ```
2. **Install FFmpeg**:

   * **Windows**: Download a static build, unzip to `C:\ffmpeg\bin`, and ensure that folder is on your PATH.
   * **Linux/macOS**: Install via package manager (e.g., `apt install ffmpeg`, `brew install ffmpeg`).
3. **Run the installer script** (`install.bat` on Windows or `install.sh` on Linux/macOS) to create a Python virtual environment, install dependencies, and launch the app.
4. **Launch the application** (if not started by installer):

   ```bash
   python video_splitter.py
   ```

## Usage

1. **Input Folder:** Directory containing MP4, MOV, AVI, or MKV files.
2. **Output Folder:** Directory where generated clips will be saved.
3. **Clip Duration:** Length (in seconds) of each output clip. Clips will be exactly this duration (e.g., 1.000s).
4. **(Optional) FFmpeg Folder:** If FFmpeg is not on your system PATH or you want to specify a custom location, enter the folder path containing `ffmpeg.exe` and `ffprobe.exe` (e.g., `C:\ffmpeg\bin`). Otherwise, leave blank.
5. **Custom Caption:** (Optional) Enter any text here. A corresponding `.txt` file will be created next to each generated clip, containing this caption.
6. **Advanced Settings:**

   * **Use Original Settings:** Copies video (and audio) streams without re-encoding; preserves original codec, resolution, and bitrate, but still truncates to exact clip lengths.
   * **Frame Rate:** Choose a preset (16, 18, 23.976, 24, 25, 29.97, 30, 50, 60) or select "custom" to enter your own FPS.
   * **Resolution:** Choose a preset resolution or select "custom" and enter width × height (e.g., `720x1280`).
   * **Video Codec:** H.264, H.265, VP9, or AV1. If CUDA is available and you pick H.264/H.265, NVENC will be used automatically for faster encoding.
   * **Bitrate:** Choose a target bitrate (e.g., `5000k`, `10000k`, `20000k`, `50000k`) when re-encoding.
7. **Process Videos 🚀:** Click to start slicing. The status box will display progress or errors.
8. **Stop Button:** Click to halt any ongoing job immediately.

## Changelog

### v2.1.0 (2025-06-03)

* Introduced "FFmpeg Folder" field to explicitly set `ffmpeg.exe` and `ffprobe.exe` paths.
* Switched to per-chunk `ffmpeg -ss … -t …` calls for exact N.000 s segments, eliminating fractional leftovers.
* Added unified mapping `-map 0:v -map 0:a?` to drop unsupported data streams (timecode), preserving video and optional audio.
* Enhanced error messages when FFmpeg binaries are missing or misconfigured.
* Added "Custom Caption" support; writes `.txt` alongside each segment.

### v2.0.0 (2025-05-15)

* Initial release of Video Splitter Pro.
* Basic GUI with folder selectors, duration, FPS, resolution, codec, and bitrate options.
* GPU-accelerated NVENC support for H.264/H.265 when a CUDA-enabled GPU is detected.
* Ability to copy original streams (`-c copy`) or re-encode.
* Automatic folder creation with timestamped output directory.

## Credits

* **App author:** Eagle-42
* **Video encoding:** FFmpeg (GPL/LGPL)
* **GPU acceleration:** NVIDIA NVENC APIs
* **UI framework:** Gradio
* **Python libs:** `torch`, `ffmpeg-python`
* Inspired by open-source splitters and community examples.

## License and Third-Party

This project is licensed under the MIT License.
By using this tool, you agree to FFmpeg’s LGPL/GPL licensing.
Third-party dependencies and their licenses are listed in `requirements.txt`.
