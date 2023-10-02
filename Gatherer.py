"""from json import loads, dumps
from re import match
with open("NKJV.json") as nkjv:
    json_dict = loads(u"" + nkjv.read())
    for book in json_dict["books"]:
        with open("Books/%s.json" % book["name"], "w") as sep_book:
            sep_book.write(dumps(book))"""