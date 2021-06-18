import json
import frontmatter
import os
import urllib.request
from urllib.parse import urlparse
import yaml
from pprint import pprint

dirs = [x[0].split("/")[-1] for x in os.walk("../content/media")]
dirs = [x for x in dirs if x != "media"]
dirs = sorted(dirs)

out = []
with open("media2.jsonl", "r") as f:
    for line in f:
        j = json.loads(line)
        if 'external_link' in j:
            out.append(j)

out = list({v['url']: v for v in out}.values())

# pprint(out[0])
# pprint(out[4])

urls = [x['url'] for x in out]

for j in out:
    if j['headline']:
        try:

            date = j['date'][:10] if j['date'] else ''

            domain = urlparse(j['url']).netloc
            pub = j['publication'] if j['publication'] else domain

            dir_name = date + "-" + pub
            dir_name = dir_name.replace(" ","-").lower()

            if 'outline_html' not in j:
                print(dir_name)
                j['outline_html'] = j['article']

            try:
                os.mkdir(f"../content/media/{dir_name}")
            except:
                pass

            try:
                urllib.request.urlretrieve(
                    "https://logo.clearbit.com/{}".format(domain), 
                    f"../content/media/{dir_name}/featured.png"
                    )
            except:
                os.system(f"cp news.png ../content/media/{dir_name}/featured.png")
                pass

            del j['url']
            del j['content']
            
            j['title'] = j['headline']
            j['summary'] = ' '.join(j['summary'].split()[:50]) + "..."
            
            if 'external_link' in j:
                j['_external_link'] = j['external_link']
                del j['external_link']

            with open(f"../content/media/{dir_name}/index.md", "w") as f:
                f.write("---\n")
                yaml.dump(j, f)
                f.write("\n---")

            print(f"PROCESSED: {dir_name}")
        except Exception as e:
            print(j['date'])
            print(j['publication'])
            print(f"ERROR: {dir_name}: {str(e)}")
            pass


# for dir in dirs:
#     fn = "../content/media/{}/index.md".format(dir)
    
#     with open(fn, "r") as f:
#         lines = f.readlines()

#     with open(fn, "w") as f:
#         for line in lines:
#             if not line.startswith("content:"):
#                 f.write(line)
    
#     print(fn)
#     post = frontmatter.load(fn)
#     res = post.to_dict()

#     found = False
#     for j in out:
#         if 'external_link' in res:
#             if j['external_link'] == res['_external_link']:
#                 found = True
#                 for k, v in j.items():
#                     post[k] = v
#                 del post['url']
#                 del post['content']
                
#                 post['title'] = post['headline']
#                 post['article'] = post['summary']
                
#                 if 'external_link' in post:
#                     post['_external_link'] = post['external_link']
#                     del post['external_link']

#                 with open(fn, "w") as f:
#                     f.write(frontmatter.dumps(post))

#                 break

#     if not found:
#         os.system("rm -rf ../content/media/{}".format(dir))
#         # os.rmdir("../content/media/{}".format(dir))

    
