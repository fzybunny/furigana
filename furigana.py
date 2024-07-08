#! /usr/bin/env python3

from difflib import SequenceMatcher
import unicodedata

import pykakasi


def make_furigana(original, kana):
	matches = SequenceMatcher(None, original, kana).get_matching_blocks()

	original_idx = 0
	kana_idx = 0

	for match in matches:
		kanji = original[original_idx:match.a]
		furigana = kana[kana_idx:match.b]
		okurigana = original[match.a:match.a + match.size]

		is_katakana = all('KATAKANA' in unicodedata.name(k) for k in kanji)

		if kanji:
			print('{}'.format(kanji), end='')
			if not is_katakana:
				print('({})'.format(furigana), end='')
		if okurigana:
			print('{}'.format(okurigana), end='')

		original_idx = match.a + match.size
		kana_idx = match.b + match.size


def main():
	# Load text
	with open('text.txt') as f:
		text = f.read()

	sections = text.split('\n', 2)
	title = sections[0]
	author = sections[1]
	text = sections[2]

	# Load template
	with open('templates/tate-a6-title.tex') as f:
		template = f.read()

	# Put text in template
	template = template.replace('\\title{}', '\\title{{{}}}'.format(title))
	template = template.replace('\\author{}', '\\author{{{}}}'.format(author))
	template = template.replace('\\end{document}', '{}\n\\end{{document}}'.format(text))

	print(template)

	return;

	kks = pykakasi.kakasi()
	text = '吾輩は猫である。名前はまだ無い。'
#	text = 'キツツキ計画'
	result = kks.convert(text)
	for word in result:
		make_furigana(word['orig'], word['hira'])

	print()


if __name__ == '__main__':
	main()
