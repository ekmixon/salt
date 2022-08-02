"""
A simple beacon to watch journald for specific entries
"""
import logging

import salt.utils.data

try:
    import systemd.journal  # pylint: disable=no-name-in-module

    HAS_SYSTEMD = True
except ImportError:
    HAS_SYSTEMD = False


log = logging.getLogger(__name__)

__virtualname__ = "journald"


def __virtual__():
    return __virtualname__ if HAS_SYSTEMD else False


def _get_journal():
    """
    Return the active running journal object
    """
    if "systemd.journald" in __context__:
        return __context__["systemd.journald"]
    __context__["systemd.journald"] = systemd.journal.Reader()
    # get to the end of the journal
    __context__["systemd.journald"].seek_tail()
    __context__["systemd.journald"].get_previous()
    return __context__["systemd.journald"]


def validate(config):
    """
    Validate the beacon configuration
    """
    if not isinstance(config, list):
        return (False, "Configuration for journald beacon must be a list.")
    _config = {}
    list(map(_config.update, config))

    return next(
        (
            (
                False,
                "Services configuration for journald beacon "
                "must be a list of dictionaries.",
            )
            for name in _config.get("services", {})
            if not isinstance(_config["services"][name], dict)
        ),
        (True, "Valid beacon configuration"),
    )


def beacon(config):
    """
    The journald beacon allows for the systemd journal to be parsed and linked
    objects to be turned into events.

    This beacons config will return all sshd jornal entries

    .. code-block:: yaml

        beacons:
          journald:
            - services:
                sshd:
                  SYSLOG_IDENTIFIER: sshd
                  PRIORITY: 6
    """
    ret = []
    journal = _get_journal()

    _config = {}
    list(map(_config.update, config))

    while True:
        cur = journal.get_next()
        if not cur:
            break

        for name in _config.get("services", {}):
            n_flag = 0
            for key in _config["services"][name]:
                if isinstance(key, str):
                    key = salt.utils.data.decode(key)
                if key in cur and _config["services"][name][key] == cur[key]:
                    n_flag += 1
            if n_flag == len(_config["services"][name]):
                # Match!
                sub = salt.utils.data.simple_types_filter(cur)
                sub.update({"tag": name})
                ret.append(sub)
    return ret
