with open('test.txt') as myfile:
	line_count = sum(1 for line in myfile)

print line_count