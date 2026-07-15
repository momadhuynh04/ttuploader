import asyncio
import time
from pathlib import Path

from src.renderer.strategies import get_strategy


async def render_video(
    input_path: str,
    output_dir: Path,
    render_strategy: str = "stealth",
    audio_strategy: str = "pitch_speedshift",
    enable_hflip: bool = False,
) -> tuple[str, float]:
    output_path = str(output_dir / "processed.mp4")
    strategy = get_strategy(render_strategy)

    start = time.time()
    print(f"[RENDER] Strategy: {render_strategy} | Audio: {audio_strategy} | Hflip: {enable_hflip}", flush=True)

    if render_strategy in ("stealth", "transform", "loop"):
        result_path = await strategy.render(input_path, output_path, audio_strategy, enable_hflip)
    else:
        result_path = await strategy.render(input_path, output_path, audio_strategy)

    elapsed = time.time() - start

    if result_path == input_path or not Path(result_path).exists():
        return input_path, elapsed

    return result_path, elapsed
