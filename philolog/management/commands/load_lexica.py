from django.core.management import BaseCommand
from philolog.models import Word
from django.conf import settings
import os
import git
import lxml.etree as ET
import sys
import unicodedata
import requests


# https://stackoverflow.com/questions/3402520/is-there-a-way-to-force-lxml-to-parse-unicode-strings-that-specify-an-encoding-i
utf8_parser = ET.XMLParser(encoding='utf-8')


def parse_from_unicode(unicode_str):
    s = unicode_str.encode('utf-8')
    return ET.fromstring(s, parser=utf8_parser)


# ALTER TABLE philolog_word ALTER COLUMN word SET DATA TYPE character varying(255) COLLATE "el-x-icu";


CONVERT_TEI_TO_HTML = True  # do xslt conversion from TEI to HTML
IMPORT_TO_SOLR = True
IMPORT_TO_DJANGO = True
SOLR_IMPORT_DIR = settings.SOLR_IMPORT_DIR
SOLR_COLLECTION_NAME = settings.SOLR_COLLECTION_NAME
SOLR_SERVER = settings.SOLR_SERVER


def solr_create_xml_root():
    return ET.Element('add')


def solr_append_word(root, word_id, name, lexicon, content):
    doc_el = ET.SubElement(root, 'doc')

    id_el = ET.SubElement(doc_el, 'field', name='id')
    id_el.text = lexicon + "_" + str(word_id)

    name_el = ET.SubElement(doc_el, 'field', name='name')
    name_el.text = name

    cat_el = ET.SubElement(doc_el, 'field', name='cat')
    cat_el.text = lexicon

    features_el = ET.SubElement(doc_el, 'field', name='features')
    features_el.text = content


def solr_write_file(solr_xml_root, file_name):
    solr_xml_doc = ET.ElementTree(solr_xml_root)
    with open(file_name, 'wb') as f:
        solr_xml_doc.write(f, encoding="UTF-8", xml_declaration=True, pretty_print=True)


