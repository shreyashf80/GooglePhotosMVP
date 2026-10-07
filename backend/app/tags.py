import re
import unicodedata

def normalize(value: str) -> str:
    text = unicodedata.normalize("NFKD", value.lower().strip())
    text = "".join(c for c in text if not unicodedata.combining(c))
    # Christmas is singular: preserve the explicit PRD normalization example.
    def singular(word):
        return word[:-1] if word != "christmas" and len(word) > 3 and word.endswith("s") and not word.endswith(("ss", "us")) else word
    return " ".join(singular(word) for word in re.sub(r"\s+", " ", text).split())

def build_tags(values):
    tags = set()
    for value in values:
        value = normalize(value)
        if value:
            tags.add(value)
            tags.update(value.split())
    return sorted(tags)
