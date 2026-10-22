from dataclasses import dataclass
from typing import Literal

SameSite = Literal["lax", "strict", "none"]


@dataclass(frozen=True)
class CookieParams:
    max_age: int
    name: str = "__Host-session"
    secure: bool = True
    httponly: bool = True
    samesite: SameSite = "lax"
    path: str = "/"
