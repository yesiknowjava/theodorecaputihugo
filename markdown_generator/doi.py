import os
import requests
import bibtexparser
import tempfile
from pprint import pprint
from time import strptime
import pybtex
import pybtex.database.input.bibtex 
import pybtex.plugin
import biblib.bib
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import re
import frontmatter
import unicodedata
import random
import sys
import time
from tqdm import tqdm
import string

from unidecode import unidecode
def remove_non_ascii(text):
    new_string = text.encode('ascii',errors='ignore').decode()
    return str(new_string)
    # return unidecode(unicode(text, encoding = "utf-8"))

style = pybtex.plugin.find_plugin('pybtex.style.formatting', 'plain')()
backend = pybtex.plugin.find_plugin('pybtex.backends', 'plaintext')()

dirs = [x[0].split("/")[-1] for x in os.walk("../content/publications")]
dirs = [x for x in dirs if x != "publications"]

# DOIS = [
#     ("10.1016/j.drugpo.2021.103133", "covid-cannabis", "IJDP-2021"),
#     ("10.1136/tobaccocontrol-2021-056661", "pmi-evali", "TC-2021"),
# ]


def get_frontmatter(fn):
    post = frontmatter.load(fn)
    return post


# p = get_abstract("/home/theo/theodorecaputihugo/content/publications/2020-lgbq-violence/index.md")
# print(p['abstract'])
# print(p['links'][0]['url'])
# print(os.path.basename(p['url_pdf']))

# exit()

def cleanhtml(raw_html):
#   cleanr = re.compile('<.*?>')
  cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

def doi2abstract(doi):
    url = f"http://api.crossref.org/works/{doi}"
    r = requests.get(url)
    j = r.json()
    if 'message' in j:
        return cleanhtml(j['message'].get('abstract', ''))
    else:
        return ''
    # root = ET.fromstring(r.text)
    # for child in root[0][1][0][-1][0][0][-1][2]:
    #     print(child.tag, child.attrib, child.text)


def doi2bib(doi):
  """
  Return a bibTeX string of metadata for a given DOI.
  """

  url = "http://dx.doi.org/" + doi
  headers = {"accept": "application/x-bibtex"}
  r = requests.get(url, headers = headers)
  out = r.text
  
#   print(doi)
#   print(out)
  
  return out

def remove_control_characters(s):
    # return "".join(ch for ch in s if unicodedata.category(ch)[0]!="C")
    # s = s.replace("â", "'")
    # s = s.replace("\\textquotedblleft", "'").replace("\\textquotedblright", "'")
    # s = s.replace("\\&", "&").replace("\\#", "#")
    # s = s.replace("", "")
    return s

# def remove_control_characters2(s):
#     return "".join(ch for ch in s if unicodedata.category(ch)[0]!="C")
    # return s.replace("â", "'").replace("\\textquotedblleft", "'").replace("\\textquotedblright", "'").replace("\\&", "&").replace("\\#", "#")


def get_citation(doi):
    headers = {
        'Accept': 'text/x-bibliography; style=apa',
        # 'Accept': 'text/x-bibliography; style=elsevier-harvard',
    }
    citation = requests.get(f'https://doi.org/{doi}', headers=headers)
    out = citation.text.replace("\n", "")

    # print(doi)
    # print(out)
    
    return out

# get_citation("10.1080/09687637.2017.1288681")
# doi2bib("10.1080/09687637.2017.1288681")
# exit()


# DOIS = []
# for dir in dirs:

#     print(dir)

#     index_fn = f"../content/publications/{dir}/index.md"

#     with open(index_fn, "r") as f:
#         txt = f.read()

#     with open(index_fn, "w") as f:
#         f.write(remove_non_ascii(txt))

#     p = frontmatter.load(index_fn)

#     doi = p.get('doi', None)
#     dir_no_date = "-".join(dir.split("-")[1:])
#     pdf_no_ext = str(os.path.basename(p['url_pdf'])).replace(".pdf", "")
#     abstract = p.get('abstract', None)
#     if not abstract:
#         if doi:
#             abstract = doi2abstract(doi)
#     url_pdf = p['links'][0]['url']
#     if not doi:
#         doi = ""
#     if not abstract:
#         abstract = ""

#     altmetric_id = p.get('altmetric_id', None)
#     if not altmetric_id:
#         altmetric_id = ''

#     out = (doi, dir_no_date, pdf_no_ext, abstract, url_pdf, altmetric_id)
#     DOIS.append(out)



import pandas as pd
df = pd.read_csv("publications.csv", encoding='utf8')
df = df[df.title.notnull()]
df['paperurl'] = [x.split("?")[0] for x in df['paperurl']]
df['paperurl'] = [x.split("#")[0] for x in df['paperurl']]
df.to_csv("publications.csv", encoding='utf8')

print(df.head())
print(df.tail())

# exit()

