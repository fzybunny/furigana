#! /usr/bin/env python3

import argparse
from difflib import SequenceMatcher
import os
import subprocess
import unicodedata

import pykakasi


def add_latex_furigana_word(original, kana):
	'''Generate LaTeX to show furigana on a word, given its reading.
	'''
	matches = SequenceMatcher(None, original, kana).get_matching_blocks()

	original_idx = 0
	kana_idx = 0

	latex = []

	for match in matches:
		kanji = original[original_idx:match.a]
		furigana = kana[kana_idx:match.b]
		okurigana = original[match.a:match.a + match.size]

		is_kanji = all('CJK' in unicodedata.name(k) for k in kanji)

		if kanji:
			if is_kanji:
				latex.append('\\ruby{{{}}}{{{}}}'.format(kanji, furigana))
			else:
				latex.append(kanji)
		if okurigana:
			latex.append(okurigana)

		original_idx = match.a + match.size
		kana_idx = match.b + match.size

	return ''.join(latex)


def add_latex_furigana(text):
	'''Add furigana to every kanji in a string.
	'''
	kks_result = iter(pykakasi.kakasi().convert(text))
	furigana_words = []

	for word in kks_result:
		# There's a bug in kakasi where control characters
		# cause it to duplicate the previous output.
		if unicodedata.category(word['orig'][0])[0] == 'C':
			furigana_words.append(word['orig'])
			next(kks_result)
		else:
			furigana_words.append(add_latex_furigana_word(word['orig'], word['hira']))

	return ''.join(furigana_words)


def fix_quotes_indent(text):
	'''Make sure that quotes that are in their own paragraph aren't indented
	'''

	text = text.replace('\n\n「', '\n\n{\\hackyquoteindent\n「')
	return text.replace('」\n\n', '」\n}\n\n')


def load_text(path):
	with open(path) as f:
		text = f.read()
	return tuple(text.split('\n', 2)) # (title, author, text)


def save_with_template(out_path, template_path, title, author, content):
	with open(template_path) as f:
		template = f.read()

	template = template.replace('<<TITLE>>', title)
	template = template.replace('<<AUTHOR>>', author)
	template = template.replace('<<CONTENT>>', content)

	with open(out_path, 'w') as f:
		f.write(template)


def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'template', type=str, help='Path of LaTeX document template'
	)
	parser.add_argument(
		'input', type=str, help='Path of document text file'
	)

	return parser.parse_args()


def main():
	args = parse_args()

	title, author, text = load_text(args.input)

	furigana_text = add_latex_furigana(text)

	furigana_text = fix_quotes_indent(furigana_text)
	text = fix_quotes_indent(text)

	# No furigana
	no_furigana_fname = os.path.splitext(args.input)[0] + '.tex'
	save_with_template(no_furigana_fname, args.template, title, author, text)
	# With furigana
	furigana_fname = os.path.splitext(args.input)[0] + '-furigana.tex'
	save_with_template(furigana_fname, args.template, title, author, furigana_text)

	subprocess.run(['lualatex', no_furigana_fname])
	subprocess.run(['lualatex', furigana_fname])


if __name__ == '__main__':
	main()
