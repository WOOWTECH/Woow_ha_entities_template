"""Runtime translations ship for en and zh-Hant (commercial acceptance INFRA-HA-009-3).

Home Assistant reads a custom integration's UI text from translations/<lang>.json
only; strings.json is a development source it never loads for custom
components. With no translations/ directory the config flow showed raw field
keys such as 'switch_entity' to every user, in every language.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

COMPONENT = Path(__file__).resolve().parents[1]
STRINGS = COMPONENT / "strings.json"
TRANSLATIONS = COMPONENT / "translations"
ENGLISH_WORD = re.compile(r"[A-Za-z]{3,}")
CJK = re.compile(r"[㐀-鿿]")
PLACEHOLDER = re.compile(r"\{\{ ?\w+ ?\}\}|\{\w+\}")


def _leaves(node: object, prefix: str = "") -> dict[str, str]:
    if isinstance(node, dict):
        out: dict[str, str] = {}
        for key, value in node.items():
            out.update(_leaves(value, f"{prefix}{key}."))
        return out
    return {prefix[:-1]: node} if isinstance(node, str) else {}


def _load(path: Path) -> dict[str, str]:
    return _leaves(json.loads(path.read_text(encoding="utf-8")))


def test_en_translation_is_a_verbatim_copy_of_strings() -> None:
    english = (TRANSLATIONS / "en.json").read_text(encoding="utf-8")
    assert english == STRINGS.read_text(encoding="utf-8")


def test_zh_hant_mirrors_strings_keys() -> None:
    assert set(_load(TRANSLATIONS / "zh-Hant.json")) == set(_load(STRINGS))


def test_zh_hant_translates_every_english_sentence() -> None:
    english = _load(STRINGS)
    chinese = _load(TRANSLATIONS / "zh-Hant.json")
    untranslated = sorted(
        key
        for key, text in english.items()
        if ENGLISH_WORD.search(PLACEHOLDER.sub("", text))
        and not CJK.search(chinese.get(key, ""))
    )
    assert not untranslated


def test_zh_hant_keeps_every_placeholder() -> None:
    english = _load(STRINGS)
    chinese = _load(TRANSLATIONS / "zh-Hant.json")
    for key, text in english.items():
        assert sorted(PLACEHOLDER.findall(chinese[key])) == sorted(
            PLACEHOLDER.findall(text)
        ), key
