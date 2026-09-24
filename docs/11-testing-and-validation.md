# Omivoid LMDE — Testing and Validation Specification

**Project:** `omivoid-lmde`
**Phase:** Phase 1

---

# 1. Purpose

This document defines the minimum testing and validation requirements for Phase 1.

Omivoid changes desktop configuration and system interaction.

Testing must therefore protect both:

* architectural correctness;
* continued usability of the machine.

---

# 2. Testing Principles

Testing should be:

* incremental;
* repeatable;
* automated where practical;
* non-destructive by default;
* architecture-aware;
* capable of catching configuration failures before activation.

---

# 3. Test Categories

Phase 1 testing should cover:

```text
registry
configuration
adapters
Niri
DMS
theme
AI
integration
rollback
```

---

# 4. Registry Parsing Tests

Test:

* valid TOML;
* malformed TOML;
* duplicate action IDs;
* missing required fields;
* invalid registry version;
* invalid action ID format.

Expected result:

Invalid registry input must fail validation clearly.

---

# 5. Registry Schema Tests

Validate supported values for:

```text
risk
confirmation
contexts
platforms
```

Unknown required enum values should not be silently accepted.

---

# 6. Keybinding Conflict Tests

The validator should detect:

* duplicate direct bindings;
* duplicate chord bindings;
* prefix conflicts where detectable;
* duplicate primary bindings.

Existing Niri bindings should also be compared against proposed generated bindings.

---

# 7. Application Role Tests

For each configured application role:

```text
terminal
browser
files
editor
notes
mail
```

test:

1. role exists;
2. command can be resolved;
3. action can invoke the role;
4. missing application produces understandable error.

---

# 8. Adapter Tests

Each adapter should be testable independently where practical.

Test:

* valid invocation;
* invalid arguments;
* missing dependency;
* unsupported platform;
* implementation failure;
* returned status.

---

# 9. Dry-Run Capability

Where practical, destructive or configuration-writing tools should support:

```text
--dry-run
```

or an equivalent validation mode.

Examples:

* registry build;
* generated Niri config;
* theme generation.

Dry run should describe intended changes without applying them.

---

# 10. Niri Configuration Validation

Generated Niri configuration must be checked before replacing or enabling it.

The implementation should use Niri's supported validation mechanisms where available.

If no direct validator exists, use the safest available parse/test approach.

A generated failure must not destroy the known-working config.

---

# 11. Niri Behaviour Tests

Verify:

* focus left/right/up/down;
* window close;
* fullscreen toggle;
* workspace movement;
* workspace navigation;
* application launch bindings;
* `Super+K`;
* `Super+Space`;
* `Super+A`.

These should be tested on the actual compositor session after static validation.

---

# 12. Existing Behaviour Regression

Record important existing Niri behaviour before Omivoid changes.

After integration verify that unrelated functionality still works.

Examples:

* touchpad;
* output configuration;
* window rules;
* startup applications;
* existing useful custom bindings.

---

# 13. DMS Tests

Where DMS is adopted, validate:

* startup;
* bar rendering;
* Niri integration;
* workspace state;
* notifications;
* OSD;
* network controls;
* audio controls;
* wallpaper;
* theme updates;
* action/IPC invocation.

DMS failure should not make native Niri interaction inaccessible.

---

# 14. Theme Tests

Test:

1. select wallpaper;
2. palette changes;
3. DMS reflects palette;
4. external theme consumer reflects palette;
5. palette regeneration works;
6. mode toggle works where implemented.

---

# 15. Theme Failure Tests

Test failure of one consumer.

Expected behaviour:

* remaining consumers stay functional;
* partial failure is reported;
* configuration files are not corrupted.

---

# 16. Generated File Tests

Generated files should be checked for:

* correct syntax;
* deterministic output;
* expected header;
* no unrelated content;
* stable formatting.

Repeated generation from unchanged inputs should ideally produce no diff.

---

# 17. CLI Tests

Test:

```text
omivoid action list
omivoid action show
omivoid action search
omivoid action run
omivoid registry validate
omivoid registry build
```

Invalid action IDs must return non-zero exit status where appropriate.

---

# 18. Structured Error Tests

Verify stable errors including:

```text
ACTION_NOT_FOUND
ACTION_UNAVAILABLE
DEPENDENCY_MISSING
INVALID_ARGUMENT
PERMISSION_DENIED
CONFIRMATION_REQUIRED
ADAPTER_FAILED
CONTEXT_UNAVAILABLE
PLATFORM_UNSUPPORTED
```

Not every error must be implemented immediately, but implemented cases must remain consistent.

---

