cmd_add = "\\PyDiffAdd"
cmd_del = "\\PyDiffDel"

def impl_cmd_add(style: str) -> str:
    match style.lower():
        case "plain":
            return "#1"
        case "underline":
            return r"\ul{#1}"
        case _:
            raise ValueError(f"unknown addition style {style}")

def impl_cmd_del(style: str) -> str:
    match style.lower():
        case "none":
            return ""
        case "plain":
            return "#1"
        case "strike":
            return r"\st{#1}"
        case "underline":
            return r"\ul{#1}"
        case _:
            raise ValueError(f"unknown deletion style {style}")