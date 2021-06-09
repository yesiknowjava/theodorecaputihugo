import requests
import bibtexparser
import tempfile
from pprint import pprint
from time import strptime
import pybtex

import pybtex.database.input.bibtex 
import pybtex.plugin
# import codecs
# import latexcodec
import biblib.bib

style = pybtex.plugin.find_plugin('pybtex.style.formatting', 'plain')()
backend = pybtex.plugin.find_plugin('pybtex.backends', 'plaintext')()

def doi2bib(doi):
  """
  Return a bibTeX string of metadata for a given DOI.
  """

  url = "http://dx.doi.org/" + doi

  headers = {"accept": "application/x-bibtex"}
  r = requests.get(url, headers = headers)

  return r.text


DOIS = [
    ("10.1016/j.drugpo.2021.103133", "covid-cannabis", "IJDP-2021")
]

import sys
articles = []
for doi, slug, paperurl in DOIS:
    t = tempfile.NamedTemporaryFile()
    with open(t.name, "w") as bibtex_file:
        bibtex_file.write(doi2bib(doi))

    with open(t.name, "r") as bibtex_file:
            bibtex = bibtex_file.read()

    with open(t.name, "r") as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)
    
    with open(t.name, "r") as bibtex_file:
        db = biblib.bib.Parser().parse(bibtex_file).get_entries()
        # print(db)
        # for ent in db.values():
        #     print("here")
        #     print(ent.to_bib())
        #     citation = ent.to_bib()

    headers = {
        # 'Accept': 'text/x-bibliography; style=apa',
        'Accept': 'text/x-bibliography; style=elsevier-harvard',
    }
    citation = requests.get(f'https://doi.org/{doi}', headers=headers)


    # citation = pybtex.format_from_file(t.name, style = "plain", backend="html")    
    
    entry = bib_database.entries[0]
    # pprint(entry)

    month = strptime(entry['month'],'%b').tm_mon
    month = str(month)
    if len(month) == 1:
        month = "0" + month

    out = {
        'doi': doi,
        'pub_date': f"{entry['year']}-{month}-01",
        'title': entry['title'],
        'venue': entry['journal'],
        'authors': entry['author'].split(" and "),
        'citation': citation.text.replace("\n", ""),
        'url_slug': slug,
        'paper_url': f"https://www.theodorecaputi.com/files/{paperurl}.pdf",
        'excerpt': '',
        'paperurlslug': paperurl,
        'bibtex': bibtex
    }

    articles.append(out)

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

    pprint(item)
    
    # md_filename = str(item.pub_date) + "-" + item.url_slug + ".md"
    # html_filename = str(item.pub_date) + "-" + item.url_slug
    # year = item.pub_date[:4]
    
    ## YAML variables
    
    md = "---\ntitle: \""   + item['title'] + '"\n'

    authors = [f'-"{x}"' for x in item['authors']]
    author_md = "\nauthors:\n{}".format('\n'.join(authors))
    author_md = author_md.replace("Theodore L. Caputi", "admin")
    author_md = author_md.replace("Theodore Caputi", "admin")
    md += author_md

    dt = datetime.datetime.strptime(item['pub_date'], "%Y-%m-%d")
    md += "\ndate: '{}'".format(dt.strftime('%Y-%m-%dT00:00:002'))
    md += "\ndoi: '{}'".format(item['doi'])
    md += "\nvenue: '{}'".format(item['venue'])
    md += "\npublishDate: '2010-01-01T00:00:002'"
    md += "\npublication_types: ['2']"
    md += "\nsummary: '{}'".format(item['citation'])
    md += "\ntags: \nfeatured: false\nlinks:\n- name: Paper Link"
    md += "\n  url: 'https://doi.org/{}'".format(item['doi'])
    md += "\nurl_pdf: '/files/{}.pdf'".format(item['paperurlslug'])
    md += "\nimage:"
    md += "\n  focal_point: ''"
    md += "\n  preview_only: false"
    md += "\n---"

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