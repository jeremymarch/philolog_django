from django.shortcuts import render
from django.http import JsonResponse
from . models import Word
import json
import requests


# def error404(request, exception):
#     return HttpResponseRedirect("/")


def home(request):
    return render(request, "philolog/index.html")


def query(request):
    query_data = json.loads(request.GET['query'])

    page = int(request.GET['page'])

    if query_data['lexicon'] == "lsj":
        lex = "greatscott"
    elif query_data['lexicon'] == "ls":
        lex = "latindico"
    elif query_data['lexicon'] == "slater":
        lex = "pindar_dico"
    else:
        return ""

    before_words = []
    after_words = []
    page_size = 100
    if page <= 0:
        before_words = Word.objects.filter(word__lt=query_data['w'], lexicon=lex).order_by('-word', 'word_id')[0:page_size]
    if page >= 0:
        after_words = Word.objects.filter(word__gte=query_data['w'], lexicon=lex).order_by('word', 'word_id')[0:page_size]

    words = []
    for w in before_words:
        words.append([w.word, w.word_id])

    words.reverse()  # before words are selected in reverse order
    selected_id = 0
    scroll_position = 'top'  # will either be 'top' or the word_id of the selected word

    for idx, w in enumerate(after_words):
        if idx == 0:
            selected_id = w.word_id  # first result of this query is the selected word
            scroll_position = ''
        words.append([w.word, w.word_id])

    response = {
        'selectId': selected_id,
        'error': '',
        'wtprefix': 'test1',
        'nocache': 0,
        'container': request.GET['idprefix'] + 'Container',
        'requestTime': request.GET['requestTime'],
        'page': 0,
        'lastPage': 0,
        'lastPageUp': 1,
        'scroll': scroll_position,
        'query': '',
        'arrOptions': words
    }
    return JsonResponse(response)


def get_def(request):
    if request.GET['lexicon'] == "lsj":
        lex = "greatscott"
    elif request.GET['lexicon'] == "ls":
        lex = "latindico"
    elif request.GET['lexicon'] == "slater":
        lex = "pindar_dico"
    else:
        return ""

    word_id = request.GET['id']
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
        "method": "setWord"
    }
    return JsonResponse(response)


def ft(request):
    solr_query = request.GET.get("q", "")  # "features: food"

    # add field name to each query term
    solr_query_list = solr_query.split(" ")
    real_query = ""
    for i in solr_query_list:
        real_query += "features:" + i + " "

    solr_url = "http://localhost:8983/solr/localDocs/select?indent=true&wt=json&q.op=AND&q=" + real_query

    r = requests.get(solr_url)
    response = json.loads(r.text)

    num_found = response['response']['numFound']

    res = []
    for document in response['response']['docs']:
        word_id = document['id'].split("_")[-1:][0]  # remember pindar_dico lexicon has a _, so only get very last item
        lex = document['cat'][0]
        word = Word.objects.filter(word_id=word_id, lexicon=lex).first()
        r = {}
        r['id'] = word.word_id
        r['lex'] = word.lexicon
        r['lemma'] = word.word
        r['def'] = word.definition
        res.append(r)

    response = {
        "num": num_found,
        "ftquery": None,
        "ftresults": res,
        "requestTime": 0,
        "status": "0",
        "lexicon": "lsj",
    }
    return JsonResponse(response, safe=False, json_dumps_params={'ensure_ascii': False})
