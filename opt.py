import pages


def main(text, header=''):
	return pages.main.format(header+text).replace('\n', '').replace('\t', '')
	
	
def err(err, content):
	return main(pages.error.format(err)+content)