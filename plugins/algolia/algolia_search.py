from bs4 import BeautifulSoup
import json
from pelican import signals
from pelican.settings import DEFAULT_CONFIG
import logging
import hashlib

from algoliasearch.search_client import SearchClient

logger = logging.getLogger(__name__)

__all__ = ['register']


def set_default_settings(settings):
    settings.setdefault('ALGOLIA_APP_ID', None)
    settings.setdefault('ALGOLIA_SEARCH_API_KEY', None)
    settings.setdefault('ALGOLIA_ADMIN_API_KEY', None)
    settings.setdefault('ALGOLIA_INDEX_NAME', None)

def init_default_config(pelican):
    set_default_settings(DEFAULT_CONFIG)
    if(pelican):
        set_default_settings(pelican.settings)


def process_html(html):
    soup = BeautifulSoup(html.replace('&nbsp;', ' '), 'html.parser')
    [code_block.extract() for code_block in soup.find_all('div', {"class":"highlight"})]
    content = soup.get_text(' ', strip=True).replace('“', '"').replace('”', '"').replace('’', "'").replace('^', '&#94;')
    return content
    
def extract(article):
    article_data = {
        "title": article.title,
        "slug": article.slug,
        "content": process_html(article.content),
        "summary": article.short_summary,
        "created": int(article.date.timestamp()),
        "tags": [tag.slug for tag in article.tags],
        "url": article.url,
    }
    return article_data

def index_generator(generator):

    index_name = generator.settings.get('ALGOLIA_INDEX_NAME', None)
    app_id = generator.settings.get('ALGOLIA_APP_ID', None)
    admin_api_key = generator.settings.get('ALGOLIA_ADMIN_API_KEY', None)
    
    if not any([index_name, app_id, admin_api_key]):
        logger.error("Missing parameters")
        return

    client = SearchClient.create(app_id, admin_api_key)
    index = client.init_index(index_name)

    settings = {
        'searchableAttributes': [
            'title',
            'content, summary',
            'unordered(tags)'
        ],
        "ranking": [
            "desc(created)",
        ],
        "customRanking": [
            "desc(title)",
            "desc(summary)",
            "desc(content)"
        ]
    }
    index.set_settings(settings)

    articles = generator.articles
    current_ids = set()
    for article in articles:
        article_data = extract(article)
        object_id = hashlib.sha256(str(article_data["slug"]).encode('utf-8')).hexdigest()
        article_data["objectID"] = object_id
        current_ids.add(object_id)
        index.save_object(article_data)
        logger.info(f"Indexing {article_data['url']}")
    pass


def register():
    signals.initialized.connect(init_default_config)
    signals.article_generator_finalized.connect(index_generator)