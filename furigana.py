#! /usr/bin/env python3

from difflib import SequenceMatcher
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
				# TODO: Properly split readings between characters?
				latex.append('\\ruby[g]{{{}}}{{{}}}'.format(kanji, furigana))
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


def main():
	title, author, text = load_text('text.txt')

	furigana_text = add_latex_furigana(text)

	save_with_template(
		'./out.tex', 'templates/tate-a6-title.tex',
		title, author, furigana_text
	)


if __name__ == '__main__':
	main()
