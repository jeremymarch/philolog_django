import json

import requests
from django.http import JsonResponse
from django.shortcuts import render

from .models import Word

# def error404(request, exception):
#     return HttpResponseRedirect("/")


def get_lex_db_name(short_lex_name):
    """Return the lexicon name used in the database for the name used in the client.

    The database name comes from the naming conventions used in the git repos.
    """
    lex = ""
    if short_lex_name == "lsj":
        lex = "greatscott"
    elif short_lex_name == "ls":
        lex = "latindico"
    elif short_lex_name == "slater":
        lex = "pindar_dico"
    return lex


def query_words(word_prefix, lex, page, page_size):
    """Returns a tuple of the selected word_id and the list of words."""
    before_words = []
    after_words = []

    if page <= 0:
        before_words = Word.objects.filter(
            sort_key__lt=word_prefix, lexicon=lex
        ).order_by("-sort_key", "word_id")[0:page_size]
    if page >= 0:
        after_words = Word.objects.filter(
            sort_key__gte=word_prefix, lexicon=lex
        ).order_by("sort_key", "word_id")[0:page_size]

    words = []
    for w in before_words:
        if len(after_words) == 0:
            selected_id = (
                w.word_id
            )  # if there are no words after, select last word of the before words
        words.append([w.word_id, w.word])

    words.reverse()  # before words are selected in reverse order
    selected_id = 0

    for idx, w in enumerate(after_words):
        if idx == 0 and len(before_words) > 0:
            selected_id = w.word_id  # first result of this query is the selected word
        words.append([w.word_id, w.word])

    return selected_id, words


def get_words(request):
    """Returns page_size words above and below given string prefix."""
    page_size = 100
    query_data = json.loads(request.GET["query"])
    page = int(request.GET["page"])

    lex = get_lex_db_name(query_data["lexicon"])
    if lex == "":
        return ""

    word_prefix = query_data["w"]

    selected_id, words = query_words(word_prefix, lex, page, page_size)

    response = {
        "selectId": selected_id,
        "error": "",
        "wtprefix": "test1",
        "nocache": 0,
        "container": request.GET["idprefix"] + "Container",
        "requestTime": request.GET["requestTime"],
        "page": 0,
        "lastPage": 0,
        "lastPageUp": 0,
        "query": word_prefix,
        "arrOptions": words,
    }
    return JsonResponse(response)


def get_definition(request):
    """Returns all fields for a requested word as json."""
    lex = get_lex_db_name(request.GET["lexicon"])
    if lex == "":
        return ""

    word_id = request.GET["id"]
    word = Word.objects.filter(word_id=word_id, lexicon=lex).first()

    response = {
        "principalParts": None,
        "def": word.definition,
        "defName": None,
        "word": word.word,
        "unaccentedWord": "ω",
        "lemma": None,
        "requestTime": 0,
        "status": "0",
        "lexicon": "lsj",
        "word_id": word.word_id,
        "method": "setWord",
    }
    return JsonResponse(response)


def fulltext_query(request):
    """Query Solr and return the results as json."""
    solr_query = request.GET.get("q", "")  # "features: food"

    # add field name to each query term
    solr_query_list = solr_query.split(" ")
    real_query = ""
    for i in solr_query_list:
        real_query += "features:" + i + " "

    solr_url = (
        "http://localhost:8983/solr/localDocs/select?indent=true&wt=json&q.op=AND&q="
        + real_query
    )

    r = requests.get(solr_url)
    response = json.loads(r.text)

    num_found = response["response"]["numFound"]

    res = []
    for document in response["response"]["docs"]:
        word_id = document["id"].split("_")[-1:][
            0
        ]  # remember pindar_dico lexicon has a _, so only get very last item
        lex = document["cat"][0]
        word = Word.objects.filter(word_id=word_id, lexicon=lex).first()
        r = {}
        r["id"] = word.word_id
        r["lex"] = word.lexicon
        r["lemma"] = word.word
        r["def"] = word.definition
        res.append(r)

    response = {
        "num": num_found,
        "ftquery": None,
        "ftresults": res,
        "requestTime": 0,
        "status": "0",
        "lexicon": "lsj",
    }
    return JsonResponse(response, safe=False, json_dumps_params={"ensure_ascii": False})


def react_home(request):
    """Respond to request for the React single page app."""
    return render(request, "philolog/index.html")
