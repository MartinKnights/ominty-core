# Rollback Test (DoD §24)

**Date:** 2026-09-19
**Stage:** Phase 1 close-out
**Status:** Complete — rollback verified

DoD §24 requires that relevant configuration can be restored and that at
least one rollback test has been performed successfully
(docs/13-phase-1-definition-of-done.md §24, AGENTS.md §30).

---

## 1. Backup inventory

| Artifact | Backups |
|---|---|
| Niri config | 4 timestamped copies (`config.kdl.backup*`, `.bak-dms-pre-*`, `.bak-omivoid-*`) |
| Omivoid generated fragment | regenerable from the Action Registry |
| DMS `plugin_settings.json` | `plugin_settings.json.bak-*` (incl. pre-Omivoid) |

Backup strategy (environment-audit §11): a timestamped copy is taken before
each significant configuration change.

---

## 2. Drill A — generated fragment loss → regenerate

The Omivoid-owned Niri fragment
(`~/.config/omivoid/generated/niri/bindings.kdl`) is derived from the Action
Registry, so its rollback is: lose it → rebuild it.

```text
1. sha256(bindings.kdl)                     = f2d5125a…78964
2. mv bindings.kdl /tmp/bindings.kdl.saved  (simulate loss)
3. niri validate                            → config is valid
   (the include is optional=true, so a missing fragment cannot block Niri)
4. build_fragment(load_registry())          → regenerated
5. sha256(bindings.kdl)                     = f2d5125a…78964  ← identical
6. niri msg action load-config-file         → reloaded
```

**Result:** deterministic recovery — the regenerated fragment is
byte-identical to the lost one, and Niri remains valid throughout.

---

## 3. Drill B — Niri config backups validate

Each backup was validated in place with `niri validate -c`:

```text
config.kdl.backup1789157721              → config is valid
config.kdl.backup.2026-09-11_15-53-46    → config is valid
config.kdl.bak-dms-pre-20260911-155305    → config is valid
config.kdl.bak-omivoid-20260911           → config is valid
```

**Result:** all backups parse as valid Niri configurations and are therefore
restorable.

---

## 4. Drill C — live-path restore and rollback

A file-level restore was performed on the live config path, then rolled back
(without reloading the old config, so the running session was unaffected):

```text
1. cp config.kdl /tmp/config.kdl.current
   sha256(config.kdl) = e53c8b57…87437
2. cp config.kdl.bak-dms-pre-20260911-155305 config.kdl   (restore backup)
   niri validate → config is valid
3. cp /tmp/config.kdl.current config.kdl                  (roll back)
   sha256(config.kdl) = e53c8b57…87437  ← identical
   niri validate → config is valid
4. niri msg action load-config-file → reloaded
```

**Result:** restore and rollback both succeed; the live config is unchanged.

---

## 5. Restore procedures

**Regenerate the Niri fragment from the registry:**

```bash
cd omivoid-lmde/cli
python3 -c "from omivoidlib.registry import load_registry; \
            from omivoidlib.generator import build_fragment; \
            print(build_fragment(load_registry())[1])"
```

**Restore a Niri config backup:**

```bash
cp ~/.config/niri/config.kdl ~/.config/niri/config.kdl.pre-restore
cp ~/.config/niri/<backup> ~/.config/niri/config.kdl
niri validate
niri msg action load-config-file
```

**Restore DMS plugin settings:**

```bash
cp ~/.config/DankMaterialShell/plugin_settings.json.bak-<stamp> \
   ~/.config/DankMaterialShell/plugin_settings.json
dms restart   # DMS reads plugin settings only at startup
```

---

## 6. Conclusion

Two independent rollback paths were exercised successfully (generated
fragment regeneration; live config restore + rollback), and all Niri
backups validate. **DoD §24 is satisfied.**
