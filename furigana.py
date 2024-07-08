#! /usr/bin/env python3

from difflib import SequenceMatcher
import unicodedata

import pykakasi


def make_furigana_latex(original, kana):
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


def main():
	# Load text
	with open('text.txt') as f:
		text = f.read()

	sections = text.split('\n', 2)
	title = sections[0]
	author = sections[1]
	text = sections[2]

	# Add furigana
	kks_result = iter(pykakasi.kakasi().convert(text))
	furigana_words = []
	for word in kks_result:
		# There's a bug in kakasi where control characters
		# cause it to duplicate the previous output.
		if unicodedata.category(word['orig'][0])[0] == 'C':
			furigana_words.append(word['orig'])
			next(kks_result)
		else:
			furigana_words.append(make_furigana_latex(word['orig'], word['hira']))
	furigana_text = ''.join(furigana_words)

	# Load template
	with open('templates/tate-a6-title.tex') as f:
		template = f.read()

	# Put text in template
	template = template.replace('\\title{}', '\\title{{{}}}'.format(title))
	template = template.replace('\\author{}', '\\author{{{}}}'.format(author))
	template = template.replace('\\end{document}', '{}\n\\end{{document}}'.format(furigana_text))

	print(template)


if __name__ == '__main__':
	main()
