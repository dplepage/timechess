import re
import os

page = os.system("curl http://commons.wikimedia.org/wiki/Category:SVG_chess_pieces > pages/pieces.html")
page = open("pages/pieces.html").read()
r = re.compile('href="(/wiki/File:Chess_.*?t45\.svg)"')
links = [m.group(1) for m in set(r.finditer(page))]

r2 = re.compile(u"/upload.wikimedia.org/wikipedia/commons/.*?/Chess_.*?.svg")
for i, x in enumerate(links):
    # url = "http://commons.wikimedia.org"+x
    # print "curl {0} > pages/{1}.html".format(url, i)
    # os.system("curl {0} > pages/{1}.html".format(url, i))
    text = open("pages/{0}.html".format(i)).read()
    links = {x for x in r2.findall(text) if 'thumb' not in x}
    os.system("wget http:/{0}".format(list(links)[0]))

