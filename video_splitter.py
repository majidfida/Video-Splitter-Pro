import os
import glob
import subprocess
import gradio as gr
from datetime import datetime
import torch

def get_gpu_info():
    if torch.cuda.is_available():
        return f"CUDA {torch.version.cuda} - {torch.cuda.get_device_name(0)}"
    return "No NVIDIA GPU detected"

def get_duration_with_ffprobe(ffprobe_bin, input_path):
    """
    Uses `ffprobe` to return the total duration (in seconds) of input_path as a float.
    Returns (duration, None) on success, or (None, error_message) on failure.
    """
    cmd = [
        ffprobe_bin,
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        input_path
    ]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except FileNotFoundError:
        return None, (
            f"Error: `ffprobe` not found at `{ffprobe_bin}`.\n"
            "Please verify the FFmpeg Folder you provided, or ensure `ffprobe` is on your PATH."
        )

    if proc.returncode != 0:
        return None, (
            f"ffprobe error for `{os.path.basename(input_path)}`:\n"
            f"{proc.stderr.strip()}"
        )

    try:
        duration = float(proc.stdout.strip())
    except ValueError:
        return None, (
            f"Could not parse duration from ffprobe output:\n{proc.stdout.strip()}"
        )

    return duration, None

def split_videos(
    input_folder,
    output_folder,
    chunk_duration,
    use_original,
    fps,
    custom_fps,
    resolution,
    custom_res,
    codec,
    bitrate,
    custom_caption,
    ffmpeg_folder
):
    # --------------------------------------------
    # 1) Determine ffmpeg & ffprobe binaries
    # --------------------------------------------
    if ffmpeg_folder and ffmpeg_folder.strip() != "":
        ffmpeg_bin = os.path.join(ffmpeg_folder, "ffmpeg.exe")
        ffprobe_bin = os.path.join(ffmpeg_folder, "ffprobe.exe")
    else:
        ffmpeg_bin = "ffmpeg"
        ffprobe_bin = "ffprobe"

    # Check existence of ffmpeg & ffprobe
    if not os.path.isfile(ffmpeg_bin) or not os.access(ffmpeg_bin, os.X_OK):
        return (
            f"Error: `ffmpeg` not found or not executable at:\n  {ffmpeg_bin}\n"
            "Please specify the correct FFmpeg Folder, or install FFmpeg and add to PATH."
        )
    if not os.path.isfile(ffprobe_bin) or not os.access(ffprobe_bin, os.X_OK):
        return (
            f"Error: `ffprobe` not found or not executable at:\n  {ffprobe_bin}\n"
            "Please specify the correct FFmpeg Folder, or install FFmpeg and add to PATH."
        )

    # --------------------------------------------
    # 2) Prepare output subfolder
    # --------------------------------------------
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_folder, f"output_{timestamp}")
    os.makedirs(output_path, exist_ok=True)

    # --------------------------------------------
    # 3) Enumerate all supported video files
    # --------------------------------------------
    video_files = [
        f
        for f in os.listdir(input_folder)
        if f.lower().endswith((".mp4", ".mov", ".avi", ".mkv"))
    ]
    if not video_files:
        return f"No video files found in `{input_folder}`."

    # --------------------------------------------
    # 4) Process each video
    # --------------------------------------------
    for video_file in video_files:
        input_path = os.path.join(input_folder, video_file)
        base_name = os.path.splitext(video_file)[0]

        # 4a) Get total duration via ffprobe
        total_duration, err = get_duration_with_ffprobe(ffprobe_bin, input_path)
        if err:
            return err  # bail out on probe error

        # 4b) Compute how many full chunks of size chunk_duration fit
        num_full_chunks = int(total_duration // float(chunk_duration))
        valid_total = num_full_chunks * float(chunk_duration)

        # Skip if too short for even one chunk
        if valid_total < float(chunk_duration):
            continue

        # 4c) For each chunk, run a separate ffmpeg invocation
        for idx in range(num_full_chunks):
            start_time = idx * float(chunk_duration)
            output_clip = os.path.join(output_path, f"{base_name}_{idx:03d}.mp4")

            if use_original:
                # Copy video/audio exactly, cutting from start_time for chunk_duration
                # "-ss" after "-i" ensures accurate frame-level cut when using -c copy
                cmd = [
                    ffmpeg_bin,
                    "-hwaccel", "cuda" if torch.cuda.is_available() else "auto",
                    "-i", input_path,
                    "-ss", str(start_time),
                    "-t", str(chunk_duration),
                    "-c", "copy",
                    "-map", "0:v",
                    "-map", "0:a?",
                    "-avoid_negative_ts", "1",
                    output_clip
                ]
            else:
                # Re-encode with user settings, cutting exactly from start_time
                fps_val = float(custom_fps) if fps == "custom" else float(fps)

                if resolution == "custom":
                    try:
                        width, height = map(int, custom_res.lower().split("x"))
                    except:
                        return f"Invalid resolution format: `{custom_res}`. Use WxH (e.g. 720x1280)."
                else:
                    width, height = map(int, resolution.split("x"))

                # Select codec: use NVENC if GPU available and codec is h264/hevc
                if torch.cuda.is_available() and codec in ["h264", "hevc"]:
                    codec_arg = f"{codec}_nvenc"
                else:
                    codec_arg = codec

                cmd = [
                    ffmpeg_bin,
                    "-hwaccel", "cuda" if torch.cuda.is_available() else "auto",
                    "-i", input_path,
                    "-ss", str(start_time),
                    "-t", str(chunk_duration),
                    "-c:v", codec_arg,
                    "-r", str(fps_val),
                    "-s", f"{width}x{height}",
                    "-b:v", bitrate,
                    "-c:a", "copy",
                    "-map", "0:v",
                    "-map", "0:a?",
                    "-avoid_negative_ts", "1",
                    output_clip
                ]

            # 4d) Run ffmpeg for this chunk
            try:
                subprocess.run(cmd, check=True, stderr=subprocess.PIPE, text=True)
            except subprocess.CalledProcessError as e:
                return (
                    f"Error processing chunk {idx:03d} of `{video_file}`:\n"
                    f"{e.stderr.strip()}"
                )

            # 4e) If user provided a caption, write a .txt next to each segment
            if custom_caption and custom_caption.strip() != "":
                txt_path = os.path.splitext(output_clip)[0] + ".txt"
                try:
                    with open(txt_path, "w", encoding="utf-8") as tf:
                        tf.write(custom_caption)
                except Exception as e:
                    print(f"Warning: could not write caption file `{txt_path}`: {e}")

    return f"✅ All done! Exactly {int(chunk_duration)}-second segments are in:\n  {output_path}"


# ------------------- Gradio UI -------------------

with gr.Blocks(title="Video Splitter Pro") as demo:
    gr.Markdown("""# 🎥 Video Splitter Pro with GPU Acceleration  
**Created by Eagle-42**""")
    gr.Markdown(f"**GPU Detected:** {get_gpu_info()}")

    with gr.Row():
        input_folder = gr.Textbox(
            label="Input Folder Path",
            placeholder=r"C:\videos\input",
        )
        output_folder = gr.Textbox(
            label="Output Folder Path",
            placeholder=r"C:\videos\output",
        )

    chunk_duration = gr.Number(
        label="Chunk Duration (seconds)",
        value=1,
    )

    # FFmpeg folder (optional)
    ffmpeg_folder = gr.Textbox(
        label="FFmpeg Folder (optional)",
        placeholder=r"C:\ffmpeg\bin",
        info=(
            "If left blank, assumes `ffmpeg` & `ffprobe` are on your PATH. "
            "Otherwise point to the folder containing ffmpeg.exe and ffprobe.exe."
        )
    )

    # Custom caption
    custom_caption = gr.Textbox(
        label="Custom Caption (optional)",
        placeholder="Enter text to save as .txt for each clip"
    )

    with gr.Accordion("Advanced Settings", open=False):
        use_original = gr.Checkbox(
            label="Use Original Video Settings (no re-encode)",
            value=True
        )

        fps = gr.Dropdown(
            ["16", "18", "23.976", "24", "25", "29.97", "30", "50", "60", "custom"],
            label="Frame Rate",
            value="30",
        )
        custom_fps = gr.Number(
            label="Custom FPS",
            visible=False,
        )

        resolution = gr.Dropdown(
            [
                "1280x720",
                "720x1280",
                "1920x1080",
                "1080x1920",
                "3840x2160",
                "2160x3840",
                "2160x2160",
                "1536x1536",
                "1280x1280",
                "1024x1024",
                "720x720",
                "custom",
            ],
            label="Resolution",
            value="2160x2160",
        )
        custom_res = gr.Textbox(
            label="Custom Resolution (WxH)",
            visible=False,
            placeholder="e.g., 720x1280",
        )

        codec = gr.Dropdown(
            ["h264", "hevc", "vp9", "av1"],
            label="Video Codec",
            value="hevc",
        )
        bitrate = gr.Dropdown(
            ["5000k", "10000k", "20000k", "50000k"],
            label="Bitrate",
            value="20000k",
        )

    submit = gr.Button("Process Videos 🚀", variant="primary")
    output = gr.Textbox(label="Status / Errors")

    # Show/hide the custom FPS field
    fps.change(lambda x: gr.update(visible=(x == "custom")), fps, custom_fps)
    # Show/hide the custom resolution field
    resolution.change(lambda x: gr.update(visible=(x == "custom")), resolution, custom_res)

    submit.click(
        split_videos,
        inputs=[
            input_folder,
            output_folder,
            chunk_duration,
            use_original,
            fps,
            custom_fps,
            resolution,
            custom_res,
            codec,
            bitrate,
            custom_caption,
            ffmpeg_folder,
        ],
        outputs=output,
    )

if __name__ == "__main__":
    demo.launch()
