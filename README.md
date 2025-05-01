# Video Splitter Pro

Video Splitter Pro is a Gradio-based tool for slicing large videos into uniform clips—ideal for preparing datasets to train AI video models (e.g., Hunyuan Video, Wan Video). Simply point to an input folder, set split parameters, and click “Process.” 

## Features

- **Fast slicing:** Split into custom-length clips (default 3 s).
- **Flexible encoding:** Choose resolution, frame rate (16, 18, 24, 30, 60, or custom), and vertical orientation.
- **Multiple codecs:** H.264/H.265 (NVENC), VP9, AV1; CRF or bitrate control.
- **Audio options:** Keep original audio or transcode (copy, AAC, Opus).
- **GPU acceleration:** Toggle CUDA for NVENC encoding.
- **Stop mid-process:** A Stop button halts splitting immediately.
- **Cross-platform:** Runs on Windows/Linux/macOS if FFmpeg is installed.

## Installation

1. Clone this repo.
2. Place your FFmpeg binaries in `C:\ffmpeg\bin` (Windows) or ensure `ffmpeg` is on your `PATH`.
3. Run `start.bat` to create a Python venv, install requirements, and launch the app.
4. In the browser UI, fill in paths and settings, then hit **Process Videos 🚀**.

## Usage

1. **Input Folder:** Directory containing MP4, MOV, AVI or MKV files.
2. **Output Folder:** Where generated clips will be saved.
3. **Clip Duration:** Length (in seconds) of each output clip.
4. *(Advanced)* **FPS / Resolution / Codec / Audio:** Fine-tune encoding settings.
5. **Stop Button:** Click to cancel an ongoing split job.

## Credits

- **App author:** Eagle-42  
- **Video encoding:** FFmpeg (GPL/LGPL)  
- **GPU acceleration:** NVIDIA NVENC APIs  
- **UI framework:** Gradio  
- **Python libs:** `torch`, `ffmpeg-python`  
- Inspired by numerous open-source splitters and community examples.

## License and Third-Party

This project is licensed under the MIT License.  
By using this tool, you agree to FFmpeg’s LGPL/GPL licensing.  
Third-party dependencies and their licenses are listed in `requirements.txt`.
