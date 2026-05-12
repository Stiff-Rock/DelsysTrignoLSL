from configparser import ConfigParser
import os

_CONFIG_FILE_PATH = "config.ini"
_DEFAULT_CONFIG = {
    "CONNECTION": {"ip": "127.0.0.1", "cmd_port": "50040", "data_port": "50041"},
    "UI": {"update_interval": "150"},
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


def _save_config():
    with open(_CONFIG_FILE_PATH, "w") as config_file:
        _CONFIG.write(config_file)


def update_settings(
    ip: str,
    cmd_port: str,
    data_port: str,
    update_interval: str,
):
    _CONFIG["CONNECTION"]["ip"] = ip
    _CONFIG["CONNECTION"]["cmd_port"] = cmd_port
    _CONFIG["CONNECTION"]["data_port"] = data_port
    _CONFIG["UI"]["update_interval"] = update_interval
    _save_config()


# --- GETTERS ---
def get_ip() -> str:
    return _CONFIG.get("CONNECTION", "ip", fallback="127.0.0.1")


def get_cmd_port() -> int:
    return _CONFIG.getint("CONNECTION", "cmd_port", fallback=50040)


def get_data_port() -> int:
    return _CONFIG.getint("CONNECTION", "data_port", fallback=50041)


def get_update_interval() -> int:
    return _CONFIG.getint("UI", "update_interval", fallback=50)


def get_print_samples() -> bool:
    return _CONFIG.getboolean("DEBUG", "print_samples", fallback=False)


def get_print_xdf_contents() -> bool:
    return _CONFIG.getboolean("DEBUG", "print_xdf_contents", fallback=False)
