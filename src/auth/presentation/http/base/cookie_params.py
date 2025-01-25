from dataclasses import dataclass
from typing import Literal


@dataclass
class CookieParams:
    secure: bool
    samesite: Literal["strict"] | None = None
