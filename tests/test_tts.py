"""TTS document tests — extraction, cleaning, chunking (docs/ai/11)."""

from __future__ import annotations

import pytest

from omintylib import tts


def test_chunk_text_respects_max_chars():
    text = "\n\n".join(
        "Sentence number %d here. It has a few words total." % i for i in range(50)
    )
    chunks = tts.chunk_text(text, max_chars=200)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 200


def test_clean_text_removes_junk():
    dirty = "line one\n====\nPage 3\n\n\n   line two\n"
    clean = tts.clean_text(dirty)
    assert "====" not in clean
    assert "Page" not in clean
    assert "\n\n\n" not in clean
    assert "line two" in clean


def test_prepare_document_markdown(tmp_path):
    md = tmp_path / "doc.md"
    md.write_text("# Title\n\nHello **world** and *italics*.\n\nSecond paragraph.\n\n" * 30)
    prep = tts.prepare_document(str(md), max_chars=600)  # force several chunks
    assert prep.title == "doc"
    assert prep.total >= 2
    assert "**" not in prep.text        # pandoc strips markdown emphasis
    assert "*" not in prep.text


def test_prepare_document_txt(tmp_path):
    txt = tmp_path / "plain.txt"
    txt.write_text("Just some plain words to read aloud.\n" * 30)
    prep = tts.prepare_document(str(txt))
    assert prep.title == "plain"
    assert "plain words" in prep.text


def test_unsupported_extension_raises():
    with pytest.raises(tts.TTSError):
        tts.extract_text("archive.rar")


def test_missing_file_raises(tmp_path):
    with pytest.raises(tts.TTSError):
        tts.prepare_document(tmp_path / "nope.md")


def test_run_dir_and_state_round_trip(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(tmp_path))
    d = tts.run_dir()
    assert d.is_dir()
    d.joinpath("state.json").write_text('{"current": 2, "total": 9}')
    state = tts.read_state()
    assert state["current"] == 2
    assert state["total"] == 9


def test_send_command_without_player(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(tmp_path))
    result = tts.send_command("next")
    assert result["success"] is False
    assert result["error"]["code"] == "ACTION_UNAVAILABLE"