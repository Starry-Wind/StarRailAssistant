# noinspection PyUnresolvedReferences
from prompt_toolkit.styles import Style
from prompt_toolkit.validation import ValidationError
from prompt_toolkit.validation import Validator

from .version import __version__
from .form import Form
from .form import FormField
from .form import form
from .prompt import prompt
from .prompt import unsafe_prompt

# import the shortcuts to create single question prompts
from .prompts.autocomplete import autocomplete
from .prompts.checkbox import checkbox
from .prompts.common import Choice
from .prompts.common import Separator
from .prompts.common import print_formatted_text as print
from .prompts.confirm import confirm
from .prompts.password import password
from .prompts.path import path
from .prompts.press_any_key_to_continue import press_any_key_to_continue
from .prompts.rawselect import rawselect
from .prompts.select import select
from .prompts.text import text
from .question import Question

__all__ = [
    "__version__",
    # question types
    "autocomplete",
    "checkbox",
    "confirm",
    "password",
    "path",
    "press_any_key_to_continue",
    "rawselect",
    "select",
    "text",
    # utility methods
    "print",
    "form",
    "prompt",
    "unsafe_prompt",
    # commonly used classes
    "Form",
    "FormField",
    "Question",
    "Choice",
    "Style",
    "Separator",
    "Validator",
    "ValidationError",
]
