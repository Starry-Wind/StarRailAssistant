from . import autocomplete
from . import checkbox
from . import confirm
from . import password
from . import path
from . import press_any_key_to_continue
from . import rawselect
from . import select
from . import text

AVAILABLE_PROMPTS = {
    "autocomplete": autocomplete.autocomplete,
    "confirm": confirm.confirm,
    "text": text.text,
    "select": select.select,
    "rawselect": rawselect.rawselect,
    "password": password.password,
    "checkbox": checkbox.checkbox,
    "path": path.path,
    "press_any_key_to_continue": press_any_key_to_continue.press_any_key_to_continue,
    # backwards compatible names
    "list": select.select,
    "rawlist": rawselect.rawselect,
    "input": text.text,
}


def prompt_by_name(name):
    return AVAILABLE_PROMPTS.get(name)
