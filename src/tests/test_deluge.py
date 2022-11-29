from base64 import b64encode
from sonarr_announced.deluge import get_deluge_client
from sonarr_announced.scrapers.tl import (
    get_torrent_data as get_tl_torrent_data,
)
from sonarr_announced.sonarr import get_sonarr_client
from sonarr_announced.trackers.tl import (
    get_name_url_from_msg as get_name_url_from_tl_msg,
    get_torrent_id_from_url as get_torrent_id_from_tl_url,
)
from sonarr_announced import config
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

sonarr_client = get_sonarr_client()
deluge_client = get_deluge_client()
cfg = config.init()


def test_connect():
    deluge_client.connect_if_necessary()
    assert deluge_client.connected


def test_get_torrent_data():
    deluge_client.connect_if_necessary()
    msg = "\x02\x0300,04New Torrent Announcement:\x02\x0300,12 <TV :: Episodes HD>  Name:'Handmade Britains Best Woodworker S02E06 1080p HDTV H264-DARKFLiX' uploaded by 'Anonymous' - \x0301,15 https://www.torrentleech.org/torrent/240921997"
    name, url = get_name_url_from_tl_msg(msg)
    print(deluge_client.add_torrent(name, get_torrent_id_from_tl_url(url)))
    stop
