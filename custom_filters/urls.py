from urllib.parse import urlparse

def hostname(uri):
    url = urlparse(uri)
    return url.netloc
