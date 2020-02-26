
import sys
import os
sys.path.append(os.curdir)
from custom_filters.urls import hostname
from plugins.algolia import algolia_search

AUTHOR = 'Antonio Feregrino'
SITENAME = 'Antonio Feregrino'
TAGLINE = 'data science and software development'
SITEURL = ''

PATH = 'content'

TIMEZONE = 'Europe/London'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Social widget
SOCIAL = (
    ('github', 'https://github.com/fferegrino/'),
    ('twitter-square', 'https://twitter.com/io_exception'),
    ('youtube', 'https://www.youtube.com/channel/UC8KCb358oioQMcJ5pUfs8UQ'),
    ('linkedin', 'https://www.linkedin.com/in/antonioferegrino/'),
)

OTHER_BLOGS = (
    ("That C# Guy", "https://thatcsharpguy.com"),
    ("Personal blog", "https://fferegrino.org"),
)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

STATIC_CONTENT=[
    "images"
]
THEME = "pure-single"
COVER_IMG_URL="https://i.imgur.com/icFY0WL.jpg"
PROFILE_IMG_URL="https://i.imgur.com/6kbOP9f.jpg"

# Filters
JINJA_FILTERS = {
    'hostname': hostname
}

PLUGINS = [algolia_search]