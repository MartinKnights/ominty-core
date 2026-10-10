"""Function-row key map tests (docs/14-gks-keyboard-grammar.md §22)."""

from __future__ import annotations

from omintylib.function_keys import (
    FN_LAYER_DEFAULTS,
    FK_NAMES,
    default_keysyms,
    load_function_keys,
    physical_map,
    physical_name,
    rows,
    save_function_keys,
    template,
)


def test_24_entries():
    assert len(FK_NAMES) == 24
    assert FK_NAMES[0] == "F1"
    assert FK_NAMES[1] == "F1_fn"
    assert FK_NAMES[-1] == "F12_fn"
    assert {physical_name(n) for n in FK_NAMES} == {
        *(f"F{i}" for i in range(1, 13)),
        *(f"Fn+F{i}" for i in range(1, 13)),
    }


def test_defaults_every_entry_has_keysyms():
    for name in FK_NAMES:
        ks = default_keysyms(name)
        assert isinstance(ks, list)
        if name.endswith("_fn"):
            assert ks == FN_LAYER_DEFAULTS[name]


def test_load_missing_returns_defaults():
    data = load_function_keys("/nonexistent/function-keys.toml")
    assert set(data) == set(FK_NAMES)
    assert data["F1_fn"]["keysyms"] == ["XF86MonBrightnessDown"]
    assert data["F1"]["label"] == ""


def test_save_load_roundtrip(tmp_path):
    path = tmp_path / "function-keys.toml"
    data = {
        "F1": {"label": "refresh", "keysyms": ["F1"]},
        "F1_fn": {"label": "brightness down", "keysyms": ["XF86MonBrightnessDown"]},
    }
    saved = save_function_keys(data, path)
    assert saved.exists()
    loaded = load_function_keys(path)
    assert loaded["F1"]["label"] == "refresh"
    assert loaded["F5"]["label"] == ""  # untouched entries keep defaults
    assert loaded["F5"]["keysyms"] == ["F5"]


def test_save_backs_up_existing(tmp_path):
    path = tmp_path / "function-keys.toml"
    path.write_text("# original\n")
    save_function_keys({"F1": {"label": "x", "keysyms": ["F1"]}}, path)
    backups = list(tmp_path.glob("function-keys.toml.bak-ominty-*"))
    assert len(backups) == 1
    assert backups[0].read_text() == "# original\n"


def test_physical_map_inverts_keysyms():
    data = {
        "F5": {"label": "volume down", "keysyms": ["F5"]},
        "F5_fn": {"label": "", "keysyms": ["XF86AudioLowerVolume"]},
    }
    out = physical_map(data)
    assert out["F5"] == {"physical": "F5", "fn": False}
    assert out["XF86AudioLowerVolume"] == {"physical": "F5", "fn": True}


def test_rows_only_labelled():
    data = {
        "F1": {"label": "refresh", "keysyms": ["F1"]},
        "F2": {"label": "", "keysyms": ["F2"]},
        "F2_fn": {"label": "brightness up", "keysyms": ["XF86MonBrightnessUp"]},
    }
    out = {r["key_label"]: r for r in rows(data)}
    assert set(out) == {"F1", "Fn+F2"}
    assert out["Fn+F2"]["action_label"] == "brightness up"
    assert out["Fn+F2"]["domain"] == "Hardware"
    assert out["Fn+F2"]["managed_by"] == "function-keys"


def test_template_roundtrips():
    text = template()
    assert text.startswith("# ominty function-keys.toml")
    assert text.count("[function_keys]") == 1
    # A template written to disk loads cleanly with 24 default entries.
    import pathlib

    p = pathlib.Path("/tmp") / "fk-template-test.toml"
    p.write_text(text)
    loaded = load_function_keys(p)
    assert set(loaded) == set(FK_NAMES)
    assert loaded["F7_fn"]["keysyms"] == ["Print"]