from django.shortcuts import render, redirect
from django.http import JsonResponse

from maptools.translator import Translator

translator = Translator()

def home(request):
    return render(request, 'home.html')


def translation(request, source_lang, target_lang, translation_input):
    available_languages = ["uk", "ru", "en"]
    if source_lang not in available_languages or target_lang not in available_languages:
        data = {'error': "language not available", "description": f"try one of: {available_languages}"}
    if source_lang == target_lang:
        data = {'error': "languages are the same", "description": "please use two different languages for translation"}
    result = translator.translate(translation_input, source_lang, target_lang)
    print(result)
    translator.save_translation_cache()
    return JsonResponse({'input': translation_input, 'translation': result})