import requests
from pathlib import Path
from pelican import signals

FILES = [
    "pure-single/static/css/pure.css",
    "pure-single/static/css/pygments.css"
]

files = [Path(file) for file in FILES]


url = 'https://www.toptal.com/developers/cssminifier/raw'

def minifier(pelican_object):
    for file in files:
        new_file = file.parent / f"{file.stem}.min{file.suffix}"
        with open(file, 'rb') as rb:
            data = {'input': rb.read()}
            response = requests.post(url, data=data)
        with open(new_file, "w") as wb:
            wb.write(response.text)



def register():
    signals.initialized.connect(minifier)