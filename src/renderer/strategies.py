import asyncio
import os
import random
import subprocess
from pathlib import Path


def detect_gpu_encoder() -> str:
    try:
        result = subprocess.run(
            ["ffmpeg", "-encoders"], capture_output=True, text=True, timeout=5
        )
        if "h264_nvenc" in result.stdout:
            return "h264_nvenc"
        if "h264_qsv" in result.stdout:
            return "h264_qsv"
    except Exception:
        pass
    return "libx264"


def get_video_duration(video_path: str) -> float:
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path,
    ]
    try:
        return float(subprocess.check_output(probe_cmd, timeout=10).decode("utf-8").strip())
    except Exception:
        return 15.0


def _gpu_preset(encoder: str) -> list[str]:
    if encoder == "h264_nvenc":
        return ["-preset", "p4", "-rc", "vbr", "-cq", "23", "-b:v", "0"]
    elif encoder == "libx264":
        return ["-preset", "ultrafast", "-crf", "23"]
    return []


def _common_tail() -> list[str]:
    return ["-map_metadata", "-1", "-map_chapters", "-1", "-movflags", "+faststart", "-fflags", "+genpts"]


def _build_audio_args(strategy: str) -> list[str]:
    if strategy == "none" or not strategy:
        return []
    if strategy in ("pitch_speedshift", "pitch_speed", "enhanced_pitch"):
        return ["-af", "asetrate=44100*1.07,atempo=1/1.07,aresample=44100", "-c:a", "aac", "-b:a", "128k"]
    if strategy in ("re_encode", "replace", "audio_mix", "full_replace"):
        return ["-c:a", "aac", "-b:a", "128k"]
    if strategy in ("no_sound", "strip"):
        return ["-an"]
    return []


class BaseStrategy:
    async def render(self, input_path: str, output_path: str, audio_strategy: str = "") -> str:
        return input_path


class NoneStrategy(BaseStrategy):
    pass


class StealthStrategy(BaseStrategy):
    async def render(self, input_path: str, output_path: str, audio_strategy: str = "", enable_hflip: bool = False) -> str:
        encoder = detect_gpu_encoder()

        vf_chain = (
            "crop=iw*0.97:ih*0.97:iw*0.015:ih*0.015,"
            "scale=1080:1920,"
            "eq=brightness=0.03:contrast=1.03:saturation=1.05,"
            "setpts=PTS/1.02"
        )
        if enable_hflip:
            vf_chain = "hflip," + vf_chain
        else:
            vf_chain += ",rotate=0.005:ow=1080:oh=1920:fillcolor=none,noise=alls=2:allf=t+u"

        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vf", vf_chain,
            "-c:v", encoder,
            "-pix_fmt", "yuv420p",
        ]
        cmd += _gpu_preset(encoder)
        cmd += _build_audio_args(audio_strategy)
        cmd += _common_tail()
        cmd.append(output_path)

        return await _run_ffmpeg(cmd, input_path, output_path)


class TransformStrategy(BaseStrategy):
    async def render(self, input_path: str, output_path: str, audio_strategy: str = "", enable_hflip: bool = False) -> str:
        encoder = detect_gpu_encoder()

        vf_chain = (
            "crop=iw*0.96:ih*0.96:iw*0.02:ih*0.02,"
            "scale=1080:1920,"
            "eq=brightness=0.04:contrast=1.04:saturation=1.06,"
            "setpts=PTS/1.02,"
            "unsharp=5:5:1.0,"
            "noise=alls=3:allf=t+u"
        )
        if enable_hflip:
            vf_chain = "hflip," + vf_chain

        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vf", vf_chain,
            "-c:v", encoder,
            "-pix_fmt", "yuv420p",
        ]
        cmd += _gpu_preset(encoder)
        cmd += _build_audio_args(audio_strategy)
        cmd += _common_tail()
        cmd.append(output_path)

        return await _run_ffmpeg(cmd, input_path, output_path)


