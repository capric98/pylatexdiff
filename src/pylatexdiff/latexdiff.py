import chardet

from diff_match_patch import diff_match_patch

from .generate_header import generate_info_header, generate_style_header
from .latex_command import cmd_add, cmd_del


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

    for diff in diffs:
        diff_type, content = diff
        match diff_type:
            case 0:
                diff_tex += content
            case 1:
                diff_tex += cmd_add + "{" + content + "}"
            case -1:
                diff_tex += cmd_del + "{" + content + "}"
            case _:
                raise ValueError(f"unknown diff type: {diff_type}")

    return diff_tex


if __name__ == "__main__":
    pass