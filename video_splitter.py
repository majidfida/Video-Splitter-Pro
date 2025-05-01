import os
import subprocess
import threading
import gradio as gr
from datetime import datetime
import torch
import ffmpeg

# === Configuration ===
DEFAULT_FFMPEG_DIR = r"C:\ffmpeg\bin"

# Locate FFmpeg: explicit -> PATH -> local bundle
def find_ffmpeg():
    exe = 'ffmpeg.exe' if os.name == 'nt' else 'ffmpeg'
    default = os.path.join(DEFAULT_FFMPEG_DIR, exe)
    if os.path.isfile(default): return default
    for p in os.environ.get('PATH', '').split(os.pathsep):
        cand = os.path.join(p, exe)
        if os.path.isfile(cand): return cand
    bundled = os.path.join(os.getcwd(), 'ffmpeg', 'bin', exe)
    if os.path.isfile(bundled): return bundled
    return None

ffmpeg_path = find_ffmpeg()
if not ffmpeg_path:
    raise FileNotFoundError(f"ffmpeg not found. Checked {DEFAULT_FFMPEG_DIR}, PATH, and ./ffmpeg/bin.")
print(f"Using FFmpeg at: {ffmpeg_path}")

stop_event = threading.Event()

def split_videos(
    input_folder, output_folder, chunk_duration,
    use_original, fps, custom_fps, resolution, custom_res, vertical,
    codec, bitrate, output_format,
    include_audio, audio_codec, audio_bitrate,
    crf, use_cuda
):
    stop_event.clear()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(output_folder, f"output_{ts}")
    os.makedirs(out_dir, exist_ok=True)

    files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.mp4','.mov','.avi','.mkv'))]
    if not files:
        return "No video files found."

    for f in files:
        if stop_event.is_set():
            return "⚠️ Processing stopped by user."
        inp = os.path.join(input_folder, f)
        base = os.path.splitext(f)[0]
        pat = os.path.join(out_dir, f"{base}_%03d.{output_format}")

        if use_original:
            probe = ffmpeg.probe(inp)
            vs = next(s for s in probe['streams'] if s['codec_type']=='video')
            cur_fps = eval(vs['r_frame_rate'])
            w, h = vs['width'], vs['height']
        else:
            cur_fps = custom_fps if fps=='custom' else float(fps)
            if resolution=='custom':
                w,h = map(int, custom_res.split('x'))
            else:
                w,h = map(int, resolution.split('x'))
            if vertical: w,h = h,w

        cmd = [ffmpeg_path]
        if use_cuda: cmd += ['-hwaccel','cuda']
        cmd += ['-i', inp]

        # Video codec settings
        if use_original:
            cmd += ['-c:v','copy']
        else:
            vc_arg = f"{codec}_nvenc" if (use_cuda and codec in ['h264','hevc']) else codec
            cmd += ['-c:v', vc_arg]
            if codec in ['h264','hevc','vp9','av1']:
                cmd += ['-crf', str(crf)]
            else:
                cmd += ['-b:v', bitrate]
            keyint = int(cur_fps * chunk_duration)
            cmd += ['-g', str(keyint), '-sc_threshold', '0']
            cmd += ['-r', str(cur_fps), '-s', f'{w}x{h}']

        # Audio settings
        if include_audio:
            if use_original:
                cmd += ['-c:a','copy']
            else:
                cmd += ['-c:a', audio_codec, '-b:a', audio_bitrate]
            cmd += ['-map','0:v','-map','0:a']
        else:
            cmd += ['-map','0:v']

        # Segment
        cmd += ['-f','segment','-segment_time', str(chunk_duration), '-reset_timestamps','1', pat]

        subprocess.run(cmd, check=True)

    return f"✅ Done. Files in {out_dir}"


def build_ui():
    with gr.Blocks() as demo:
        demo.queue()
        gr.Markdown("# 🎥 Video Splitter Pro\n_Created by Eagle-42_")
        gr.Markdown(f"**GPU:** {('CUDA ' + torch.version.cuda if torch.cuda.is_available() else 'No NVIDIA GPU')} ")
        with gr.Row():
            inp=gr.Textbox(label="Input Folder")
            out=gr.Textbox(label="Output Folder")
        dur=gr.Number(label="Clip Duration (s)", value=3, precision=0)
        with gr.Accordion("Advanced Settings", open=False):
            orig=gr.Checkbox(label="Use Original Settings", value=True)
            fps=gr.Dropdown(["16","18","24","30","60","custom"], label="FPS", value="30")
            c_fps=gr.Number(label="Custom FPS", visible=False)
            res=gr.Dropdown(["1280x720","1920x1080","3840x2160","custom"], label="Resolution", value="1920x1080")
            c_res=gr.Textbox(label="Custom Res (WxH)", visible=False)
            vert=gr.Checkbox(label="Vertical Orientation", value=False)
            codec=gr.Dropdown(["h264","hevc","vp9","av1"], label="Video Codec", value="h264")
            crf=gr.Slider(0,51, value=23, step=1, label="CRF")
            br=gr.Dropdown(["5000k","10000k","20000k"], label="Bitrate", value="10000k")
            fmt=gr.Dropdown(["mp4","mkv","mov"], label="Format", value="mp4")
            audio=gr.Checkbox(label="Include Audio", value=True)
            a_codec=gr.Dropdown(["copy","aac","opus"], label="Audio Codec", value="copy")
            a_br=gr.Dropdown(["128k","192k","256k"], label="Audio Bitrate", value="192k")
            cuda=gr.Checkbox(label="Use CUDA Acceleration", value=torch.cuda.is_available())
        with gr.Row():
            start_btn=gr.Button("Process Videos 🚀", variant="primary")
            stop_btn=gr.Button("Stop", variant="stop")
        status=gr.Textbox(label="Status", interactive=False)

        fps.change(lambda x: gr.update(visible=x=='custom'), fps, c_fps)
        res.change(lambda x: gr.update(visible=x=='custom'), res, c_res)

        start_btn.click(
            split_videos,
            inputs=[inp,out,dur,orig,fps,c_fps,res,c_res,vert,codec,br,fmt,audio,a_codec,a_br,crf,cuda],
            outputs=status
        )
        stop_btn.click(lambda: stop_event.set() or "⚠️ Stopping...", None, status)

    return demo

if __name__=='__main__':
    build_ui().launch(share=True)
