"""Update the license headers in all source files (../src/.py)."""

from pathlib import Path
import re

HEADER = re.compile(r"Copyright \(c\) .*?,")
src = Path("../src")
files = src.rglob("*.py")

for path in files:
    with path.open("r", encoding="utf-8") as file:
        content = file.read()

    content = HEADER.sub("Copyright (c) 2016-2020,", content)
    with path.open("wb") as file:
        file.write(content.encode("utf-8"))
    print(f"Writing in {path}...")
