"""Static local reviewer interface generation for Crosswise outputs."""

from crosswise.reviewer.static_html import (
    DEFAULT_OUTPUT_PATH,
    REQUIRED_OUTPUT_PATHS,
    generate_static_reviewer,
    load_required_outputs,
    render_static_reviewer,
    write_static_reviewer,
)

__all__ = [
    "DEFAULT_OUTPUT_PATH",
    "REQUIRED_OUTPUT_PATHS",
    "generate_static_reviewer",
    "load_required_outputs",
    "render_static_reviewer",
    "write_static_reviewer",
]
