import sys
import os
from decouple import config
sys.path.append(os.curdir)
from custom_filters.urls import hostname
from plugins.algolia import algolia_search
from plugins.collections import collections_page_generator

AUTHOR = 'Antonio Feregrino'
SITENAME = 'Antonio Feregrino'
TAGLINE = 'data science and software development'
SITEURL = 'http://localhost:8000'

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
    ('youtube', 'https://www.youtube.com/thatcsharpguy'),
    ('linkedin', 'https://www.linkedin.com/in/antonioferegrino/'),
)

OTHER_BLOGS = (
    ("That C# Guy", "https://thatcsharpguy.com"),
    ("Personal blog", "https://fferegrino.org"),
)

DEFAULT_PAGINATION = 10

# Algolia
if config("BRANCH", default="not-master") == "master":
    ALGOLIA_INDEX_NAME = config("ALGOLIA_INDEX_NAME")
    ALGOLIA_ADMIN_API_KEY = config("ALGOLIA_ADMIN_API_KEY")
    ALGOLIA_SEARCH_API_KEY = config("ALGOLIA_SEARCH_API_KEY")
    ALGOLIA_APP_ID = config("ALGOLIA_APP_ID")

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

STATIC_CONTENT=[
    "images", 
]
STATIC_PATHS = [
    'robots.txt', 'favicon.ico'
]
THEME = "pure-single"
COVER_IMG_URL="https://ik.imagekit.io/thatcsharpguy/feregri_no/sidebar_ZtRSpq7HJM.jpg?updatedAt=1637790559197"
PROFILE_IMG_URL="https://ik.imagekit.io/thatcsharpguy/feregri_no/pfp_EpoeHfoKQZ.jpg?updatedAt=1637790988278"

# Filters
JINJA_FILTERS = {
    'hostname': hostname
}

PLUGINS = [algolia_search, collections_page_generator]

ARTICLE_EXCLUDES = ['pages', 'books']

COLLECTIONS = [
    {
        "name": "Books",
        "folder": "books",
        "item_save_as": "books/{slug}.html",
        "item_url": "books/{slug}.html",
        "item_template": "book",
        "index_location": "books"
    },
    {
        "name": "Reads",
        "folder": "reads",
        "item_save_as": "reads/{slug}.html",
        "item_url": "reads/{slug}.html",
        "item_template": "book",
        "index_location": "index"
    }
]
ARTICLE_EXCLUDES = ['pages'] + [
    collection["folder"]  for collection in COLLECTIONS
]
