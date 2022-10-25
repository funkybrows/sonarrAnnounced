import datetime
import logging

from sonarrAnnounced import config, db, sonarr, utils

cfg = config.init()

############################################################
# Tracker Configuration
############################################################
name = "TorrentLeech"
irc_host = "irc.torrentleech.org"
# irc_port = 7021
irc_port = 7011
irc_channel = "#tlannounces"
# irc_tls = True
irc_tls = False
# irc_tls_verify = True
irc_tls_verify = False

# these are loaded by init
cookies = None

logger = logging.getLogger(name.upper())
logger.setLevel(logging.DEBUG)


############################################################
# Tracker Framework (all trackers must follow)
############################################################
# Parse announcement message
@db.db_session
def parse(announcement):
    global name

    if "TV" not in announcement:
        return
    decolored = utils.strip_irc_color_codes(announcement)

    # extract required information from announcement
    torrent_title = utils.substr(decolored, "] ", " (", True)
    torrent_id = utils.get_id(decolored, 0)

    # pass announcement to sonarr
    if torrent_id is not None and torrent_title is not None:
        download_link = get_torrent_link(
            torrent_id, utils.replace_spaces(torrent_title, ".")
        )

        announced = db.Announced(
            date=datetime.datetime.now(),
            title=utils.replace_spaces(torrent_title, "."),
            indexer=name,
            torrent=download_link,
        )
        approved = sonarr.wanted(torrent_title, download_link, name)
        if approved:
            logger.debug("Sonarr approved release: %s", torrent_title)
            snatched = db.Snatched(
                date=datetime.datetime.now(),
                title=utils.replace_spaces(torrent_title, "."),
                indexer=name,
                torrent=download_link,
            )
        else:
            logger.debug("Sonarr rejected release: %s", torrent_title)


# Generate MITM torrent link
def get_torrent_link(torrent_id, torrent_name):
    host = ""
    if cfg["server.host"].startswith("0.0."):
        host = "localhost"
    else:
        host = cfg["server.host"]

    download_link = "http://{}:{}/mitm/{}/{}/{}".format(
        host,
        cfg["server.port"],
        name,
        torrent_id,
        utils.replace_spaces(torrent_name, "."),
    )
    return download_link


# Generate real download link
def get_real_torrent_link(torrent_id, torrent_name):
    torrent_link = "https://hd-torrents.org/download.php?id={}&f={}.torrent".format(
        torrent_id, torrent_name
    )
    return torrent_link


# Get cookies (MITM will request this)
def get_cookies():
    return cookies


# Initialize tracker
def init():
    global cookies

    # tmp = cfg["{}.cookies".format(name.lower())]
    tmp = None
    # check cookies were supplied
    if not tmp:
        return True

    tmp = tmp.replace(" ", "").rstrip(";")
    cookies = dict(x.split(":") for x in tmp.split(";"))
    return True