DOIS = []
SLEEP_TIME = 0
articles = []
for i, r in tqdm(df.iterrows()):
    
    doi = r['doi']
    
    if not pd.isnull(r['doi']):

        # time.sleep(SLEEP_TIME + random.random())
        citation = get_citation(doi) 

        # time.sleep(SLEEP_TIME + random.random())
        d = doi2bib(doi)

        t = tempfile.NamedTemporaryFile()
        with open(t.name, "w") as bibtex_file:
            bibtex_file.write(d)

        with open(t.name, "r") as bibtex_file:
            bibtex = bibtex_file.read()

        t = tempfile.NamedTemporaryFile()
        with open(t.name, "w") as bibtex_file:
            bibtex_file.write(d)

        with open(t.name, "r") as bibtex_file:
            bib_database = bibtexparser.load(bibtex_file)
            if len(bib_database.entries) == 0:
                print(bibtex_file.read())

        entry = bib_database.entries[0]
        authors = entry['author'].split(" and ")
        
        year = str(entry['year'])
        
        month = strptime(entry['month'], '%b').tm_mon
        month = str(month)
        if len(month) == 1:
            month = "0" + month

        ID = authors[0].split()[-1] + month + year + ' '.join(r['title'].split()[:3])
        ID = ID.title().replace(" ", "")
        entry['ID'] = ID.translate(str.maketrans('', '', string.punctuation))
        # pprint(entry)
        # print(bibtexparser.dumps(entry))
        
        out = {
            'doi': r['doi'],
            'year': year,
            'pub_date': f"{year}-{month}-01",
            'title': r['title'].replace('"', '\\"'),
            'venue': entry['journal'].replace("\\&", "&"),
            'authors': authors,
            'citation': remove_non_ascii(remove_control_characters(citation)),
            'url_slug': r['slug'],
            'paper_url': f"https://www.theodorecaputi.com/files/{r['pdfurl']}.pdf",
            'excerpt': '',
            'paperurlslug': r['pdfurl'],
            'bibtex': bibtexparser.dumps(bib_database),
            'ID': entry['ID'],
            # 'abstract': doi2abstract(doi),
            'url_pdf': r['paperurl'],
            'abstract': r['abstract'],
            'altmetric_id': '',
            'type': r['type']
        }

    else:

        # month = strptime(r['month'], '%b').tm_mon
        month = str(month)
        if len(month) == 1:
            month = "0" + month

        year = str(int(r['year']))
        pubdate = f"{year}-{month}-01"
        
        # print(r['author'])
        # print(pubdate)

        out = {
            'year': year,
            'doi': doi,
            'pub_date': pubdate,
            'title': r['title'],
            'venue': r['journal'],
            'authors': r['author'].split(" and "),
            'citation': r['citation'],
            'url_slug': r['slug'],
            'paper_url': f"https://www.theodorecaputi.com/files/{r['pdfurl']}.pdf",
            'excerpt': '',
            'paperurlslug': r['pdfurl'],
            'bibtex': bibtex,
            # 'abstract': doi2abstract(doi),
            'url_pdf': r['paperurl'],
            'abstract': r['abstract'],
            'altmetric_id': '',
            'type': r['type']
        }

    articles.append(out)


articles = sorted(articles, key=lambda i: i['pub_date'])[::-1]
pprint(articles)

article_types = [
    'Original Research',
    'Uninvited Commentary',
    'Invited Commentary',
    'Team Science'
]


def latexmaker(tag, content):
    out = "\\"
    out += tag
    out += "{"
    out += content
    out += "}"
    return out

# barticles = []
# db = biblib.db_from_string("")
# for barticle in articles:
#     doi = barticle['doi']
#     db.add_entry(entry)


with open("../static/files/pubs.tex", "w") as texfile, open("../static/files/pubs.bib", "w") as bibfile:
    tex = ""
    bib = ""

    # tex += latexmaker("nobibliography", "pubs")
    # tex += "\n"
    # tex += latexmaker("bibliographystyle", "apa")
    # tex += "\n"

    for article_type in tqdm(article_types):

        tex += latexmaker("subsection*", article_type)
        tex += "\\noindent"
        tex += "\n"

        for article in articles:

            if article['type'] != article_type:
                continue

            # if 'ID' not in article:
            #     continue

            tex += latexmaker("years", article['year'])
            # tex += latexmaker("bibentry", article['ID'])
            latex_citation = article['citation']
            latex_citation = latex_citation.replace("Caputi, T.", "\\textbf{Caputi, T. L.}")
            latex_citation = latex_citation.replace("Caputi, T. L.", "\\textbf{Caputi, T. L.}")

            tex += latex_citation
            tex += " ["
            tex += latexmaker("href", article['url_pdf']) + "{Link}"
            tex += " | "
            tex += latexmaker("href", article['paper_url']) + "{PDF}"
            tex += "] \\\\[.2cm]"
            tex += "\n"

            bib += article['bibtex']
            bib += "\n\n"

        tex += "\n"

    texfile.write(tex)
    bibfile.write(bib)



