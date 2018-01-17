# -*- coding: utf-8 -*-
import glob, os, sys
import urllib
import requests
import codecs

def main():
	# input api key
	with open('yandex.key') as api_file:
		yandex_key = api_file.read()

	yandex_url = 'https://translate.yandex.net/api/v1.5/tr.json'

	#TODO:prompt for directory
	directory = 'inputs'

	os.chdir(directory)
	output_dir = '../%s-en' % directory
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)

	limit_reached = False
	# for file in directory
	for file in glob.glob('*.txt'):
		# get text in file
		with codecs.open(file, 'r', 'utf-8') as input_file:
			input_lines = [line.rstrip('\n') for line in input_file]

		err_not_fully_translated = False
		output_lines = []

		# translate all batches/ file to English
		for line in input_lines:
			response = yandex_translate(line, yandex_key, yandex_url)
			if response[0]:
				output_lines.append(response[1][0])
			elif response[1] == 404:
				limit_reached = True
				break
			elif response[1] == 422:
				output_lines.append(text)
				err_not_fully_translated = True
			#TODO: else:

		# write file to new file output
		filename = os.path.splitext(file)[0]
		output_file = codecs.open("%s/%s.txt" % (output_dir, filename), 'w', 'utf8')
		for line in output_lines:
			output_file.write("%s\n" % line)

		if err_not_fully_translated:
			print "%s has sections left in original language due to translation errors" % file

		if limit_reached:
			print "%s could not be fully translated due to hitting daily/monthly limit" % file
			break

# make text safe to send through API request
def encode_text(text):
	return urllib.quote_plus(text.encode('utf8'))

def decode_text(text):
	return urllib.unquote_plus(txt)

# function for each API call used
def yandex_detect_lang(text, key, url, hint='fr,es'):
	txt = encode_text(text)

	request = '%s/detect?key=%s&text=%s&[hint=%s]' % (url, key, txt, hint)
	r = requests.get(request)
	if r.status_code == 200: # success
		return r.json()['lang']
	elif r.status_code == 401: #invalid api key
		print "ERROR: INVALID API KEY"
		return 
	elif r.status_code == 402: #blocked api key
		print "ERROR: BLOCKED API KEY"
	elif r.status_code == 404: #exceeded daily limit
		print "ERROR: EXCEEDED DAILY LIMIT OF FREE TRANSLATIONS"
	return None

def yandex_translate(text, key, url, lang='en'):
	lang = 'en'
	txt = encode_text(text)

	# TODO: check length of txt, and split somewhere logical if too long (10k chars?)
	request = '%s/translate?key=%s&text=%s&lang=%s' % (url, key, txt, lang)
	r = requests.get(request)
	if r.status_code == 200: # success
		return [True, r.json()['text']]
	elif r.status_code == 401: #invalid api key
		print "ERROR: INVALID API KEY"
		return [False, 401]
	elif r.status_code == 402: #blocked api key
		print "ERROR: BLOCKED API KEY"
		return [False, 402]
	elif r.status_code == 404: #exceeded daily limit
		print "ERROR: EXCEEDED DAILY LIMIT OF FREE TRANSLATIONS"
		return [False, 404]
	elif r.status_code == 413: #exceeded maximum text size
		print "ERROR: Paragraph exceeded max length (was %d)" % len(txt)
		return [False, 413]
	elif r.status_code == 422: #text could not be translated
		return [False, 422, text]
	return [False, r.status_code]


if __name__ == '__main__':
	main()