class LoopStrategy(BaseStrategy):
    async def render(self, input_path: str, output_path: str, audio_strategy: str = "", enable_hflip: bool = False) -> str:
        encoder = detect_gpu_encoder()
        duration = get_video_duration(input_path)

        if duration > 30:
            return await self._render_alt_loop(input_path, output_path, encoder, audio_strategy, enable_hflip)
        return await self._render_full_loop(input_path, output_path, encoder, audio_strategy, enable_hflip)

    def _build_loop_audio(self, args: list[str], filter_complex: str, mode: str) -> str:
        if mode in ("pitch_speedshift", "pitch_speed", "enhanced_pitch"):
            return (
                filter_complex + ";"
                "[0:a]asplit=2[a1][a2];"
                "[a1]asetrate=44100*1.04,atempo=1/1.04[a1p];"
                "[a2]asetrate=44100*0.97,atempo=1/0.97[a2p];"
                "[a1p][a2p]concat=n=2:v=0:a=1[a]"
            )
        return filter_complex

    async def _render_full_loop(self, input_path, output_path, encoder, audio_strategy, enable_hflip):
        half1 = (
            "crop=iw*0.97:ih*0.97:iw*0.015:ih*0.015,"
            "scale=1080:1920,eq=brightness=0.03:contrast=1.03:saturation=1.05,"
            "setpts=PTS/1.01"
        )
        half2 = (
            "crop=iw*0.96:ih*0.96:iw*0.02:ih*0.02,"
            "scale=1080:1920,eq=brightness=-0.02:contrast=1.05:saturation=0.95,"
            "setpts=PTS/1.01"
        )
        if enable_hflip:
            half1 = "hflip," + half1
        else:
            half1 += ",rotate=0.005:ow=1080:oh=1920:fillcolor=none"
            half2 += ",unsharp=3:3:0.8"

        fc = (
            "[0:v]split=2[v1][v2];"
            f"[v1]{half1}[va];"
            f"[v2]{half2}[vb];"
            "[va][vb]concat=n=2:v=1:a=0[v]"
        )
        fc = self._build_loop_audio([], fc, audio_strategy)

        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-filter_complex", fc,
            "-map", "[v]",
            "-c:v", encoder,
            "-pix_fmt", "yuv420p",
        ]
        cmd += _gpu_preset(encoder)
        cmd += _common_tail()

        if audio_strategy in ("pitch_speedshift", "pitch_speed", "enhanced_pitch"):
            cmd += ["-map", "[a]", "-c:a", "aac", "-b:a", "128k"]
        elif audio_strategy in ("re_encode", "replace", "audio_mix", "full_replace"):
            cmd += ["-map", "0:a:0?", "-c:a", "aac", "-b:a", "128k"]
        elif audio_strategy in ("no_sound", "strip"):
            cmd += ["-an"]
        cmd.append(output_path)

        return await _run_ffmpeg(cmd, input_path, output_path)

    async def _render_alt_loop(self, input_path, output_path, encoder, audio_strategy, enable_hflip):
        part1 = (
            "crop=iw*0.97:ih*0.97:iw*0.015:ih*0.015,"
            "scale=1080:1920,eq=brightness=0.03:contrast=1.03:saturation=1.05,"
            "setpts=PTS/0.67"
        )
        part2 = (
            "crop=iw*0.96:ih*0.96:iw*0.02:ih*0.02,"
            "scale=1080:1920,eq=brightness=-0.02:contrast=1.05:saturation=0.95,"
            "setpts=PTS/0.67"
        )
        if not enable_hflip:
            part1 += ",rotate=0.005:ow=1080:oh=1920:fillcolor=none"

        fc = (
            "[0:v]split=3[v1][v2][v3];"
            f"[v1]{part1}[va];"
            f"[v2]{part2}[vb];"
            "[va][vb]concat=n=2:v=1:a=0[v]"
        )
        fc = self._build_loop_audio([], fc, audio_strategy)

        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-filter_complex", fc,
            "-map", "[v]",
            "-c:v", encoder,
            "-pix_fmt", "yuv420p",
        ]
        cmd += _gpu_preset(encoder)
        cmd += _common_tail()

        if audio_strategy in ("pitch_speedshift", "pitch_speed", "enhanced_pitch"):
            cmd += ["-map", "[a]", "-c:a", "aac", "-b:a", "128k"]
        elif audio_strategy in ("re_encode", "replace", "audio_mix", "full_replace"):
            cmd += ["-map", "0:a:0?", "-c:a", "aac", "-b:a", "128k"]
        elif audio_strategy in ("no_sound", "strip"):
            cmd += ["-an"]
        cmd.append(output_path)

        return await _run_ffmpeg(cmd, input_path, output_path)


STRATEGY_MAP: dict[str, BaseStrategy] = {
    "none": NoneStrategy(),
    "stealth": StealthStrategy(),
    "loop": LoopStrategy(),
    "transform": TransformStrategy(),
}


def get_strategy(name: str) -> BaseStrategy:
    return STRATEGY_MAP.get(name.lower(), StealthStrategy())


async def _run_ffmpeg(cmd: list[str], input_path: str, output_path: str) -> str:
    print(f"[RENDER] Encoding video ({os.path.getsize(input_path) / 1024 / 1024:.1f} MB)...", flush=True)
    loop = asyncio.get_event_loop()
    proc = await loop.run_in_executor(
        None,
        lambda: subprocess.run(cmd, capture_output=True, timeout=300),
    )

    if proc.returncode == 0 and os.path.exists(output_path):
        out_size = os.path.getsize(output_path) / 1024 / 1024
        print(f"[RENDER] OK — {out_size:.1f} MB", flush=True)
        with open(output_path, "ab") as f:
            f.write(os.urandom(random.randint(1024, 5120)))
        return output_path

    print(f"[!] FFmpeg failed (rc={proc.returncode}), falling back to stream copy", flush=True)
    if proc.stderr:
        print(f"    stderr: {proc.stderr.decode('utf-8', errors='replace')[-300:]}", flush=True)
    return await _stream_copy(input_path, output_path)


async def _stream_copy(input_path: str, output_path: str) -> str:
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-c:v", "copy",
        "-c:a", "copy",
        "-map_metadata", "-1",
        output_path,
    ]
    loop = asyncio.get_event_loop()
    proc = await loop.run_in_executor(
        None,
        lambda: subprocess.run(cmd, capture_output=True, timeout=120),
    )
    if proc.returncode == 0 and os.path.exists(output_path):
        with open(output_path, "ab") as f:
            f.write(os.urandom(random.randint(1024, 5120)))
        return output_path
    return input_path
