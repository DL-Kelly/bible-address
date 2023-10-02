from json import load
from Bible import BibleAddress

with open("Library & Regex.json") as lar_gen:
    lar = load(lar_gen)

book_prefix_number = lar['book_prefix_number']
book_name = lar['book_name']
book_number = lar['book_number']
chapter = lar['chapter']
versification = lar['versification']
standalone = lar['standalone']

# for de-python-ized Regex pattern: print(address_pattern.replace('(?P<', '(?<'))
address_pattern =\
    f'^(?P<book>(?:{book_prefix_number} )?{book_name}|{book_number}(?!\\d)) ' \
    f'(?:{standalone}|(?:{chapter}:)?{versification})$'

while 1:
    address = BibleAddress(input(), address_pattern, "New Kings James Version.json",
                           lar['library'], lar['single_chapter_books'])
    for y, x in enumerate(address.contents()):
        print(x)
