import re

TELEGRAM_CHANNEL_LINK_PATTERN = r'(t\.me/[\w+-]+)'
_regex = re.compile(TELEGRAM_CHANNEL_LINK_PATTERN)

def extract_telegram_channel_link(text) -> list[str]:
    results = _regex.findall(text)
    return results if set(results) is not None else set()
