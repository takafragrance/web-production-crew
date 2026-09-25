"""ponytail: smoke check for resolve_llm / placeholder images. Run: python main.check.py"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from main import PLACEHOLDER_IMAGES, resolve_llm, write_placeholder_images


def main() -> None:
    os.environ.pop("OPENAI_MODEL_NAME", None)
    assert resolve_llm() is None

    os.environ["OPENAI_MODEL_NAME"] = "gpt-4o-mini"
    assert resolve_llm() == "openai/gpt-4o-mini"

    os.environ["OPENAI_MODEL_NAME"] = "openai/gpt-4o"
    assert resolve_llm() == "openai/gpt-4o"

    with tempfile.TemporaryDirectory() as tmp:
        images_dir = Path(tmp) / "images"
        write_placeholder_images(images_dir)
        names = {p.name for p in images_dir.iterdir()}
        expected = {name for name, _, _ in PLACEHOLDER_IMAGES}
        assert names == expected, names
        # second call must not overwrite existing files
        first = (images_dir / "mv.svg").read_text(encoding="utf-8")
        write_placeholder_images(images_dir)
        assert (images_dir / "mv.svg").read_text(encoding="utf-8") == first

    print("main.check.py: ok")


if __name__ == "__main__":
    main()
