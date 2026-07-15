import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ttuploader",
        description="Auto upload YouTube Shorts to TikTok",
    )
    parser.add_argument(
        "--env",
        default=".env",
        help="Path to .env file (default: .env)",
    )
    parser.add_argument(
        "--session",
        required=True,
        help="Session name (creates data/sessions/{session}/ folder)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode (no GUI window)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run pipeline once and exit (no loop)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=None,
        help="Override check interval in seconds",
    )
    return parser
