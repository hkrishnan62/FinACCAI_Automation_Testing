"""FinAccAI package initializer.

Expose the core functions from `finaccai.script` at the package level for
backwards compatibility, e.g. `import finaccai` will provide access to
`run_checks`, `get_html`, etc.
"""

from .script import *  # noqa: F401,F403

__all__ = [
    'get_html', 'check_images', 'check_inputs', 'parse_color', 'rel_luminance',
    'contrast_ratio', 'check_contrast', 'check_headings', 'run_checks',
    'generate_html_report', 'read_urls_from_csv'
]
