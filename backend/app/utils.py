import re
import unicodedata


_slug_re = re.compile(r"[^a-z0-9]+")


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower().strip()
    value = _slug_re.sub("-", value).strip("-")
    return value or "item"

