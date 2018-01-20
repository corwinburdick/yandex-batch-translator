# -*- coding: utf-8 -*-
import glob, os, sys
import urllib
import requests
import codecs

def main():
	encoding = 'latin-1' #works with french
	# encoding = 'utf-8' #works with spanish

	# input api key
	(api_base_url, api_key, max_chars_per_request) = load_api_data('yandex')

	directory = select_directory(True)
	os.chdir(directory)
	parent_dir = os.path.abspath(os.path.join(directory, os.pardir))
	output_folder_name = os.path.basename(directory) + "-en"
	output_dir = os.path.abspath(os.path.join(parent_dir, output_folder_name))
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)

	limit_reached = False
	# for file in directory
	for file in glob.glob('*.txt'):
		# get text in file
		with codecs.open(file, 'r', encoding) as input_file:
			input_lines = [line.rstrip('\n') for line in input_file]

		err_not_fully_translated = False
		output_filepath = os.path.abspath(os.path.join(output_dir, file))
		output_file = codecs.open(output_filepath, 'w', encoding)
		
		# translate all batches/ file to English
		# for i, line in enumerate(input_lines):
			# skip lines with only whitespace
			# if len(line.trim()) == 0:
			# 	output_file.write("%s\r\n" % text)
			# 	continue
		
		nline = 0
		while nline < len(input_lines):
			text_to_send = ''
			while len(text_to_send) + len(input_lines[nline]) < max_chars_per_request:
				text_to_send += input_lines[nline] + '\n'
				nline += 1
			response = yandex_translate(text_to_send, api_key, api_base_url, encoding, lang='fr-en')
			if response[0]:
				# write file to new file output
				output_file.write("%s\r\n" % response[1][0])
			elif response[1] == 404:
				limit_reached = True
				break
			elif response[1] == 422:
				output_file.write("%s\r\n" % text_to_send)
				err_not_fully_translated = True
			#TODO: else:
			display_progress_bar(file, nline, len(input_lines))
			nline += 1

		if err_not_fully_translated:
			print "%s has sections left in original language due to translation errors" % file

		if limit_reached:
			print "%s could not be fully translated due to hitting daily/monthly limit" % file
			print "Process halted due to API daily/monthly character limit being reached"
			break

def load_api_data(api='yandex'):
	if api == 'yandex':
		api_base_url = 'https://translate.yandex.net/api/v1.5/tr.json'
		max_chars_per_request = 10000

		with open('yandex.key') as api_file:
			api_key = api_file.read()

		return (api_base_url, api_key, max_chars_per_request)
	else:
		print "ERROR: Unknown API: %s" % api
		sys.exit(0)

def select_directory(default=False):
	if default:
		return 'E:/Corwin/Coding/GitHub/yandex-batch-translator/inputs'
	import tkinter, tkFileDialog

	root = tkinter.Tk()
	root.withdraw()

	file_path = tkFileDialog.askdirectory()
	return file_path

# make text safe to send through API request
def encode_text(text, encoding):
	if encoding == 'utf-8':
		return urllib.quote_plus(text.encode('utf-8'))
	elif encoding == 'latin-1':
		return urllib.quote_plus(text.encode('latin-1'))
	else:
		return urllib.quote_plus(text)

def decode_text(text):
	return urllib.unquote_plus(txt)

# function for each API call used
def yandex_detect_lang(text, key, url, encoding, hint='fr,es'):
	txt = encode_text(text, encoding)

	request = '%s/detect?key=%s&text=%s&[hint=%s]' % (url, key, txt, hint)
	r = requests.get(request)
	if r.status_code == 200: # success
		return r.json()['lang']
	else:
		r.status_code
	if r.status_code == 401: #invalid api key
		print "ERROR: INVALID API KEY"
		return 
	elif r.status_code == 402: #blocked api key
		print "ERROR: BLOCKED API KEY"
		return
	elif r.status_code == 404: #exceeded daily limit
		print "ERROR: EXCEEDED DAILY LIMIT OF FREE TRANSLATIONS"
		return
	return None

def yandex_translate(text, key, url, encoding, lang='en'):
	txt = encode_text(text, encoding)

	# TODO: check length of txt, and split somewhere logical if too long (10k chars?)
	request = '%s/translate?key=%s&text=%s&lang=%s' % (url, key, txt, lang)
	r = requests.get(request)
	print r.json()
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

def display_progress_bar(filename, progress, total):
	percent = int(float(progress)/total * 100)
	print '\r[{0}] {1}/{2}'.format('#'*(percent/10) + '-'*(10-(percent/10)), progress, total),

if __name__ == '__main__':
	main()