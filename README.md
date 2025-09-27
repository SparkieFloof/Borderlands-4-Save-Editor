# BL4 Save Editor — v0.5 Rebuild

A desktop editor for Borderlands 4 save files and YAML exports. This fork/rebuild provides a modular PySide6 GUI with improved theming, flexible YAML handling, and tabbed editors for the most commonly edited game sections (items, progression, profile, world, etc.).

This README documents the project's features, how to run it, how the UI is organized, developer notes, and testing instructions.

---

## Highlights / Features

- Modular tabbed UI (PySide6) with the following main tabs:
	- Character — character-specific state and settings
	- Items — Backpack, Equipped, Bank, and Unknown item editors; preserves original item dicts to enable round-trip edits
	- Progression — levels, experience and progression-related data
	- Stats — player statistics
	- World — world state relevant to saves
	- Unlockables — unlock flags and related content
	- Profile — profile-wide data (inputprefs, onlineprefs, UI prefs, domains/shared sections); tolerant to multiple save shapes
	- YAML — raw YAML editor/viewer for advanced users
	- Debug — runtime logs shown in-app for troubleshooting
	- Readme — loads the repository `README.md` into the UI for quick reference

- Theming & styling
	- Dark theme is used by default
	- Settings dialog includes color pickers and controls to generate a custom QSS stylesheet
	- External QSS file support (load/save an external .qss and apply on startup)
	- Additional UI settings for tab spacing and selected-tab color

- Save file support
	- Loads `.yaml` exports and `.sav` files (the latter via the included or external `bl4-crypt-cli` helper)
	- ItemsTab understands multiple YAML shapes (profile-style under `domains.local.shared.inventory.items.bank`, top-level `inventory`, `state.*`, and others). Equipped/lostloot locations are supported.
	- ProfileTab will exclude the `bank` subtree from the profile view (so items are edited only in ItemsTab) to avoid duplication.

- Developer-focused
	- `TabController` centralizes data flow between the in-memory save and tab widgets
	- Settings persisted using the app settings helper in `bl4_editor/core/settings.py`
	- Logging pipes into the Debug tab for easy troubleshooting

---

## Requirements

The project uses Python 3.10+ and PySide6.

Install the minimal dependencies from `requirements.txt`:

run the smart launcher to auto install and then run the app

or

```powershell
python -m pip install -r requirements.txt
```

Requirements file includes:
- PySide6
- PyYAML

---

## Running the app

There are two simple ways to run the editor during development. From the repository root (Windows PowerShell examples):

double click the smart launther

```powershell
# using the provided launcher
python .\smart_launcher.py

# or directly run the package main
python -m bl4_editor.main
```

When opening `.sav` files the app may require a UserID (SteamID64 or 32-byte hex). The toolbar exposes a UserID field which will be persisted for subsequent opens.

If you have `bl4-crypt-cli.exe` in the project root the application will prefer it to decrypt/encrypt `.sav` files; otherwise you can point the app at an alternative binary.

---

## UI & Workflow notes

- Open a `.yaml` or `.sav` via the toolbar `Open` action. The file will be parsed and the various tabs will be populated.
- Tabs accept edits and the controller can merge tab edits back into the in-memory YAML representation before saving.
- `Save as YAML` will export the current merged data. There are protections for atomic writes and backup creation when overwriting files.
- The YAML tab is the authoritative textual representation when the 'YAML priority' setting is selected; otherwise the tab controls take priority and their edits are merged into the saved YAML.

---

## File formats and where items are found

The editor tries to be tolerant to multiple export/save layouts. Examples of locations scanned for items:

- Profile-style bank: `domains.local.shared.inventory.items.bank` or top-level `shared.inventory.items.bank`
- Character-style inventory: `inventory.items.backpack` and `inventory.items.unknown_items`
- Equipped: `state.inventory.equipped_inventory` (preferred), or `equipped_inventory` / `equipped` (fallbacks) (broken)
- Lost loot: `state.lostloot.items` (no tab added)

ItemsTab preserves the original item dictionaries in `_original_items` so editing only updates chosen fields and preserves other details (like serial numbers) for round-tripping.

---

## Development notes

