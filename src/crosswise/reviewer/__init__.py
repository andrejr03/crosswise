"""Static local reviewer interface generation for Crosswise outputs."""

from crosswise.reviewer.static_html import (
    CURATED_STORY_LABELS,
    DEFAULT_OUTPUT_PATH,
    INTERACTIVE_EXPLORER_SELECTOR,
    INTERACTIVE_SCREENSHOT_OUTPUT_PATH,
    REQUIRED_OUTPUT_PATHS,
    SCREENSHOT_OUTPUT_PATH,
    generate_reviewer_screenshot,
    generate_static_reviewer,
    load_required_outputs,
    render_static_reviewer,
    write_static_reviewer,
)

__all__ = [
    "CURATED_STORY_LABELS",
    "DEFAULT_OUTPUT_PATH",
    "INTERACTIVE_EXPLORER_SELECTOR",
    "INTERACTIVE_SCREENSHOT_OUTPUT_PATH",
    "REQUIRED_OUTPUT_PATHS",
    "SCREENSHOT_OUTPUT_PATH",
    "generate_reviewer_screenshot",
    "generate_static_reviewer",
    "load_required_outputs",
    "render_static_reviewer",
    "write_static_reviewer",
]
