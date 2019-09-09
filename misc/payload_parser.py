import re
import sys


# small script to remove comments and multiple newlines from a file
def parse_payload(text):
    text = re.sub('(?s)(<#.+?#>\n)', '', text)
    text = re.sub('#.+?\n', '', text)
    text = re.sub('\n\n', '\n', text)

    return text


if __name__ == "__main__":
    with open(sys.argv[1], 'r') as f:
        print(parse_payload(f.read()))
