import unicodedata

def remove_diacritical(text):
    " Removes diacritical from text. "
    line = unicode(text, 'utf-8')
    line = unicodedata.normalize('NFKD', line)

    output = ''
    for c in line:
        if not unicodedata.combining(c):
            output += c
    return output
