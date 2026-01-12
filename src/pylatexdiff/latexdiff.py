import re

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

    pending_buffer = ""
    suppress_closing_brace = False

    for diff in diffs:
        print(diff)
        diff_type, content = diff

        if diff_type == 0:
            latex_tracker.parse(content)

            if suppress_closing_brace:
                # We expect the next token to be '}' because we reconstructed the command output.
                # Crudely remove the first '}' found?
                # Or parsing it properly?
                # Simple heuristic: remove first occurrence of '}'
                # This assumes the diff boundary was exactly at the insertion point.
                if "}" in content:
                    content = content.replace("}", "", 1)
                    suppress_closing_brace = False

            pending_buffer += content
            continue

        # Process Add/Del
        # Capture state BEFORE wrapping to match pending_buffer content
        environ = latex_tracker.parent
        buffer_content = latex_tracker.current_buffer

        wrapped = _wrap_safe(diff, latex_tracker)

        # Check if we need to backtrack pending_buffer

        if environ and environ in ["cite", "cref"] and ("\\mbox{\\" + environ) in wrapped:
            # We reconstructed the command.

            # Try to match end of buffer
            # Note: explicit regex might be safer for spacing
            pattern = r"\\" + re.escape(environ) + r"\s*\{\s*" + re.escape(buffer_content) + r"$"
            # print(f"DEBUG: Checking pattern '{pattern}' against pending_buffer '{pending_buffer}'")
            match = re.search(pattern, pending_buffer)

            if match:
                # print("DEBUG: Match found! suppressing prefix.")
                pending_buffer = pending_buffer[:match.start()]
                suppress_closing_brace = True
            else:
                pass # print("DEBUG: No match.")

        diff_tex += pending_buffer
        pending_buffer = ""
        diff_tex += wrapped

        print("-------------------------------------------")

    # Flush remaining buffer
    diff_tex += pending_buffer

    return diff_tex


def _wrap_safe(diff: tuple[int, str], latex) -> str:
    diff_type, content = diff

    if diff_type == 0:
        latex.parse(content)
        return content

    is_add = diff_type == 1
    cmd = cmd_add if is_add else cmd_del

    wrap_content = ""
    remaining = content

    while remaining:
        segment, remaining = latex.parse_next(remaining)
        text = segment.text if segment else ""

        # If segment is None but remaining is not empty (should be caught by regex catch-all),
        # but just in case of weirdness:
        if not text and remaining:
            # Force progress to avoid infinite loop if something goes wrong
            wrap_content += remaining
            break

        parent  = latex.parent
        environ = latex.environment
        buffer  = latex.current_buffer

        if not parent:
            wrap_content += text
        elif environ in ["thebibliography", "equation", "subequations", "align", "align*"]:
            # Skip math environments or others requested
            # We use 'environ' (ancestor) instead of 'parent' (immediate) because we might be inside \sqrt{}
            # User wants "just simply keep the new content".
            # If diff_type == 1 (Add), include it.
            # If diff_type == -1 (Del), ignore it.
            # If diff_type == 0 (Unchanged), include it (but _wrap_safe called only for Add/Del).
            # Wait, _wrap_safe IS ONLY called for Add/Del.
            if is_add:
                wrap_content += text
        elif parent in ["cite", "cref"]:
            # Vulnerable command handling:
            # User request: "\PyDiffAdd{\mbox{\cite{einstein, dirac}}}"\\" + parent + "{" + buffer + "}}}"
            wrap_content += cmd + r"{\mbox{" + "\\" + parent + "{" + buffer + "}}}"
        else:
            # Standard wrapping
            wrap_content += cmd + "{" + text + "}"

    return wrap_content


if __name__ == "__main__":
    pass