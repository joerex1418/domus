from httpx import Response
from rich.console import Console
from rich.theme import Theme
from rich.style import Style


console = Console(
    theme=Theme({
        "json.brace": Style(bold=True),
        "json.key": Style(color="cyan"),
        "json.str": Style(color="bright_magenta"),
        "json.number": Style(color="yellow", bold=True),
        "json.bool_true": Style(color="bright_green", italic=True),
        "json.bool_false": Style(color="bright_red", italic=True),
        "json.null": Style(dim=True, italic=True)
    })
)


class _color:
    __slots__ = tuple()
    def __init__(self) -> None:
        pass
    def bold(self,s: str):
        return f"\033[1m{s}\033[0m"
    
    def dim(self,s: str):
        return f"\033[2m{s}\033[0m"
    
    def underline(self,s: str):
        return f"\033[4m{s}\033[0m"
    
    def italic(self,s: str):
        return f"\033[3m{s}\033[0m"
    
    def yellow(self,s: str):
        return f"\033[93m{s}\033[0m"
    
    def cyan(self,s: str):
        return f"\033[96m{s}\033[0m"
    
    def magenta(self,s: str):
        return f"\033[35m{s}\033[0m"
    
    def bright_magenta(self,s: str):
        return f"\033[95m{s}\033[0m"
    
    def red(self,s: str):
        return f"\033[31m{s}\033[0m"
    
    def bright_red(self,s: str):
        return f"\033[91m{s}\033[0m"
    
    def green(self,s: str):
        return f"\033[92m{s}\033[0m"
    
    def blue(self,s: str):
        return f"\033[34m{s}\033[0m"
    
    def bright_yellow(self,s: str):
        return f"\033[93m{s}\033[0m"


color = _color()


def log_response(r: Response):
    if r.status_code in (401, 403):
        colorize = color.red
    elif r.status_code in (400, 404):
        colorize = color.yellow
    elif r.status_code == 429:
        colorize = color.magenta
    else:
        colorize = color.bold
    
    print("{status_code} {urlhost}{urlpath}".format(
        status_code = colorize(f"[{r.status_code}]"),
        urlhost = color.dim(r.url.scheme + r.url.host),
        urlpath = color.magenta(r.url.path)
    ))

