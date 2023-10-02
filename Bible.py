

class BibleFile:
    keying_template = ['books', 0, 'chapters', 0, 'verses', 0, 'text']

    def __init__(self, file_path: str or bytes = None, library: iter = (), verse_books: iter = None):
        self.file_path = file_path
        self.library = library
        self.verse_books = verse_books
        self.verify()

    def verify(self):
        bible_json = self.open_bible()
        mutate_template = list(self.keying_template)

        for book_no in range(len(self.library)):
            mutate_template[1] = book_no
            self.recursive_keying(bible_json, mutate_template)

            if book_no in self.verse_books:
                if len(self.recursive_keying(bible_json, mutate_template[0:3])) != 1:
                    raise IndexError(
                        f'"{self.file_path}" book index "{book_no}" is not '
                        f'single chaptered as asserted: {self.verse_books=}'
                    )

    def open_bible(self):
        from json import load
        with open(self.file_path) as bible_gen:
            return load(bible_gen)

    def recursive_keying(self, json, address_keys, index=0):
        current_key = address_keys[index]
        if index == len(address_keys) - 1:
            return json[current_key]
        else:
            return self.recursive_keying(json[current_key], address_keys, index+1)


class BibleAddress(BibleFile):
    from re import Pattern

    def __init__(self, address: str = None, pattern: str or Pattern = None, *args):
        """
        :type address: str
        """
        from re import match
        super().__init__(*args)

        self.address = address
        self.book_no = None
        self.book = None
        self.chapter = None
        self.verse = None
        self.verse_extensions = None
        addr_dict = match(pattern, address).groupdict()

        if addr_dict:
            self.resolve_book(addr_dict['book'])

            if addr_dict['chapter']:
                self.chapter = int(addr_dict['chapter']) - 1
            elif addr_dict['standalone']:
                self.resolve_standalone(int(addr_dict['standalone']) - 1)
            else:
                self.chapter = 0

            if addr_dict['verse']:
                self.verse = int(addr_dict['verse']) - 1
            if addr_dict['verse_extensions']:
                self.verse_extensions = addr_dict['verse_extensions']
        else:
            raise ValueError(f"invalid address '{self.address}' provided ")

    def resolve_book(self, book_object):
        """"""
        if not book_object.isdecimal():
            for position, variants in enumerate(self.library):
                for variant in variants:
                    if variant.lower().startswith(book_object.lower()):
                        self.book_no = position
                        self.book = book_object
                        break
        else:
            self.book_no = int(book_object) - 1
            self.book = self.library[self.book_no][0]

        if not self.book and not self.book_no:
            raise ValueError(f"invalid book object '{book_object}' provided")  # will raise for typos

    def resolve_standalone(self, standalone):
        """"""
        if self.book_no in self.verse_books:
            self.verse = standalone
            self.chapter = 0
        else:
            self.chapter = standalone

    def contents(self):
        indices = [segment_key for segment_key in (self.book_no, self.chapter, self.verse) if segment_key is not None]
        key_path = []

        for key in self.keying_template:
            if type(key) == str:
                key_path.append(key)
            else:
                if indices:
                    key_path.append(indices.pop(0))
                else:
                    break

        bible_json = self.open_bible()
        if self.verse is not None:

            if self.verse_extensions:
                segments = (str(self.verse + 1) + self.verse_extensions).replace(' ', '').split(',')
                chapter = self.recursive_keying(bible_json, key_path[0:-2])

                for segment in segments:
                    if '-' in segment:
                        start, end = segment.split('-')
                        for verse in chapter[int(start) - 1:int(end)]:
                            yield verse['text']
                    else:
                        yield chapter[int(segment) - 1]['text']
            else:
                yield self.recursive_keying(bible_json, key_path)
        else:
            chapter = self.recursive_keying(bible_json, key_path)

            for verse in chapter:
                yield verse['text']
