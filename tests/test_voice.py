"""Voice / STT tests — docs/ai/11-voice-integration.md, ADR-007.

Covers configuration, engine/model resolution, transcription error paths,
the recording status file, injection, the dictation toggle, and that the
registry and the Niri generator know about the voice actions.
"""

from __future__ import annotations

from omintylib import voice


# --- configuration ---------------------------------------------------------


def test_config_defaults_load():
    cfg = voice.load_config()
    stt = cfg["voice"]["stt"]
    assert cfg["voice"]["enabled"] is True
    assert stt["engine"] == "whisper.cpp"
    assert stt["capture"]["command"] == "pw-record"
    assert stt["inject"]["method"] == "wtype"


# --- engine / model resolution --------------------------------------------


def test_engine_resolution_respects_absolute_config(tmp_path):
    fake = tmp_path / "whisper-cli"
    fake.write_text("#!/bin/sh\n")
    fake.chmod(0o755)
    cfg = {"voice": {"stt": {"binary": str(fake)}}}
    assert voice.resolve_engine(cfg) == str(fake)


def test_engine_resolution_missing_is_none():
    cfg = {"voice": {"stt": {"binary": "/nonexistent/whisper-cli"}}}
    assert voice.resolve_engine(cfg) is None


def test_model_resolution_missing_is_none(tmp_path):
    cfg = {"voice": {"stt": {"model": str(tmp_path / "nope.bin")}}}
    assert voice.resolve_model(cfg) is None


# --- transcription ---------------------------------------------------------


def test_transcribe_missing_file_is_invalid(monkeypatch):
    monkeypatch.setattr(voice, "resolve_engine", lambda cfg=None: "/bin/true")
    monkeypatch.setattr(voice, "resolve_model", lambda cfg=None: "/bin/true")
    r = voice.transcribe_file("/nonexistent/audio.wav")
    assert r["success"] is False
    assert r["error"]["code"] == "INVALID_ARGUMENT"


def test_transcribe_without_engine_is_dependency_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(voice, "resolve_engine", lambda cfg=None: None)
    monkeypatch.setattr(voice, "resolve_model", lambda cfg=None: None)
    audio = tmp_path / "a.wav"
    audio.write_bytes(b"RIFF")
    r = voice.transcribe_file(str(audio))
    assert r["success"] is False
    assert r["error"]["code"] == "DEPENDENCY_MISSING"


# --- recording state -------------------------------------------------------


def test_status_round_trip(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(tmp_path))
    voice.write_status("recording", pid=123)
    status = voice.read_status()
    assert status["state"] == "recording"
    assert status["pid"] == 123
    voice.write_status("idle")
    assert voice.read_status()["state"] == "idle"


def test_read_status_defaults_to_idle(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(tmp_path))
    assert voice.read_status()["state"] == "idle"


# --- injection -------------------------------------------------------------


def test_inject_empty_text_is_noop():
    r = voice.inject_text("")
    assert r["success"] is True
    assert r["state"]["injected"] is False


def test_inject_dry_run(monkeypatch):
    monkeypatch.setenv("OMINTY_VOICE_DRY_RUN", "1")
    monkeypatch.setattr(voice.shutil, "which", lambda name: "/usr/bin/wtype")
    r = voice.inject_text("hello")
    assert r["success"] is True
    assert r["state"].get("dry_run") is True


def test_inject_without_wtype_is_dependency_missing(monkeypatch):
    monkeypatch.delenv("OMINTY_VOICE_DRY_RUN", raising=False)
    monkeypatch.setattr(voice.shutil, "which", lambda name: None)
    r = voice.inject_text("hello")
    assert r["success"] is False
    assert r["error"]["code"] == "DEPENDENCY_MISSING"


# --- dictation toggle ------------------------------------------------------


def test_dictate_disabled_by_config(monkeypatch):
    monkeypatch.setattr(
        voice, "load_config", lambda: {"voice": {"enabled": False}}
    )
    r = voice.dictate()
    assert r["success"] is False
    assert r["error"]["code"] == "ACTION_UNAVAILABLE"


def test_dictate_starts_when_idle(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(tmp_path))
    monkeypatch.setattr(voice, "load_config", lambda: {"voice": {"enabled": True}})
    called = {}

    def fake_start(cfg=None):
        called["start"] = True
        return {"success": True, "state": {"recording": True}}

    monkeypatch.setattr(voice, "start_recording", fake_start)
    monkeypatch.setattr(voice, "_recording_active", lambda: False)
    r = voice.dictate()
    assert r["success"] is True
    assert called.get("start") is True


def test_dictate_stops_when_recording(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(tmp_path))
    monkeypatch.setattr(voice, "load_config", lambda: {"voice": {"enabled": True}})
    called = {}

    def fake_stop(cfg=None):
        called["stop"] = True
        return {"success": True, "state": {"text": "hi"}}

    monkeypatch.setattr(voice, "stop_recording", fake_stop)
    monkeypatch.setattr(voice, "_recording_active", lambda: True)
    r = voice.dictate()
    assert r["success"] is True
    assert called.get("stop") is True


# --- registry / generator integration --------------------------------------


def test_registry_has_voice_actions():
    from omintylib.registry import load_registry

    reg = load_registry()
    for aid in ("voice.dictate", "voice.stop", "voice.transcribe"):
        action = reg.actions[aid]
        assert action.voice_accessible is True
        assert action.ai_accessible is False
    assert load_registry().actions["voice.dictate"].adapter == "voice.dictate"


def test_generator_emits_voice_binding():
    from omintylib.generator import generate_niri_fragment
    from omintylib.registry import load_registry

    fragment = generate_niri_fragment(
        load_registry(), "/path/to/ominty", claimed_keys=frozenset()
    )
    assert "voice.dictate" in fragment
    assert "Mod+Alt+D" in fragment
    assert '"action" "run" "voice.dictate"' in fragment
