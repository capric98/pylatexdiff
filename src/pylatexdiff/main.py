import argparse
import sys

from .latexdiff import latexdiff


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="pylatexdiff",
        description="Generate a .tex file showing differences between LaTeX documents."
    )

    parser.add_argument("old_tex", nargs="?", help="Path to the original .tex file")
    parser.add_argument("new_tex", nargs="?", help="Path to the revised .tex file")
    parser.add_argument("--old", help="explicitly provide path to the original .tex file")
    parser.add_argument("--new", help="explicitly provide path to the revised .tex file")

    parser.add_argument(
        "--add",
        dest="style_add",
        choices=["none", "underline"],
        default="underline",
        help="Style for added text (default: underline)",
    )
    parser.add_argument(
        "--del",
        dest="style_del",
        choices=["none", "underline"],
        default="none",
        help="Style for deleted text (default: none)",
    )

    parser.add_argument("-o", "--output", help="Output file path (default: stdout)")

    args = parser.parse_args()
    # print(args)

    diff_tex = latexdiff(
        fn_old=args.old or args.old_tex,
        fn_new=args.new or args.new_tex,
        style_add=args.style_add,
        style_del=args.style_del,
        style_eqn="none", # not implemented
        style_ref="none", # not implemented
    )

    f_output = sys.stdout if not args.output else open(args.output, "w", encoding="utf-8")

    # print(diff_tex, file=f_output, end=None, flush=True)

    if args.output: f_output.close()


if __name__ == "__main__":
    main()