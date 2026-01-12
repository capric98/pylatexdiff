import chardet

from diff_match_patch import diff_match_patch

from .generate_header import generate_info_header, generate_style_header
from .latex_command import cmd_add, cmd_del
from .latex_parser import LatexParser


def latexdiff(
    fn_old: str, fn_new: str,
    style_add: str,
    style_del: str,
    style_eqn: str,
    style_ref: str,
) -> str:

    with open(fn_old, "rb") as f:
        tex_byte_old = f.read()
        cdt_result = chardet.detect(tex_byte_old)
        tex_old = tex_byte_old.decode(encoding=cdt_result["encoding"])

    with open(fn_new, "rb") as f:
        tex_byte_new = f.read()
        cdt_result = chardet.detect(tex_byte_new)
        tex_new = tex_byte_new.decode(encoding=cdt_result["encoding"])

    dmp = diff_match_patch()
    diffs = dmp.diff_main(tex_old, tex_new)
    dmp.diff_cleanupSemantic(diffs)

    diff_tex = ""
    diff_tex += generate_info_header(fn_old, fn_new)
    diff_tex += generate_style_header(style_add=style_add, style_del=style_del)

    latex_tracker = LatexParser()

    for diff in diffs:
        print(diff)
        diff_type, content = diff
        diff_tex += _wrap_safe(diff, latex_tracker)
        print("-------------------------------------------")

    return diff_tex


def _wrap_safe(diff: tuple[int, str], latex) -> str:
    diff_type, content = diff

    if diff_type == 0:
        latex.parse(content)
        return content

    is_add = diff_type == 1
    cmd = cmd_add if is_add else cmd_del

    wrap_content = ""

    while True:
        environ = latex.environment
        parent  = latex.parent

        if environ in ["document"]:
            if parent.lower() in ["cite", "cref"]:
                wrap_content += cmd + r"{\mbox{" + content + "}}"
            else:
                wrap_content += cmd + "{" + content + "}"
        else:
            if is_add:
                wrap_content += content

        return wrap_content


if __name__ == "__main__":
    pass