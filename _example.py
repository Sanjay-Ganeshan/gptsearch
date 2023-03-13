from pdfbox import PDFBox
import os
import typing as T
import tempfile
from julielib.speech import TTS
from pydub import AudioSegment
import argparse

def get_example_pdf_path():
    mydir = os.path.abspath(os.path.dirname(__file__))
    example_path = os.path.join(mydir, "Babel.pdf")
    return example_path

def get_example_output_path():
    mydir = os.path.abspath(os.path.dirname(__file__))
    example_path = os.path.join(mydir, "Babel.mp3")
    return example_path

def is_ext_file(path: str, ext: str, exists: T.Optional[bool]=True):
    return (exists is None or os.path.isfile(path) == exists) and path.lower().endswith(f".{ext}")

def is_txt_file(path: str, exists: T.Optional[bool]= True):
    return is_ext_file(path, "txt", exists)

def is_pdf_file(path: str, exists: T.Optional[bool]=True):
    return is_ext_file(path, "pdf", exists)

def get_default_output_path(input_path: str):
    return f"{os.path.splitext(input_path)[0]}.mp3"

def is_wav_file(path: str, exists: T.Optional[bool]=True):
    return is_ext_file(path, "wav", exists)

def is_mp3_file(path: str, exists: T.Optional[bool]=True):
    return is_ext_file(path, "mp3", exists)

def extract_text(pdf_path: str) -> str:
    assert is_pdf_file(pdf_path)
    output_path = tempfile.mktemp(prefix="extractedtext",suffix=".txt")
    pdf = PDFBox()
    print(f"Extracting text to {output_path}")
    pdf.extract_text(input_path=pdf_path, output_path=output_path)
    if os.path.isfile(output_path):
        try:
            with open(output_path, "r") as f:
                contents = f.read()
        except IOError as err:
            raise err
        else:
            print(f"Text extracted. {len(contents)} characters.")
        finally:
            os.remove(output_path)
    else:
        raise IOError(f"Expected text to be written to {output_path}")
    
    return contents

def to_audiobook(contents: str, output_path: str, allow_overwrite=False):
    assert is_mp3_file(output_path, None if allow_overwrite else False), f"{output_path} Not MP3, or already exists"
    tmp_path = tempfile.mktemp(prefix="spokentext",suffix=".wav")
    print(f"Speaking to {tmp_path}")
    with TTS(outfile=tmp_path) as tts:
        tts.say(contents)
    try:
        print(f"Converting WAV to MP3: {tmp_path} -> {output_path}")
        uncompressed = AudioSegment.from_wav(tmp_path)
        uncompressed.export(output_path)
    except Exception as err:
        raise err
    else:
        print(f"Successfully made audiobook: {output_path}")
    finally:
        os.remove(tmp_path)
    return output_path

def pdf_to_audiobook(pdf_path:str, output_path:str, allow_overwrite = False):
    contents = extract_text(pdf_path)
    to_audiobook(contents, output_path, allow_overwrite)

def txt_to_audiobook(txt_path: str, output_path: str, allow_overwrite = False):
    assert is_txt_file(txt_path), f"TXT file doesn't exist: {txt_path}"
    with open(txt_path, "r") as f:
        contents = f.read()
    to_audiobook(contents, output_path, allow_overwrite)


def main():
    parser = argparse.ArgumentParser(description="Converts PDF files to MP3 text-to-speech audio")
    parser.add_argument("input", help="Input PDF or .TXT file")
    parser.add_argument("output", nargs="?", help="Output MP3")
    parser.add_argument("-f", "--force", default=False, action="store_true", help="Overwrite existing files")
    args = parser.parse_args()
    # Validate args
    print(f"INPUT: {args.input}, OUTPUT: {args.output}, FORCE: {args.force}")
    assert is_pdf_file(args.input) or is_txt_file(args.input), "Not a PDF or TXT input file"
    if args.output is None:
        args.output = get_default_output_path(args.input)
    assert is_mp3_file(args.output, exists=None if args.force else False), "Not an MP3, or already exists (-f to force overwrite)"
    if is_txt_file(args.input):
        txt_to_audiobook(args.input, args.output, args.force)
    elif is_pdf_file(args.input):
        pdf_to_audiobook(args.input, args.output, args.force)
    else:
        raise IOError(f"Unexpected input file type, or doesn't exist: {args.input}")

if __name__ == '__main__':
    main()