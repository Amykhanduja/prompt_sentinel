ZERO_WIDTH_CHARS = [
    "\u200b",  # Zero Width Space
    "\u200c",  # Zero Width Non-Joiner
    "\u200d",  # Zero Width Joiner
    "\ufeff"   # Zero Width No-Break Space (BOM)
]


def remove_zero_width(text: str):

    modified = text

    for char in ZERO_WIDTH_CHARS:
        modified = modified.replace(char, "")

    removed_flag = modified != text

    return modified, removed_flag
