import argparse


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="pylatexdiff",
        description="Generate a .tex file showing differences between LaTeX documents."
    )

    parser.add_argument("old_tex", nargs="?", help="Path to the original .tex file")
    parser.add_argument("new_tex", nargs="?", help="Path to the revised .tex file")
    parser.add_argument("--old", help="explicitly provide path to the original .tex file")
    parser.add_argument("--new", help="explicitly provide path to the revised .tex file")

    parser.add_argument("-o", "--output", help="Output file path (default: stdout)")

    args = parser.parse_args()
    print(args)


if __name__ == "__main__":
    main()