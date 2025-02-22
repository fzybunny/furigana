#! /usr/bin/env python3

import argparse
from difflib import SequenceMatcher
import os
import shutil
import subprocess
import tempfile
import unicodedata

import MeCab

import jaconv


def add_latex_furigana_word(original, kana):
	'''Generate LaTeX to show furigana on a word, given its reading.
	'''

	# SequenceMatcher has trouble when both the kanji reading and okurigana use
	# the same kana. Going in reverse seems to avoid that.
	reverse = slice(None, None, -1)
	original_r = original[reverse]
	kana_r = kana[reverse]

	matches = SequenceMatcher(None, original_r, kana_r).get_matching_blocks()

	original_idx = 0
	kana_idx = 0

	latex = []

	for match in matches:
		okurigana_r = original_r[match.a:match.a + match.size]
		furigana_r = kana_r[kana_idx:match.b]
		kanji_r = original_r[original_idx:match.a]

		is_kanji = all('CJK' in unicodedata.name(k) for k in kanji_r)

		if kanji_r:
			if is_kanji:
				latex.append(
					'\\ruby{{{}}}{{{}}}'.format(kanji_r[reverse], furigana_r[reverse])
				)
			else:
				latex.append(kanji_r[reverse])
		if okurigana_r:
			latex.append(okurigana_r[reverse])

		original_idx = match.a + match.size
		kana_idx = match.b + match.size


	return ''.join(reversed(latex))


def mecab_convert(mecab, text):
	'''Get kanji readings in the same format as kakasi.
	'''

	words = []

	for word in mecab.parse(text).split('\n'):
		if word == 'EOS':
			break
		orig, kata, _, _, _, _ = tuple(word.split('\t'))
		words.append({'orig': orig, 'hira': jaconv.kata2hira(kata)})

	return words


def add_latex_furigana(text):
	'''Add furigana to every kanji in a string.

		Paragraphs are separated by '\n\n', and may span multiple lines
	'''

	m = MeCab.Tagger('-O chasen')

	paragraph_delim = '\n\n'
	return paragraph_delim.join(
		''.join(
			add_latex_furigana_word(word['orig'], word['hira'])
			for word in mecab_convert(m, paragraph.replace('\n', ''))
		)
		for paragraph in text.split(paragraph_delim)
	)


def fix_quotes_indent(text):
	'''Make sure that quotes that are in their own paragraph aren't indented
	'''

	# 〈〉
	text = text.replace('\n\n〈', '\n\n{\\hackyquoteindent\n〈')
	text = text.replace('〉\n\n', '〉\n}\n\n')

	# 「」
	text = text.replace('\n\n「', '\n\n{\\hackyquoteindent\n「')
	return text.replace('」\n\n', '」\n}\n\n')


def load_text(path):
	with open(path) as f:
		text = f.read()
	return tuple(text.split('\n', 2)) # (title, author, text)


def save_latex_with_template(out_path, template_path, title, author, content):
	with open(template_path) as f:
		template = f.read()

	template = template.replace('<<TITLE>>', title)
	template = template.replace('<<AUTHOR>>', author)
	template = template.replace('<<CONTENT>>', content)

	with open(out_path, 'w') as f:
		f.write(template)


def compile_latex(src_path):
	'''Compile a LaTeX source file to a PDF
	'''

	with tempfile.TemporaryDirectory() as build_dir:
		shutil.copy(src_path, build_dir)
		subprocess.run(
			['lualatex', os.path.basename(src_path)],
			cwd=build_dir
		)
		pdf_name = os.path.splitext(src_path)[0] + '.pdf'
		shutil.copy('{}/{}'.format(build_dir, pdf_name), os.getcwd())


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
	save_latex_with_template(no_furigana_fname, args.template, title, author, text)
	# With furigana
	furigana_fname = os.path.splitext(args.input)[0] + '-furigana.tex'
	save_latex_with_template(furigana_fname, args.template, title, author, furigana_text)

	compile_latex(no_furigana_fname)
	compile_latex(furigana_fname)


if __name__ == '__main__':
	main()
