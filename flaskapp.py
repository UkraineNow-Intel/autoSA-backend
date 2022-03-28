import json
import os
import configparser
from flask import Flask, render_template

from maptools.translator import Translator

config = configparser.ConfigParser()
config.read("server.config")
print(config["DEFAULT"]["Port"])

DEBUG_MODE = config.getboolean("DEFAULT", "Debug")

template_dir = os.path.abspath('./website/templates/')
app = Flask(__name__, template_folder=template_dir)
app.config["JSON_AS_ASCII"] = False

translator = Translator()


@app.route("/", methods=["GET"])
def index():
    return render_template('./translation.html')


@app.route(
    "/translation/<string:source_lang>/<string:target_lang>/<string:translation_input>",
    methods=["GET"],
)
def translation(source_lang, target_lang, translation_input):
    available_languages = ["uk", "ru", "en"]
    if source_lang not in available_languages or target_lang not in available_languages:
        return json.dumps(
            {
                "error": "language not available",
                "description": f"try one of: {available_languages}",
            },
            ensure_ascii=False,
        )
    if source_lang == target_lang:
        return json.dumps(
            {
                "error": "languages are the same",
                "description": "please use two different languages for translation",
            },
            ensure_ascii=False,
        )
    result = translator.translate(translation_input, source_lang, target_lang)
    print(result)
    translator.save_translation_cache()
    return json.dumps(
        {"input": translation_input, "translation": result}, ensure_ascii=False
    )


if __name__ == "__main__":
    app.run(
        host=config["DEFAULT"]["Host"],
        port=config["DEFAULT"]["Port"],
        debug=DEBUG_MODE,
        use_reloader=DEBUG_MODE,
    )
