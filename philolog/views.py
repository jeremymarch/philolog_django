from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from . models import Word
import json
import requests
# from .models import Post


def error404(request, exception):
    return HttpResponseRedirect("/")


def home(request):
    context = {
        # "posts": Post.objects.all()
    }
    return render(request, "philolog/index.html", context)


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
        'arrOptions': words  # [["Α α",1],["ἀ-",2],["ἀ-",3],["ἆ",4],["ἃ ἅ",5],["ἄα",6],["ἀάατος",7],["ἀάβακτοι",8],["ἀαγής",9],["ἄαδα",10],["ἀαδένη",11],["ἀαδής",12],["ἀάζω",13],["ἄαθι",14],["ἀάκατος",15],["ἀακίδωτος",16],["ἀάλιον",17],["ἀανές",18],["ἄανθα",19],["ἀάπλετος",20],["ἄαπτος",21],["ἄας",22],["ἀασιφόρος",23],["ἀασιφρονία",24],["ἀασιφροσύνη",25],["ἀάσκει",26],["ἀασμός",27],["ἀάσπετος",28],["ἀάστονα",29],["ἀατήρ",30],["ἄατος",31],["ἄατος",32],["ἀάτυλον",33],["ἀάω",34],["ἄβα",35],["ἄβαγνα",36],["ἀβάδιστος",37],["ἀβαθής",38],["ἄβαθρος",39],["ἀβαίνω",40],["ἀβακέω",41],["ἀβακηνούς",42],["ἀβακής",43],["ἀβάκητον",44],["ἀβακίζομαι",45],["ἀβάκιον",46],["ἀβακίσκος",47],["ἀβακλή",48],["ἀβακοειδής",49],["ἄβακτον",50],["ἀβάκχευτος",51],["ἀβακχίωτος",52],["ἄβαλε",53],["ἀβαμβάκευτος",54],["ἄβαξ",55],["ἀβάπτιστος",56],["ἄβαπτος",57],["ἀβαρβάριστος",58],["ἀβαρής",59],["ἄβαρις",60],["ἀβασάνιστος",61],["ἀβασίλευτος",62],["ἀβασκάνιστος",63],["ἀβάσκανος",64],["ἀβάσκαντος",65],["ἀβάστακτος",66],["ἄβαστον",67],["ἀβατόομαι",68],["ἄβατος",69],["ἀβαφής",70],["ἄβδελον",71],["ἀβδέλυκτος",72],["Ἀβδηρίτης",73],["ἄβδης",74],["ἀβέβαιος",75],["ἀβεβαιότης",76],["ἀβέβηλος",77],["ἄβεις",78],["ἄβελλον",79],["ἀβελτέρειος",80],["ἀβελτερεύομαι",81],["ἀβελτερία",82],["ἀβελτεροκόκκυξ",83],["ἀβέλτερος",84],["ἀβέρβηλον",85],["ἀβηδών",86],["ἀβήρει",87],["ἀβηροῦσιν",88],["ἀβίαστος",89],["ἀβίβαστος",90],["ἀβίβλης",91],["ἄβιδα",92],["ἄβιν",93],["ἄβιος",94],["ἄβιος",95],["ἀβίοτος",96],["ἀβίυκτον",97],["ἀβιωτοποιός",98],["ἀβίωτος",99],["ἀβλάβεια",100],["ἀβλαβής",101]]
    }

    # response = """{"selectId":1,"error":"","wtprefix":"test1","nocache":0,"container":"test1Container","requestTime":1676605233296,"page":0,"lastPage":0,"lastPageUp":1,"scroll":"top","query":"","arrOptions":[["Α α",1],["ἀ-",2],["ἀ-",3],["ἆ",4],["ἃ ἅ",5],["ἄα",6],["ἀάατος",7],["ἀάβακτοι",8],["ἀαγής",9],["ἄαδα",10],["ἀαδένη",11],["ἀαδής",12],["ἀάζω",13],["ἄαθι",14],["ἀάκατος",15],["ἀακίδωτος",16],["ἀάλιον",17],["ἀανές",18],["ἄανθα",19],["ἀάπλετος",20],["ἄαπτος",21],["ἄας",22],["ἀασιφόρος",23],["ἀασιφρονία",24],["ἀασιφροσύνη",25],["ἀάσκει",26],["ἀασμός",27],["ἀάσπετος",28],["ἀάστονα",29],["ἀατήρ",30],["ἄατος",31],["ἄατος",32],["ἀάτυλον",33],["ἀάω",34],["ἄβα",35],["ἄβαγνα",36],["ἀβάδιστος",37],["ἀβαθής",38],["ἄβαθρος",39],["ἀβαίνω",40],["ἀβακέω",41],["ἀβακηνούς",42],["ἀβακής",43],["ἀβάκητον",44],["ἀβακίζομαι",45],["ἀβάκιον",46],["ἀβακίσκος",47],["ἀβακλή",48],["ἀβακοειδής",49],["ἄβακτον",50],["ἀβάκχευτος",51],["ἀβακχίωτος",52],["ἄβαλε",53],["ἀβαμβάκευτος",54],["ἄβαξ",55],["ἀβάπτιστος",56],["ἄβαπτος",57],["ἀβαρβάριστος",58],["ἀβαρής",59],["ἄβαρις",60],["ἀβασάνιστος",61],["ἀβασίλευτος",62],["ἀβασκάνιστος",63],["ἀβάσκανος",64],["ἀβάσκαντος",65],["ἀβάστακτος",66],["ἄβαστον",67],["ἀβατόομαι",68],["ἄβατος",69],["ἀβαφής",70],["ἄβδελον",71],["ἀβδέλυκτος",72],["Ἀβδηρίτης",73],["ἄβδης",74],["ἀβέβαιος",75],["ἀβεβαιότης",76],["ἀβέβηλος",77],["ἄβεις",78],["ἄβελλον",79],["ἀβελτέρειος",80],["ἀβελτερεύομαι",81],["ἀβελτερία",82],["ἀβελτεροκόκκυξ",83],["ἀβέλτερος",84],["ἀβέρβηλον",85],["ἀβηδών",86],["ἀβήρει",87],["ἀβηροῦσιν",88],["ἀβίαστος",89],["ἀβίβαστος",90],["ἀβίβλης",91],["ἄβιδα",92],["ἄβιν",93],["ἄβιος",94],["ἄβιος",95],["ἀβίοτος",96],["ἀβίυκτον",97],["ἀβιωτοποιός",98],["ἀβίωτος",99],["ἀβλάβεια",100],["ἀβλαβής",101]]}"""
    context = {
        # "posts": Post.objects.all()
    }
    return JsonResponse(response)  # json.loads(d))  # request.GET['query'])  # https://stackoverflow.com/questions/2428092/creating-a-json-response-using-django-and-python


def get_def(request):
    context = {
        # "posts": Post.objects.all()
    }
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
    context = {
        # "posts": Post.objects.all()
    }
    # if request.GET['lexicon'] == "lsj":
    #     lex = "greatscott"
    # elif request.GET['lexicon'] == "ls":
    #     lex = "latindico"
    # elif request.GET['lexicon'] == "slater":
    #     lex = "pindar_dico"
    # else:
    #     return ""

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
        # print(word.definition)
        res.append(r)
        # print("  Name =", word.definition + "\n\n")

    # word_id = request.GET['id']
    # word = Word.objects.filter(word_id=word_id,lexicon=lex).first()

    response = {
        "num": num_found,
        "ftquery": None,
        "ftresults": res,
        "requestTime": 0,
        "status": "0",
        "lexicon": "lsj",
    }

    return JsonResponse(response, safe=False, json_dumps_params={'ensure_ascii': False})
