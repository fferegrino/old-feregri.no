from pelican.generators import CachingGenerator
from pelican.utils import process_translations, order_content
from pelican.contents import Content
from pelican import signals
from itertools import chain, groupby
import logging


class Book(Content):
    mandatory_properties = ('title',)
    allowed_statuses = ('published', 'hidden', 'draft')
    default_status = 'published'
    default_template = 'book'

    def _expand_settings(self, key):
        klass = 'draft_page' if self.status == 'draft' else None
        return super()._expand_settings(key, klass)

class BookPagesGenerator(CachingGenerator):

    def __init__(self, *args, **kwargs):
        self.pages = []
        self.translations = []
        self.hidden_pages = []
        self.hidden_translations = []
        self.draft_pages = []
        self.draft_translations = []
        super().__init__(*args, **kwargs)
        signals.page_generator_init.send(self)
        self.logger = logging.getLogger(__name__)

    def generate_context(self):
        all_pages = []
        hidden_pages = []
        draft_pages = []
        self.logger.info(f"PAGE_SAVE_AS {self.settings['PAGE_URL']}")
        for f in self.get_files(self.settings['BOOKS_PATH']):
            page = self.get_cached_data(f, None)
            if page is None:
                try:
                    page = self.readers.read_file(
                        base_path=self.path, path=f, content_class=Book,
                        context=self.context,
                        preread_signal=signals.page_generator_preread,
                        preread_sender=self,
                        context_signal=signals.page_generator_context,
                        context_sender=self)
                except Exception as e:
                    self.logger.error(
                        'Could not process %s\n%s', f, e,
                        exc_info=self.settings.get('DEBUG', False))
                    self._add_failed_source_path(f)
                    continue

                if not page.is_valid():
                    self._add_failed_source_path(f)
                    continue

                self.cache_data(f, page)

            if page.status == "published":
                all_pages.append(page)
            elif page.status == "hidden":
                hidden_pages.append(page)
            elif page.status == "draft":
                draft_pages.append(page)
            self.add_source_path(page)
            self.add_static_links(page)

        def _process(pages):
            origs, translations = process_translations(
                pages, translation_id=self.settings['PAGE_TRANSLATION_ID'])
            origs = order_content(origs, self.settings['PAGE_ORDER_BY'])
            return origs, translations

        self.pages, self.translations = _process(all_pages)
        self.hidden_pages, self.hidden_translations = _process(hidden_pages)
        self.draft_pages, self.draft_translations = _process(draft_pages)

        self._update_context(('pages', 'hidden_pages', 'draft_pages'))

        self.save_cache()
        self.readers.save_cache()
        signals.page_generator_finalized.send(self)

    

    def generate_tags(self, write):
        """Generate Tags pages."""
        tag_template = self.get_template('tag')
        for tag, articles in self.tags.items():
            dates = [article for article in self.dates if article in articles]
            write(tag.save_as, tag_template, self.context, tag=tag,
                  url=tag.url, articles=articles, dates=dates,
                  template_name='tag', blog=True, page_name=tag.page_name,
                  all_articles=self.articles)

    def generate_output(self, writer):
        for page in chain(self.translations, self.pages,
                          self.hidden_translations, self.hidden_pages,
                          self.draft_translations, self.draft_pages):
            signals.page_generator_write_page.send(self, content=page)
            writer.write_file(
                page.save_as, self.get_template(page.template),
                self.context, page=page,
                relative_urls=self.settings['RELATIVE_URLS'],
                override_output=hasattr(page, 'override_save_as'),
                url=page.url)
        signals.page_writer_finalized.send(self, writer=writer)

    def refresh_metadata_intersite_links(self):
        for e in chain(self.pages,
                       self.hidden_pages,
                       self.hidden_translations,
                       self.draft_pages,
                       self.draft_translations):
            if hasattr(e, 'refresh_metadata_intersite_links'):
                e.refresh_metadata_intersite_links()


def add_book_pages_generator(pelican_object):
    return BookPagesGenerator

def register():
    signals.get_generators.connect(add_book_pages_generator)