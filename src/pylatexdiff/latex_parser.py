import re
from dataclasses import dataclass


@dataclass
class Segment:
    text: str
    hierarchy: list[str]


@dataclass
class Context:
    type: str  # "Environment", "CommandArg", "Group"
    name: str = None  # e.g. "equation", "section", or None for Group
    buffer: str = ""

    def __str__(self):
        if self.type == "Group":
            return "Group"
        if self.name:
            return f"{self.type}({self.name})"
        return self.type


class LatexParser:
    def __init__(self) -> None:
        self.stack: list[Context] = []
        self.pending_command: str = None
        # Added (.) as a catch-all group to prevent infinite loops on invalid syntax (e.g. trailing backslash)
        self.token_pattern = re.compile(r"\\([a-zA-Z@*]+)|([{}])|([^\\{}]+)|(.)", re.DOTALL)

    def parse_next(self, content: str) -> tuple[Segment | None, str]:
        if not content:
            return None, ""

        match = self.token_pattern.match(content)
        if not match:
            # Should not happen as final group catches everything
            return None, content

        text = match.group(0)
        cmd_name = match.group(1)
        brace = match.group(2)
        other = match.group(3)
        catch_all = match.group(4)

        current_hierarchy = [str(ctx) for ctx in self.stack]
        segment = Segment(text, current_hierarchy)

        # Update State Logic
        if self.stack:
            ctx = self.stack[-1]
            if ctx.type == "CommandArg" and ctx.name in ("begin", "end"):
                ctx.buffer += text

        if cmd_name:
            self.pending_command = cmd_name

        elif brace == "{":
            if self.pending_command:
                new_ctx = Context("CommandArg", self.pending_command)
                self.pending_command = None
            else:
                new_ctx = Context("Group")
            self.stack.append(new_ctx)

        elif brace == "}":
            if not self.stack:
                raise ValueError("Unmatched '}' encountered")

            ctx = self.stack.pop()

            # Check for environment transitions
            if ctx.type == "CommandArg":
                if ctx.name == "begin":
                    # The buffer includes the "{" and "text" and "}".
                    env_name = ctx.buffer[:-1].strip()
                    self.stack.append(Context("Environment", env_name))

                elif ctx.name == "end":
                    env_name = ctx.buffer[:-1].strip()

                    if not self.stack:
                        raise ValueError(f"Extra \\end{{{env_name}}}")

                    top = self.stack[-1]
                    if top.type != "Environment" or top.name != env_name:
                        raise ValueError(f"Environment mismatch: expected \\end{{{top.name if top.type=='Environment' else '?'}}}, got \\end{{{env_name}}}")

                    self.stack.pop()

            self.pending_command = None

        elif other or catch_all:
            # Handling "space after command consumes command"
            content_text = other if other else catch_all
            if self.pending_command:
                if self.pending_command in ("begin", "end"):
                    if not content_text.strip():
                        # whitespace, allow.
                        pass
                    else:
                        raise ValueError(f"Command \\{self.pending_command} missing argument")
                else:
                    # Other commands (e.g. \item) without braces are done.
                    self.pending_command = None

        return segment, content[match.end():]

    def reset(self) -> None:
        self.stack = []
        self.pending_command = None

    def parse(self, content: str) -> None:
        remaining = content
        while remaining:
            segment, remaining = self.parse_next(remaining)
            # print(segment, remaining)

            if not remaining and not segment:
                break

        print(self.current_hierarchies)

    @property
    def current_hierarchies(self) -> list[str]:
        return [str(ctx) for ctx in self.stack]

    @property
    def current_environment(self) -> str:
        if not self.pending_command:
            for stack in reversed(self.stack):
                if stack.type == "Environment":
                    return stack.name

        return ""


if __name__ == "__main__":
    pass