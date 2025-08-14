

class BibleObject:
    from typing import Union
    from re import Pattern

    def __init__(self, library: iter = (), address: str = None, translation: Union[str, int] = None, pattern: str or Pattern = None):
        """
        Numbers are kept as natural numbers (starting at 1) instead of whole numbers (starting at 0).
        This maintains compatibility with SQL and keeps output readily user-friendly.
        It also curbs redundant conversions.
        """
        from re import match
        self.library: dict = library
        self.address: str = address
        self.database_map: str = self.library["translation_data"]
        self.current_database: str = self.resolve_database(translation)
        self.book_no: int
        self.book_name: str
        self.chapter: int
        self.verse: int
        self.verse_books = (31, 57, 63, 64, 65)  # perhaps verse books should be auto-detected :/ ?
        self.verse_extensions: str

        pattern_match = match(pattern, address)
        if pattern_match:
            address_dict = pattern_match.groupdict()
            self.book_no, self.book_name = self.resolve_book(address_dict['book'])

            if address_dict['chapter']:
                self.chapter = int(address_dict['chapter'])
            elif address_dict['standalone']:
                if self.book_no in self.verse_books:
                    self.verse = int(address_dict['standalone'])
                    self.chapter = 0
                else:
                    self.chapter = int(address_dict['standalone'])
            else:
                self.chapter = 1

            if address_dict['verse']:
                self.verse = int(address_dict['verse'])
            else:
                self.verse = None
            if address_dict['verse_extensions']:
                self.verse_extensions = address_dict['verse_extensions']
            else:
                self.verse_extensions = None
        else:
            # make address mismatch error more verbose with logic
            # according to which parts of the regex pattern did not match
            raise ValueError(f"Invalid address '{self.address}' provided.")

    def resolve_translation(self, translation: Union[str, int]) -> tuple[int, str, str]:
        """"""
        from sqlite3 import connect

        translation_query = connect(self.database_map, autocommit=False)
        name_pairs = translation_query.cursor().execute("SELECT id, title, acronym FROM translations ORDER BY id ASC;").fetchall()

        if type(translation) == str:
            for pair in name_pairs:
                if translation == pair[1] or translation == pair[2]:
                    translation_query.close()
                    return pair[0], pair[1], pair[2]
            else:
                translation_query.close()
                raise ValueError(f"No translation maps to the value: {translation}")

        else:
            for pair in name_pairs:
                if translation == pair[0]:
                    translation_query.close()
                    return translation, pair[1], pair[2]
            else:
                translation_query.close()
                raise ValueError(f"No translation maps to the value: {translation}")

    def resolve_database(self, translation):
        from os.path import exists
        assumed_path = self.library["database_directory"] + self.resolve_translation(translation)[1] + '.db'

        if exists(assumed_path):
            return assumed_path
        else:
            raise ValueError(f"Translation '{translation}' file '{assumed_path}' does not exist")

    def resolve_book(self, book_object):
        """"""
        if not book_object.isdecimal():  # excludes valid non-floating decimal strings, handles book name strings
            for position, variants in enumerate(self.library["library"]):
                for variant in variants:
                    if variant.lower().startswith(book_object.lower()):
                        return position + 1, book_object
            else:
                raise ValueError(f"invalid book object '{book_object}' provided")  # will raise for typos
        else:  # handles book numbers
            return int(book_object), self.library["library"][int(book_object)][0]

    def contents(self) -> iter:
        """"""
        from sqlite3 import connect

        with connect(self.current_database, autocommit=False) as bible_query:
            if self.verse is not None:  # handles verse

                if self.verse_extensions:  # handles verse extensions
                    segments = (str(self.verse) + self.verse_extensions).replace(' ', '').split(',')

                    for segment in segments:
                        # distinguish ranges from single verses

                        if '-' in segment: # handles ranges
                            start, end = segment.split('-')

                            range_query = bible_query.cursor().execute(
                                "SELECT verse_text FROM verses "
                                "WHERE (book_id IS ?) AND (chapter IS ?) AND (verse BETWEEN ? AND ?);",
                                (self.book_no, self.chapter, start, end)
                            ).fetchall()

                            for no, verse in enumerate(range_query, start=int(start)):
                                yield no, verse[0]

                        else:  # handles single verses
                            single_verses_query = bible_query.cursor().execute(
                                "SELECT verse_text FROM verses "
                                "WHERE (book_id IS ?) AND (chapter IS ?) AND (verse IS ?);",
                                (self.book_no, self.chapter, segment)
                            ).fetchone()[0]

                            yield int(segment), single_verses_query

                else: # handles normal single verse addresses
                    verse_query = bible_query.cursor().execute(
                        "SELECT verse_text FROM verses "
                        "WHERE (book_id IS ?) AND (chapter IS ?) AND (verse IS ?);",
                        (self.book_no, self.chapter, self.verse)
                    ).fetchone()[0]

                    yield self.verse, verse_query

            else: # handles addresses without verses
                chapter_query = bible_query.cursor().execute(
                    "SELECT verse_text FROM verses WHERE (book_id IS ?) AND (chapter IS ?);",
                    (self.book_no, self.chapter)
                ).fetchall()

                for no, verse in enumerate(chapter_query, start=1):
                    yield no, verse[0]
        bible_query.close()
