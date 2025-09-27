import json, os
SETTINGS_FILE = os.path.join(os.getcwd(), "settings.json")
_defaults = {
    "backup_on_save": True,
    "log_retention_minutes": 10,
    "last_userid": "",
    "yaml_as_source": False,
    # UI/theme settings
    "ui_theme": "Dark",  # one of: Light, Dark, System (default changed to Dark)
    "custom_stylesheet": "",  # user-provided Qt stylesheet (applied on startup)
    # optional external QSS file path (relative to cwd)
    "qss_path": "app_custom.qss",
    # UI color customizations persisted here
    "ui_hover_color": "#3a3a3a",
    "ui_tab_color": "#2b2b2b",
    "ui_text_color": "#e6e6e6",
    "ui_toolbar_color": "#272727"
    ,
    # Tab presentation
    "ui_tab_spacing": 6,
    "ui_selected_tab_color": "#3d7bd9"
}
def _ensure_loaded():
    global _settings
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                _settings = json.load(f)
        else:
            _settings = {}
    except Exception:
        _settings = {}
    for k,v in _defaults.items():
        if k not in _settings:
            _settings[k] = v
def save_settings():
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(_settings, f, indent=2)
    except Exception:
        pass
def get_setting(key, default=None):
    try:
        return _settings.get(key, default if default is not None else _defaults.get(key))
    except NameError:
        _ensure_loaded()
        return _settings.get(key, default if default is not None else _defaults.get(key))
def set_setting(key, value):
    try:
        _settings[key] = value
    except NameError:
        _ensure_loaded()
        _settings[key] = value
    save_settings()
_ensure_loaded()
