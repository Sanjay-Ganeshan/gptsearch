from pdfbox import PDFBox

import argparse
import os
import typing as T
from pathlib import Path

def pdf_to_text(pdf: Path, output: T.Optional[Path]) -> Path:
    if output is None:
        output = pdf.parent / ("%s.txt" % (os.path.splitext(pdf.name)[0],))
    
    p = PDFBox()
    p.extract_text(pdf, output)

    return output

def convert_library(pdf_library: Path, txt_library: Path) -> None:
    assert not txt_library.exists() or txt_library.is_dir()
    for each_pdf in pdf_library.glob("**/*.pdf"):
        output = txt_library / each_pdf.relative_to(pdf_library)
        output.parent.mkdir(mode=0b111_101_101, parents=True, exist_ok=True)
        pdf_to_text(each_pdf, output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("library", type=Path)
    parser.add_argument("-o", "--output", type=lambda s: str(Path(s).resolve()), default=None)
    args = parser.parse_args()
    to_convert = args.library.resolve(strict=True)
    print(convert_library(to_convert, args.output))

if __name__ == "__main__":
    main()