# https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string
def decompose_and_strip_combining(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')  # Mn is the combining character class


# need to handle digamma = ewww
# and ' = ""
def get_greek_sort_key(ustr):
    # s = unicodedata.normalize('NFD', ustr)
    # s = s.strip(u"\u0304\u0301\u0314\u0313\u0300\u0342\u0345\u0306\u0308")  #remove combining chars
    if ustr == "σάν":
        return "πωω"
    elif ustr == "Ϟ ϟ":
        return "πωωω"
    else:
        ustr = ustr.replace(u"\u1fbd", u"")  # koronis, used for spacing smooth breathing
        s = decompose_and_strip_combining(ustr)
        s = s.lower()
        s = s.replace(u"\u03c2", u"\u03c3")  # replace final sigma with sigma
        s = s.replace(u"ʼ", u"")  # only in ʼκτώ
        s = s.replace(u"ϝ", u"εωωω")
        return s


def get_latin_sort_key(s):
    s = decompose_and_strip_combining(s)
    s = s.lower()
    if s == "'st":
        return "st2"
    return s


# return empty string or string number if word already exists in word_dict
def get_unique_suffix(word, word_dict):
    strwordnum = ""
    if word in word_dict:
        wordnum = word_dict[word]
        word_dict[word] = wordnum + 1
        strwordnum = str(wordnum + 1)
    else:
        word_dict[word] = 1
    return strwordnum


def process_lexica(lexica):
    if os.path.isdir(SOLR_IMPORT_DIR) is False:
        os.mkdir(SOLR_IMPORT_DIR)

    for lex in lexica:
        lex_path_exists = os.path.isdir(lex.path)

        if lex_path_exists is False:
            print("cloning repository: " + lex.repo_url + "...\n")
            repo = git.Repo.clone_from(lex.repo_url, lex.path, branch=lex.repo_branch)
            print("clone complete\n")
        else:
            print("pulling updates from repository: " + lex.repo_url + "...\n")
            repo = git.Git(lex.path)
            repo.pull("origin", lex.repo_branch)
            print("pull complete\n")

        if CONVERT_TEI_TO_HTML:
            print("converting tei to html...")
            trans = ET.parse("import_data/logeionxslt.xml").getroot()
            transform = ET.XSLT(trans)

        lex_word_counter = 1
        url_lemma_dictionary = {}
        display_url_lemma_dictionary = {}

        for x in range(lex.start_file_num, (lex.end_file_num + 1)):
            lex_file = lex.path + "/" + lex.file_prefix + str(x).zfill(2) + ".xml"  # path with leading zero

            if lex_file == "import_data/latinrepo/latindico10.xml":  # j is skipped
                continue

            if IMPORT_TO_SOLR:
                solr_xml_root = solr_create_xml_root()

            root = ET.parse(lex_file).getroot()

            print("file: " + lex_file)

            top = root.find("text").find("body")  # Lewis and Short has a body tag, LSJ does not
            if top is None:
                top = root.find("text")

            alpha_div = top.find(lex.alphabetic_div_name)
            for lemma_div in alpha_div.findall(lex.lemma_div):  # in case there is more than one div0
                lemma = lemma_div.find("head")
                orth = lemma.find("orth")  # n1671a
                if orth is not None:
                    lemma_text = orth.text
                else:
                    lemma_text = lemma.text
                original_id = lemma_div.get("orig_id")
                if original_id is None:
                    original_id = ""
                logeion_id = lemma_div.get("id")
                if logeion_id is None:
                    logeion_id = ""

                entry_def = ET.tostring(lemma_div, method="xml", encoding="utf-8").decode('UTF-8')  # changing UTF-8 to unicode no longer escapes character (= good
                # print("entry: " + str(len(entry_def)))
                sort_key = lex.sort_key_func(lemma_text)

                if logeion_id in lex.letter_ids:
                    idx = lex.letter_ids.index(logeion_id)
                    lemma_text = lex.head_letters[idx]
                    print("letter: " + lemma_text)

                # web unique url headword
                # sort_suffix = get_unique_suffix(sort_key, url_lemma_dictionary)  # will change space to - later
                # display_suffix = get_unique_suffix(lemma_text, display_url_lemma_dictionary)

                # print(entry_def)

                if CONVERT_TEI_TO_HTML:
                    # print(entry_def)
                    entry_root_for_xslt = parse_from_unicode(entry_def)

                    new_dom = transform(entry_root_for_xslt)
                    html_string = ET.tostring(new_dom, method="xml", encoding="utf-8").decode('UTF-8')
                    # print(html_string)

                if IMPORT_TO_DJANGO:
                    w = Word.objects.create(word_id=lex_word_counter, lexicon=lex.file_prefix, word=lemma_text.strip(), definition=html_string.strip())
                    w.save()

                if IMPORT_TO_SOLR:
                    # strip xml tags
                    entry_def_notags = ET.tostring(lemma_div, method='text', encoding='UTF-8').decode('UTF-8')
                    # print(entry_def_notags + "\n\n")
                    solr_append_word(solr_xml_root, lex_word_counter, lemma_text.strip(), lex.file_prefix, entry_def_notags.strip())

                lex_word_counter = lex_word_counter + 1

            # save xml file to SOLR_IMPORT_DIR
            solr_file = SOLR_IMPORT_DIR + lex.file_prefix + str(x).zfill(2) + ".xml"
            solr_write_file(solr_xml_root, solr_file)

            # upload to solr server
            solr_update_url = SOLR_SERVER + "/solr/" + SOLR_COLLECTION_NAME + "/update?commit=true"
            solr_update_headers = {"Content-Type": "application/xml"}
            solr_update_payload = open(solr_file, 'rb').read()
            res = requests.post(solr_update_url, headers=solr_update_headers, data=solr_update_payload)
            # print("res: " + res.text)

            # or use the terminal command which is much faster:
            # os.system("bin/post -c SOLR_COLLECTION_NAME ~/Documents/solr_import_docs")


# https://stackoverflow.com/questions/49610125/whats-the-easiest-way-to-import-a-csv-file-into-a-django-model
class Command(BaseCommand):
    # help = 'Load a questions csv file into the database'

    # def add_arguments(self, parser):
    #     parser.add_argument('--path', type=str)

    def handle(self, *args, **kwargs):
        process_lexica(lexica)


class lex:
    repo_url = ""
    repo_branch = ""
    path = ""
    name = ""
    file_prefix = ""
    head_letters = ""
    letter_ids = ""
    sort_key_func = None
    alphabetic_div_name = ""
    lemma_div = ""
    start_file_num = ""
    end_file_num = ""


lsjlex = lex()
lsjlex.repo_url = "https://github.com/helmadik/LSJLogeion.git"
lsjlex.repo_branch = "master"
lsjlex.path = "import_data/greekrepo"
lsjlex.file_prefix = "greatscott"
# san is after π
# koppa is after san
lsjlex.head_letters = ["Α α", "Β β", "Γ γ", "Δ δ", "Ε ε", "Ϝ ϝ", "Ζ ζ", "Η η", "Θ θ", "Ι ι", "Κ κ", "Λ λ", "Μ μ", "Ν ν", "Ξ ξ", "Ο ο", "Π π", "Ϻ ϻ", "Ϟ ϟ", "Ρ ρ", "Σ σ", "Τ τ", "Υ υ", "Φ φ", "Χ χ", "Ψ ψ", "Ω ω"]
lsjlex.letter_ids = ["cross*a", "crossb", "crossg", "crossd", "crosse", "cross*v", "cross*zz", "cross*hh", "cross*qq", "cross*ii", "cross*kk", "crossl", "crossm", "crossn", "cross*c", "cross*o", "crossp", "crosssan", "crosskoppa", "cross*r", "cross*s", "cross*t", "cross*uu", "cross*f", "cross*x", "cross*y", "cross*w"]
lsjlex.sort_key_func = get_greek_sort_key
lsjlex.alphabetic_div_name = "div1"
lsjlex.lemma_div = "div2"
lsjlex.start_file_num = 2  # skip 1, it contains intro
lsjlex.end_file_num = 86

lewisshortlex = lex()
lewisshortlex.repo_url = "https://github.com/helmadik/LewisShortLogeion.git"
lewisshortlex.repo_branch = "master"
lewisshortlex.path = "import_data/latinrepo"
lewisshortlex.file_prefix = "latindico"
lewisshortlex.head_letters = ["A a", "B b", "C c", "D d", "E e", "F f", "G g", "H h", "I i", "K k", "L l", "M m", "N n", "O o", "P p", "Q q", "R r", "S s", "T t", "U u", "V v", "X x", "Y y", "Z z"]
lewisshortlex.letter_ids = ["crossA1", "crossB", "crossC", "crossD", "crossE", "crossF", "crossG", "crossH", "crossI", "crossK", "crossL", "crossM", "crossN", "crossO1", "crossP", "crossQ", "crossR", "crossS", "crossT", "crossU", "crossV", "crossX", "crossY", "crossZ"]
lewisshortlex.sort_key_func = get_latin_sort_key
lewisshortlex.alphabetic_div_name = "div0"
lewisshortlex.lemma_div = "div1"
lewisshortlex.start_file_num = 1
lewisshortlex.end_file_num = 25

pindarlex = lex()
pindarlex.repo_url = "https://github.com/helmadik/SlaterPindar.git"
pindarlex.repo_branch = "main"
pindarlex.path = "import_data/slaterrepo"
pindarlex.file_prefix = "pindar_dico"
pindarlex.head_letters = ["Α α", "Β β", "Γ γ", "Δ δ", "Ε ε", "Ϝ ϝ", "Ζ ζ", "Η η", "Θ θ", "Ι ι", "Κ κ", "Λ λ", "Μ μ", "Ν ν", "Ξ ξ", "Ο ο", "Π π", "Ϻ ϻ", "Ϟ ϟ", "Ρ ρ", "Σ σ", "Τ τ", "Υ υ", "Φ φ", "Χ χ", "Ψ ψ", "Ω ω"]
pindarlex.letter_ids = ["cross*a", "crossb", "crossg", "crossd", "crosse", "cross*v", "cross*zz", "cross*hh", "cross*qq", "cross*ii", "cross*kk", "crossl", "crossm", "crossn", "cross*c", "cross*o", "crossp", "crosssan", "crosskoppa", "cross*r", "cross*s", "cross*t", "cross*uu", "cross*f", "cross*x", "cross*y", "cross*w"]
pindarlex.sort_key_func = get_greek_sort_key
pindarlex.alphabetic_div_name = "div1"
pindarlex.lemma_div = "div2"
pindarlex.start_file_num = 1  # skip 1, it contains intro
pindarlex.end_file_num = 24

lexica = [lsjlex, lewisshortlex, pindarlex]
