#!/usr/bin/env python3
"""Validate an official-ai-explainer episode configuration.

Uses only the Python standard library. When ffprobe is available, local media
dimensions are inspected and low-resolution sources produce warnings.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
SOURCE_KINDS = {"official", "own-product", "illustration", "media"}
MEDIA_SUFFIXES = {".mp4", ".png", ".jpg", ".jpeg", ".webp"}
EXPECTED_RECIPES = [
    "cursor-flyover",
    "before-after-slider-scrub",
    "deck-deal-flyin",
    "ai-stream-response",
    "card-flip-reveal",
    "text-column-converge",
]
FOCUS_RECIPES = {"focus-zoom", "scan-annotate"}
ALLOWED_RECIPES = EXPECTED_RECIPES + sorted(FOCUS_RECIPES)
# Recipes whose motion is built on a real picture; deck cards are pure information.
SOURCE_REQUIRED_RECIPES = set(ALLOWED_RECIPES) - {"deck-deal-flyin"}


class Result:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def require_string(container: dict[str, Any], key: str, label: str, result: Result) -> str | None:
    value = container.get(key)
    if not is_nonempty_string(value):
        result.error(f"{label}.{key} must be a non-empty string")
        return None
    return value.strip()


COVER_TEXT_MAX = 10
COVER_LINE_MAX = 5


def cover_character_count(text: str) -> int:
    """Han glyphs count one each, a Latin/digit word counts one, punctuation counts zero."""
    words = re.findall(r"[A-Za-z0-9]+", text)
    rest = re.sub(r"[A-Za-z0-9]+", "", text)
    han = re.findall(r"[\u3040-\u30ff\u3400-\u9fff]", rest)
    return len(words) + len(han)


def cover_text_issue(text: str) -> str | None:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    total = sum(cover_character_count(line) for line in lines)
    if total > COVER_TEXT_MAX:
        return f"has {total} characters; the cover rule allows {COVER_TEXT_MAX}"
    for line in lines:
        if cover_character_count(line) > COVER_LINE_MAX:
            return f"line {line!r} exceeds {COVER_LINE_MAX} characters"
    return None


def valid_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def inspect_media(path: Path, label: str, result: Result) -> None:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        result.warn("ffprobe is unavailable; media dimensions were not inspected")
        return
    try:
        completed = subprocess.run(
            [
                ffprobe,
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height",
                "-of",
                "json",
                str(path),
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=20,
        )
        payload = json.loads(completed.stdout)
        streams = payload.get("streams") or []
        if not streams:
            result.warn(f"{label} has no readable video/image stream: {path}")
            return
        width = int(streams[0].get("width") or 0)
        height = int(streams[0].get("height") or 0)
        if width < 1920 or height < 1080:
            result.warn(f"{label} is {width}x{height}; confirm it is large enough for its on-screen size")
    except (OSError, ValueError, json.JSONDecodeError, subprocess.SubprocessError) as exc:
        result.warn(f"could not inspect {label}: {exc}")


def validate_source(
    source: Any,
    label: str,
    config_dir: Path,
    schema_only: bool,
    result: Result,
) -> None:
    if not isinstance(source, dict):
        result.error(f"{label} must be an object")
        return
    raw_path = require_string(source, "path", label, result)
    require_string(source, "label", label, result)
    source_url = require_string(source, "sourceUrl", label, result)
    if source_url and not valid_http_url(source_url):
        result.error(f"{label}.sourceUrl must be a complete HTTP/HTTPS URL")
    captured_at = source.get("capturedAt")
    if not is_nonempty_string(captured_at) or captured_at.startswith("1970"):
        result.error(f"{label}.capturedAt must be the real ISO 8601 capture time")
    kind = source.get("kind", "official")
    if kind not in SOURCE_KINDS:
        result.error(f"{label}.kind must be one of {sorted(SOURCE_KINDS)}")
    if raw_path and Path(raw_path).suffix.lower() not in MEDIA_SUFFIXES:
        result.error(f"{label}.path must be MP4, PNG, JPG or WebP")
    if raw_path and not schema_only:
        media_path = Path(raw_path).expanduser()
        if not media_path.is_absolute():
            media_path = config_dir / media_path
        media_path = media_path.resolve()
        if not media_path.is_file():
            result.error(f"{label}.path does not exist: {media_path}")
        else:
            inspect_media(media_path, label, result)


def validate_delivery(value: Any, narration: str | None, label: str, result: Result) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        result.error(f"{label} must be an object")
        return
    for key in ("emphasis", "breakAfter", "break_after"):
        phrases = value.get(key)
        if phrases is None:
            continue
        if not isinstance(phrases, list) or not all(is_nonempty_string(item) for item in phrases):
            result.error(f"{label}.{key} must be an array of non-empty strings")
            continue
        if narration:
            for phrase in phrases:
                if phrase not in narration:
                    result.error(f"{label}.{key} phrase is absent from narration: {phrase!r}")
    speed = value.get("speed")
    if speed is not None and (not isinstance(speed, (int, float)) or not 0.5 <= float(speed) <= 2.0):
        result.error(f"{label}.speed must be between 0.5 and 2.0")


def validate_pronunciation(value: Any, label: str, result: Result) -> None:
    if value is None:
        return
    if not isinstance(value, list):
        result.error(f"{label} must be an array")
        return
    for index, rule in enumerate(value):
        rule_label = f"{label}[{index}]"
        if not isinstance(rule, dict):
            result.error(f"{rule_label} must be an object")
            continue
        require_string(rule, "key", rule_label, result)
        require_string(rule, "value", rule_label, result)
        if "caseSensitive" in rule and not isinstance(rule["caseSensitive"], bool):
            result.error(f"{rule_label}.caseSensitive must be a boolean")


def validate_episode(payload: Any, config_path: Path, schema_only: bool) -> Result:
    result = Result()
    if not isinstance(payload, dict):
        result.error("episode root must be an object")
        return result

    slug = require_string(payload, "slug", "episode", result)
    if slug and not SLUG_RE.fullmatch(slug):
        result.error("episode.slug must use lowercase letters, digits, and hyphens (max 64 chars)")
    require_string(payload, "title", "episode", result)
    cover_text = require_string(payload, "coverText", "episode", result)
    if cover_text:
        issue = cover_text_issue(cover_text)
        if issue:
            result.error(f"episode.coverText {issue}")
    require_string(payload, "callToAction", "episode", result)

    hook = payload.get("hook")
    if not isinstance(hook, dict):
        result.error("episode.hook must be an object")
    else:
        require_string(hook, "statement", "episode.hook", result)
        beats = hook.get("beats")
        if not isinstance(beats, list) or len(beats) != 3 or not all(is_nonempty_string(item) for item in beats):
            result.error("episode.hook.beats must contain exactly 3 non-empty strings")

    scenes = payload.get("scenes")
    if not isinstance(scenes, list) or len(scenes) != 6:
        result.error("episode.scenes must contain exactly 6 scenes")
        return result

    for index, scene in enumerate(scenes):
        label = f"episode.scenes[{index}]"
        if not isinstance(scene, dict):
            result.error(f"{label} must be an object")
            continue
        require_string(scene, "heading", label, result)
        require_string(scene, "body", label, result)
        narration = require_string(scene, "narration", label, result)
        bullets = scene.get("bullets")
        if not isinstance(bullets, list) or not 1 <= len(bullets) <= 4 or not all(is_nonempty_string(item) for item in bullets):
            result.error(f"{label}.bullets must contain 1 to 4 non-empty strings")
        duration = scene.get("durationSeconds")
        if duration is not None and (not isinstance(duration, (int, float)) or not 2 <= float(duration) <= 30):
            result.error(f"{label}.durationSeconds must be between 2 and 30")

        recipe = scene.get("recipe", EXPECTED_RECIPES[index])
        if recipe not in ALLOWED_RECIPES:
            result.error(f"{label}.recipe must be one of {ALLOWED_RECIPES}")
        regions = scene.get("focusRegions")
        if recipe in FOCUS_RECIPES:
            limit = 1 if recipe == "focus-zoom" else 4
            if not isinstance(regions, list) or not 1 <= len(regions) <= limit:
                result.error(f"{label}.focusRegions needs 1 to {limit} regions for {recipe}")
            else:
                for index, region in enumerate(regions):
                    rlabel = f"{label}.focusRegions[{index}]"
                    values = [region.get(key) if isinstance(region, dict) else None for key in ("x", "y", "w", "h")]
                    if not all(isinstance(v, (int, float)) and 0 <= v <= 100 for v in values):
                        result.error(f"{rlabel} needs x, y, w, h between 0 and 100")
                        continue
                    x, y, w, h = values
                    if w < 2 or h < 2 or x + w > 100.001 or y + h > 100.001:
                        result.error(f"{rlabel} must sit inside the frame and be at least 2% wide and high")
                    if recipe == "scan-annotate" and not is_nonempty_string(region.get("label")):
                        result.error(f"{rlabel}.label is required for scan-annotate")
        elif regions is not None:
            result.error(f"{label}.focusRegions only applies to focus-zoom or scan-annotate")
        source = scene.get("source")
        if recipe in SOURCE_REQUIRED_RECIPES and source is None:
            result.error(f"{label}.source is required for the {recipe} scene")
        elif source is not None:
            validate_source(source, f"{label}.source", config_path.parent, schema_only, result)
        compare = scene.get("compareSource")
        if compare is not None:
            if recipe != "before-after-slider-scrub":
                result.error(f"{label}.compareSource only applies to before-after-slider-scrub")
            validate_source(compare, f"{label}.compareSource", config_path.parent, schema_only, result)

        validate_delivery(scene.get("delivery"), narration, f"{label}.delivery", result)
        validate_pronunciation(scene.get("pronunciation"), f"{label}.pronunciation", result)
        shot_copy = scene.get("shotCopy")
        if shot_copy is not None and not isinstance(shot_copy, dict):
            result.error(f"{label}.shotCopy must be an object")

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("episode", type=Path, help="Path to episode JSON")
    parser.add_argument("--schema-only", action="store_true", help="Skip local asset existence and media checks")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Print machine-readable output")
    args = parser.parse_args()

    config_path = args.episode.expanduser().resolve()
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"Episode file not found: {config_path}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON in {config_path}: {exc}", file=sys.stderr)
        return 2

    result = validate_episode(payload, config_path, args.schema_only)
    output = {
        "ok": not result.errors,
        "episode": str(config_path),
        "errors": result.errors,
        "warnings": result.warnings,
    }
    if args.json_output:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        for warning in result.warnings:
            print(f"WARNING: {warning}")
        for error in result.errors:
            print(f"ERROR: {error}")
        if not result.errors:
            print(f"OK: {config_path}")
            if result.warnings:
                print(f"Validated with {len(result.warnings)} warning(s).")
        else:
            print(f"FAILED: {len(result.errors)} error(s), {len(result.warnings)} warning(s).")
    return 1 if result.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
