from urllib.parse import urlparse
import unicodedata
from shop import login_manager
from shop.models import User


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def url_has_allowed_host_and_scheme(url, allowed_hosts):
    if url is not None:
        url = url.strip()
    if not url:
        return False
    return more_url_checks(url, allowed_hosts) and \
        more_url_checks(url.replace('\\', '/'), allowed_hosts)


def more_url_checks(url, allowed_hosts):
    if url.startswith("///"):
        return False
    if unicodedata.category(url[0])[0] == 'C':
        return False

    parsed_url = urlparse(url)
    if not parsed_url.netloc and parsed_url.scheme:
        return False
    
    scheme = parsed_url.scheme
    valid_schemes = ['http', 'https']
    if not parsed_url.scheme and parsed_url.netloc:
        scheme = 'http'
    return ((not parsed_url.netloc or parsed_url.netloc in allowed_hosts) and
            (not scheme or scheme in valid_schemes))
