# Generate PDFs with furigana
This program takes a Japanese plain text file and generates PDF files with
and without furigana.

## Dependencies
 * MeCab
 * jaconv
 * LuaLaTex
 * TeXLive packages for Japanese

MeCab and jaconv can be installed from`requirements.txt`:
`pip install -r requirements.txt`.


## Usage
```
python ./furigana.py <TEMPLATE> <INPUT>
```

This command creates two PDFs, one with furigana and one without, from a
template TeX file.

It also saves the intermediate TeX files for each. In case any changes,
such as incorrect readings, need to be made, the TeX files can be
recompiled with this command:
```
lualatex <TEX FILE>
```

### Input format
The input plain text file should have the following format:
 * Line 1 contains the title.
 * Line 2 contains the author.
 * Paragraphs are separated with a blank line. Line breaks are permitted
   within paragraphs.

Lines 1 (title) and 2 (author) will be used as arguments to the `\title{}`
and `\author{}` commands in the generated TeX file.

### Templates
The templates are ordinary TeX files. The program will search for the
strings `<<TITLE>>`, `<<AUTHOR>>`, and `<<CONTENT>>` and replace them with
the appropriate strings read from the input plain text file.