- Code layout (important files):
	- `bl4_editor/main.py` — application entry used in development mode
	- `smart_launcher.py` — convenience launcher that may be used to start the app
	- `bl4_editor/ui/mainwindow.py` — main UI wiring, toolbar, tab registration, and file open/save flows
	- `bl4_editor/ui/tabs/` — contains tab implementations (items_tab.py, profile_tab.py, character_tab.py, etc.)
	- `bl4_editor/core/` — core utilities (controller, settings, fileio, crypt wrapper, logger)
	- `bl4_editor/ui/settings_dialog.py` — UI for theming and runtime settings

- Settings: stored/persisted via `bl4_editor/core/settings.py`. New keys include `qss_path`, UI color keys, and tab spacing options.
- Logging: internal logger prints to the Debug tab when attached by `mainwindow`.

YAML quirk: some `*.yaml` exports may contain custom YAML tags that the PyYAML SafeLoader doesn't accept by default. During development a permissive constructor was used in test utilities. If you run into parse errors, you can preprocess or extend the YAML loader to register safe constructors for those tags.

---

## Tests

There is a `tests/` folder with small targeted tests / scripts. You can run the test suite using pytest (recommended):

```powershell
pip install pytest
pytest -q
```

Temporary test helpers used during development (examples):
- `tests/.tmp_items_tab_test.py` — quick script to validate ItemsTab parsing logic
- `tests/.tmp_readme_test.py` — verify ReadmeTab loads the README

You can add pytest-compatible unit tests under the `tests/` directory to protect parsing/round-trip behavior.

---

## Contributing

Contributions are welcome. A few suggestions to get started:

- Fork the repo and open a branch for your change.
- Keep UI/logic changes small and add tests for parsing or save/load behavior.
- If you change the public data format or settings keys, include upgrade/migration notes.

Please respect the project's license (see `LICENSE`).

---

## Troubleshooting

- If the app fails to open `.sav` files, ensure a valid `bl4-crypt-cli.exe` is available in the project root or adjust the `CryptWrapper` to point to your installer binary.
- Theme/QSS issues: check `qss/example-*.qss` (if present) and the `qss_path` setting in the settings dialog.
- If a save load fails with a YAML tag error, inspect the YAML around the reported line and either remove custom tags for testing or implement a SafeLoader constructor for those tags.

---

## Screenshots / Quick GIF

Add screenshots or a short animated GIF to visually demonstrate the editor. Place images under `docs/screenshots/` (create the directory if it does not exist). Example markdown you can drop into this README or a docs page:

```markdown
![Main window screenshot](docs/screenshots/main-window.png)

![Items tab screenshot](docs/screenshots/items-tab.png)

![Theme settings GIF](docs/screenshots/theme-picker.gif)
```

Notes:
- GIFs are handy to show theme changes, the Settings dialog color picker, or an open/save workflow.
- Keep images under ~1–2 MB to keep the repo manageable; optimize GIFs with tools like gifsicle or convert to MP4 for larger demos and embed via HTML if needed.

---

## Usage examples

Quick commands and examples to run and use the editor from the repository root (Windows PowerShell examples):

1) Install dependencies (one-time):

```powershell
python -m pip install -r requirements.txt
```

2) Start the editor (development):

```powershell
# Prefer the smart launcher which can install missing deps and run
python .\smart_launcher.py

# Or run directly
python -m bl4_editor.main
```

3) Open a YAML or .sav and inspect items (manual):

- Click `Open` in the toolbar and select a `.yaml` or `.sav` file.
- If opening a `.sav` you'll be prompted for a UserID if not already provided. The UserID is saved for future opens.

4) Edit items and save back to YAML:

- Select the `Items` tab, choose the `Bank` or `Equipped` subtabs and edit the flags/notes.
- Use `Save as YAML` from the toolbar to export the current merged data to a YAML file.

5) Generate and test a custom QSS theme:

- Open `Settings` → UI tab. Use color pickers to tune colors and tab spacing.
- Click `Build QSS` or `Save QSS` to write to the external `qss_path` configured in settings.
- Restart the app (or use the Settings apply callback) to load the external QSS on startup.

6) Troubleshooting YAML parse errors (custom tags):

- If PyYAML raises a constructor error for an unknown tag (e.g., `!tags`), you can either remove the tag for testing or extend the YAML loader to handle it. For quick debugging, open the YAML in the `YAML` tab and inspect the offending line reported by the error message.

---

If you want, I can add one or two annotated screenshots and a short GIF showing: opening a file, switching to Items, editing a bank entry, and saving — tell me which scene(s) to capture and I will generate optimized images and embed them into the README.

