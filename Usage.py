from json import load
# from Bible import BibleAddress
from Bible2 import BibleObject

with open("Library & Regex.json") as lar_gen:
    lar = load(lar_gen)

book_prefix_number = lar['book_prefix_number']
book_name = lar['book_name']
book_number = lar['book_number']
chapter = lar['chapter']
versification = lar['versification']
standalone = lar['standalone']
translation_file = lar['translation_data']


# for de-python-ized Regex pattern: print(address_pattern.replace('(?P<', '(?<'))
address_pattern =\
    f'^(?P<book>(?:{book_prefix_number} )?{book_name}|{book_number}(?!\\d)) ' \
    f'(?:{standalone}|(?:{chapter}:)?{versification})$'


while 1:  # Take verse addresses (e.g. John 1:31, Jude 1, James 1:2, 5, 6-5) as input and print
    # address = BibleAddress(
    #     input(), address_pattern, "New King James Version.json", lar['library'], lar['single_chapter_books']
    # )

    address = BibleObject(
        lar, input(), "New King James Version", address_pattern
    )

    for x in address.contents():
        print(x[1])