# doi2bib("10.1080/09687637.2017.1288681")
# doi2bib("10.1093/ntr/ntx143")
# get_citation("10.1093/ntr/ntx143")
# print()
# print()
# exit()

# SLEEP_TIME = 0
# articles = []
# for doi, slug, paperurl, abstract, url_pdf, altmetric_id in tqdm(DOIS):

#     if doi != "":

#         time.sleep(SLEEP_TIME + random.random())
#         citation = get_citation(doi) 

#         time.sleep(SLEEP_TIME + random.random())
#         d = doi2bib(doi)

#         t = tempfile.NamedTemporaryFile()
#         with open(t.name, "w") as bibtex_file:
#             bibtex_file.write(d)

#         with open(t.name, "r") as bibtex_file:
#             bibtex = bibtex_file.read()

#         t = tempfile.NamedTemporaryFile()
#         with open(t.name, "w") as bibtex_file:
#             bibtex_file.write(d)

#         with open(t.name, "r") as bibtex_file:
#             bib_database = bibtexparser.load(bibtex_file)
#             if len(bib_database.entries) == 0:
#                 print(bibtex_file.read())
        
#         # with open(t.name, "r") as bibtex_file:
#         #     db = biblib.bib.Parser().parse(bibtex_file).get_entries()

#         # print(db)
#         # for ent in db.values():
#         #     print("here")
#         #     print(ent.to_bib())
#         #     citation = ent.to_bib()

#         # citation = pybtex.format_from_file(t.name, style = "plain", backend="html")    
        
#         entry = bib_database.entries[0]
#         # pprint(entry)

#         month = strptime(entry['month'],'%b').tm_mon
#         month = str(month)
#         if len(month) == 1:
#             month = "0" + month

#         out = {
#             'doi': doi,
#             'pub_date': f"{entry['year']}-{month}-01",
#             'title': entry['title'],
#             'venue': entry['journal'],
#             'authors': entry['author'].split(" and "),
#             'citation': remove_non_ascii(remove_control_characters(citation)),
#             'url_slug': slug,
#             'paper_url': f"https://www.theodorecaputi.com/files/{paperurl}.pdf",
#             'excerpt': '',
#             'paperurlslug': paperurl,
#             'bibtex': bibtex,
#             # 'abstract': doi2abstract(doi),
#             'url_pdf': url_pdf,
#             'abstract': abstract,
#             'altmetric_id': altmetric_id
#         }

#         articles.append(out)


# pprint(articles)
# exit()

# pprint(articles)
# import pandas as pd
# df = pd.DataFrame(articles)
# df.to_csv("publications.tsv", sep="\t", index = False)

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;"
    }

def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)


import os
import datetime
for row, item in enumerate(articles):

    # pprint(item)
    
    # md_filename = str(item.pub_date) + "-" + item.url_slug + ".md"
    # html_filename = str(item.pub_date) + "-" + item.url_slug
    # year = item.pub_date[:4]
    
    ## YAML variables
    
    md = "---\ntitle: \""   + item['title'] + '"\n'

    authors = [f'- "{x}"' for x in item['authors']]
    author_md = "\nauthors:\n{}".format('\n'.join(authors))
    author_md = author_md.replace("Theodore L. Caputi", "admin")
    author_md = author_md.replace("Theodore Caputi", "admin")
    author_md = author_md.replace("Theodore L Caputi", "admin")
    md += author_md

    dt = datetime.datetime.strptime(item['pub_date'], "%Y-%m-%d")
    md += '\ndate: "{}"'.format(dt.strftime('%Y-%m-%dT00:00:00Z'))
    md += '\ndoi: "{}"'.format(item['doi'])
    md += '\nvenue: "{}"'.format(item['venue'])
    md += '\npublishDate: "2017-01-01T00:00:00Z"'
    md += '\npublication_types: ["2"]'
    md += '\nabstract: "{}"'.format(item['abstract'].replace("\n", "<br>"))
    md += '\nsummary: "{}"'.format(item['citation'])
    md += '\ntags: \nfeatured: false\nlinks:\n- name: Paper Link'
    md += '\n  url: "{}"'.format(item['url_pdf'])
    md += '\nurl_pdf: "/files/{}.pdf"'.format(item['paperurlslug'])
    md += '\nimage:'
    md += '\n  focal_point: ""'
    md += '\n  preview_only: false'
    md += '\n---'

    md = md.replace("{", "")
    md = md.replace("}", "")
    md = md.replace("'", "â")

    md = remove_control_characters(md)

    overwrite = True

    dir_name = f"../content/publications/{dt.strftime('%Y')}-{item['url_slug']}"
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

    index_filename = f"{dir_name}/index.md"
    if not os.path.isfile(index_filename) or overwrite:
        with open(index_filename, 'w') as f:
            f.write(md)

    bib_filename = f"{dir_name}/cite.bib"
    if not os.path.isfile(bib_filename) or overwrite:
        with open(bib_filename, 'w') as f:
            f.write(item['bibtex'])
    

    print(f"WRITING {index_filename}")
    



# pprint(bib_database.entries)
