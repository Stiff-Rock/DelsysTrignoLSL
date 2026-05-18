from configparser import ConfigParser
import os

_CONFIG_FILE_PATH = "config.ini"
_DEFAULT_CONFIG = {
    "CONNECTION": {"ip": "127.0.0.1", "cmd_port": "50040", "data_port": "50041"},
    "UI": {
        "enable_trigno_module": "False",
        "update_interval": "150",
        "samples_per_page": "5000",
    },
    "DEBUG": {"print_samples": "False", "print_xdf_contents": "False"},
}
_CONFIG: ConfigParser


def load_settings():
    global _CONFIG
    _CONFIG = ConfigParser()
    if not os.path.exists(_CONFIG_FILE_PATH):
        for section, options in _DEFAULT_CONFIG.items():
            _CONFIG[section] = options
        _save_config()
    else:
        _CONFIG.read(_CONFIG_FILE_PATH)
        _validate_and_sanitize_config()


def _validate_and_sanitize_config():
    needs_save = False

    validation_map = [
        ("CONNECTION", "cmd_port", _CONFIG.getint),
        ("CONNECTION", "data_port", _CONFIG.getint),
        ("UI", "enable_trigno_module", _CONFIG.getboolean),
        ("UI", "update_interval", _CONFIG.getint),
        ("UI", "samples_per_page", _CONFIG.getint),
        ("DEBUG", "print_samples", _CONFIG.getboolean),
        ("DEBUG", "print_xdf_contents", _CONFIG.getboolean),
    ]

    for section, option, getter_func in validation_map:
        if not _CONFIG.has_section(section) or not _CONFIG.has_option(section, option):
            if not _CONFIG.has_section(section):
                _CONFIG.add_section(section)
            _CONFIG[section][option] = str(_DEFAULT_CONFIG[section][option])
            needs_save = True
            continue

        try:
            getter_func(section, option)
        except ValueError:
            _CONFIG[section][option] = str(_DEFAULT_CONFIG[section][option])
            needs_save = True

    if needs_save:
        _save_config()


def _save_config():
    with open(_CONFIG_FILE_PATH, "w") as config_file:
        _CONFIG.write(config_file)


def update_settings(
    ip: str,
    cmd_port: str,
    data_port: str,
    enable_trigno_module: str,
    update_interval: str,
    samples_per_page: str,
):
    _CONFIG["CONNECTION"]["ip"] = ip
    _CONFIG["CONNECTION"]["cmd_port"] = cmd_port
    _CONFIG["CONNECTION"]["data_port"] = data_port
    _CONFIG["UI"]["enable_trigno_module"] = enable_trigno_module
    _CONFIG["UI"]["update_interval"] = update_interval
    _CONFIG["UI"]["samples_per_page"] = samples_per_page
    _save_config()


# --- GETTERS ---
def get_ip() -> str:
    return _CONFIG.get("CONNECTION", "ip", fallback="127.0.0.1")


def get_cmd_port() -> int:
    return _CONFIG.getint("CONNECTION", "cmd_port", fallback=50040)


def get_data_port() -> int:
    return _CONFIG.getint("CONNECTION", "data_port", fallback=50041)


def get_enable_trigno_module() -> bool:
    return _CONFIG.getboolean("UI", "enable_trigno_module", fallback=False)


# TODO: DISABLE WITH IF NO TRIGNO MODULE?
def get_update_interval() -> int:
    return _CONFIG.getint("UI", "update_interval", fallback=50)


def get_samples_per_page() -> int:
    return _CONFIG.getint("UI", "samples_per_page", fallback=5000)


def get_print_samples() -> bool:
    return _CONFIG.getboolean("DEBUG", "print_samples", fallback=False)


def get_print_xdf_contents() -> bool:
    return _CONFIG.getboolean("DEBUG", "print_xdf_contents", fallback=False)