# 19. AI Permission Tests

Verify that:

```text
ai_accessible = false
```

actions are not exposed as callable AI capabilities.

Test at least one allowed and one denied action.

---

# 20. AI Confirmation Tests

For an action marked:

```text
confirmation = "ai-only"
```

verify that AI invocation cannot proceed without the required confirmation mechanism.

Direct keyboard invocation may follow normal desktop behaviour.

---

# 21. AI Capability Proof Test

A Phase 1 integration test should demonstrate:

```text
AI request
  ↓
registered action
  ↓
action validation
  ↓
adapter
  ↓
successful desktop result
```

Recommended test:

```text
app.browser.open
```

---

# 22. Context Tests

If selection-based AI actions are implemented:

* selected text present;
* no selection;
* stale clipboard state;
* unsupported application;
* context retrieval failure.

No selection should produce:

```text
CONTEXT_UNAVAILABLE
```

rather than fabricated or stale context.

---

# 23. Platform Tests

Verify platform detection.

Current expected result:

```text
debian
```

for LMDE.

Platform detection must not be duplicated across unrelated modules.

---

# 24. Path Tests

Verify correct handling of:

```text
$HOME
$XDG_CONFIG_HOME
$XDG_CACHE_HOME
$XDG_DATA_HOME
```

Do not assume these variables are always explicitly set.

---

# 25. No Personal Path Test

Search core project files for machine-specific paths.

The test should flag hard-coded values such as:

```text
/home/<specific-user>/
```

unless they exist only in test fixtures or documentation examples.

---

# 26. Debian Leakage Test

Search portable directories for commands such as:

```text
apt
apt-get
dpkg
systemctl
```

Review each match.

Platform-specific code should remain in the appropriate adapter.

---

# 27. Shell Script Quality

If shell scripts are used:

* enable suitable error handling;
* quote variables;
* avoid destructive globbing;
* return useful exit codes;
* keep output concise;
* avoid requiring interactive shells unless intended.

Use ShellCheck where practical.

---

# 28. Python or Other Language Tests

If registry tooling is implemented in Python or another language, use the ecosystem's normal test framework.

Tests should live under:

```text
tests/
```

and should run without requiring the full desktop session wherever possible.

---

# 29. Unit vs Integration

Use unit tests for:

* parsing;
* validation;
* role resolution;
* action lookup;
* adapter selection;
* search ranking.

Use integration tests for:

* Niri;
* DMS;
* actual application launch;
* actual wallpaper changes;
* AI provider invocation.

---

# 30. Manual Tests

Some desktop interaction requires manual validation.

Manual tests must be documented rather than assumed.

Use a checklist such as:

```text
[ ] Super+K opens
[ ] Esc closes
[ ] search works
[ ] displayed binding matches active binding
```

---

# 31. Test Records

Implementation-stage manual validation may be recorded under:

```text
docs/implementation/test-results/
```

Do not store transient noisy logs in Git unless useful.

---

# 32. Backup Tests

Before modifying active Niri or shell configuration, verify backup creation.

Also verify restoration once during Phase 1.

A backup that has never been tested is not a complete rollback mechanism.

---

# 33. Rollback Test

At least once before Phase 1 completion:

1. restore previous Niri configuration;
2. verify Niri can start/use it;
3. restore Omivoid configuration.

This proves configuration changes are reversible.

---

# 34. Startup Test

Reboot or restart the desktop session as appropriate and verify:

* Niri starts;
* DMS starts if enabled;
* Omivoid-generated configuration loads;
* no duplicate shell components start;
* shortcuts work.

A system that only works after manual commands is not complete.

---

# 35. Performance Test

Frequent native interactions should feel immediate.

If focus/navigation visibly lags, inspect whether the implementation unnecessarily invokes:

* shell scripts;
* registry loaders;
* subprocess chains;
* IPC round trips.

Native Niri operations should remain native.

---

# 36. Validation Gates

The agent should not progress past major stages if:

* registry validation fails;
* generated configuration is invalid;
* existing desktop functionality is broken;
* rollback is unavailable;
* architecture violations are knowingly unresolved.

---

# 37. Definition of Passing

A feature is considered tested when:

* its intended behaviour works;
* expected failures are handled;
* existing behaviour is not unintentionally broken;
* relevant automated/manual test is recorded;
* configuration remains recoverable.

---

# 38. Final Phase 1 Validation

Before Phase 1 completion, run:

```text
registry validation
automated tests
Niri configuration validation
action catalogue review
DMS validation
theme validation
AI capability validation
platform abstraction review
rollback validation
clean-session/reboot validation
```

No single green test replaces the full integration check.
