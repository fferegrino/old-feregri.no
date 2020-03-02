from pelican.generators import CachingGenerator
from pelican.utils import process_translations, order_content
from pelican.contents import Content
from pelican import signals
from itertools import chain, groupby
import logging


class CollectionItem(Content):
    mandatory_properties = ('title',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._save_as = None
        self._url = None

    def _expand_settings(self, key):
        klass = 'draft_page' if self.status == 'draft' else None
        return super()._expand_settings(key, klass)


    @property
    def save_as(self):
        return self._save_as

    @save_as.setter
    def save_as(self, value):
        self._save_as = value

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value

class CollectionPagesGenerator(CachingGenerator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        signals.page_generator_init.send(self)
        self.logger = logging.getLogger(__name__)
        self.collections = {
            collection["folder"]: [] for collection in self.settings["COLLECTIONS"]
        }
        self.collection_settings = { collection["folder"]:collection  for collection in self.settings["COLLECTIONS"] }

    def generate_context(self):
        for folder, item_list in self.collections.items():
            for f in self.get_files(folder):
                page = self.get_cached_data(f, None)
                if page is None:
                    try:
                        page = self.readers.read_file(
                            base_path=self.path, path=f, content_class=CollectionItem,
                            context=self.context,
                            preread_signal=signals.page_generator_preread,
                            preread_sender=self,
                            context_signal=signals.page_generator_context,
                            context_sender=self)
                        page.save_as = self.collection_settings[folder]["item_save_as"].format(slug=page.slug)
                        page.url = self.collection_settings[folder]["item_url"].format(slug=page.slug)
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

                item_list.append(page)

        self._update_context(('collections',))
        self.save_cache()
        self.readers.save_cache()
        signals.page_generator_finalized.send(self)

    def generate_output(self, writer):
        for folder, items in self.collections.items():
            for item in items:
                signals.page_generator_write_page.send(self, content=item)
                writer.write_file(
                    item.save_as, self.get_template(self.collection_settings[folder]["item_template"]),
                    self.context, item=item,
                    relative_urls=self.settings['RELATIVE_URLS'],
                    override_output=hasattr(item, 'override_save_as'),
                    url=item.url)
            self.generate_index(writer, folder)
        signals.page_writer_finalized.send(self, writer=writer)


    def generate_index(self, writer, folder):
        collection_settings = self.collection_settings[folder]
        index_location = collection_settings.get("index_location", collection_settings["folder"])
        collection_name = collection_settings["name"]
        writer.write_file(
            f"{index_location}/index.html", self.get_template("collection"), self.context, collection=self.collections[folder], collection_name=collection_name)

    def refresh_metadata_intersite_links(self):
        for folder, items in self.collections.items():
            for item in items:
                if hasattr(item, 'refresh_metadata_intersite_links'):
                    item.refresh_metadata_intersite_links()


def add_collection_generator(pelican_object):
    return CollectionPagesGenerator

def register():
    signals.get_generators.connect(add_collection_generator)