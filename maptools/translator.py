import glob
import os
import pickle

from easynmt import EasyNMT


class Translator:
    """ """

    def __init__(self):
        self.model = None
        self.TRANSLATION_CACHE_FILENAME = str(
            os.path.abspath(os.path.abspath(__file__) + "/../translationCache.pickle")
        )
        self.translation_cache = self.get_translation_cache()

    def get_translation_cache(self):
        try:
            translation_cache = pickle.load(open(self.TRANSLATION_CACHE_FILENAME, "rb"))
        except:
            print("New Cache")
            translation_cache = {}
        return translation_cache

    def save_translation_cache(self):
        pickle.dump(self.translation_cache, open(self.TRANSLATION_CACHE_FILENAME, "wb"))

    def translate(self, sentence, source_lang="uk", target_lang="en"):
        # add language entry to translation cache
        if source_lang not in self.translation_cache:
            self.translation_cache[source_lang] = {}
        if target_lang not in self.translation_cache[source_lang]:
            self.translation_cache[source_lang][target_lang] = {}

        # if not in cache, translate
        if sentence not in self.translation_cache[source_lang][target_lang]:
            if not self.model:
                self.model = EasyNMT("opus-mt")
            self.translation_cache[source_lang][target_lang][
                sentence
            ] = self.model.translate(
                sentence, source_lang=source_lang, target_lang=target_lang
            )
        return self.translation_cache[source_lang][target_lang][sentence]


def get_file_with_extensions(type="shp"):
    all_files = glob.glob("./Data/*." + type)
    print("Please choose file you want to analyze:")
    for i, file in enumerate(all_files, 1):
        print(i, file)
    val = 99999
    while val < 1 or val > len(all_files):
        val = int(input("Your Number:"))
    print("You choose:", file)
    return file
