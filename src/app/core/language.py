from typing import Optional, List


class Language:
    def __init__(self, name: str, display_name: str):
        self.name = name
        self.display_name = display_name


class LanguageRegistry:
    def __init__(self):
        self.languages_dict_by_name = {}
        self.languages_dict_by_display_name = {}

    def register(self, lang: Language):
        name = lang.name
        display_name = lang.display_name

        if name in self.languages_dict_by_name:
            raise RuntimeError('Language "{}" is already registered'.format(name))
        if display_name in self.languages_dict_by_display_name:
            raise RuntimeError('Language "{}" is already registered'.format(name))

        self.languages_dict_by_name[name] = lang
        self.languages_dict_by_display_name[display_name] = lang

    def get_by_name(self, name: str) -> Optional[Language]:
        return self.languages_dict_by_name.get(name)

    def get_by_display_name(self, name: str) -> Optional[Language]:
        return self.languages_dict_by_display_name.get(name)

    def get_languages_list(self) -> List[Language]:
        l = list(self.languages_dict_by_display_name.values())
        l.sort(key=lambda game: game.display_name)
        return l

    @staticmethod
    def from_languages(languages: List[Language]) -> 'LanguageRegistry':
        r = LanguageRegistry()
        for l in languages:
            r.register(l)
        return r
