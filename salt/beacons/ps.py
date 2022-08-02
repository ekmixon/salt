"""
Send events covering process status
"""
import logging

try:
    import salt.utils.psutil_compat as psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


log = logging.getLogger(__name__)  # pylint: disable=invalid-name

__virtualname__ = "ps"


def __virtual__():
    return (
        __virtualname__
        if HAS_PSUTIL
        else (False, "cannot load ps beacon: psutil not available")
    )


def validate(config):
    """
    Validate the beacon configuration
    """
    if not isinstance(config, list):
        return False, ("Configuration for ps beacon must be a list.")
    _config = {}
    list(map(_config.update, config))

    if "processes" not in _config:
        return False, ("Configuration for ps beacon requires processes.")
    return (
        (True, "Valid beacon configuration")
        if isinstance(_config["processes"], dict)
        else (False, "Processes for ps beacon must be a dictionary.")
    )


def beacon(config):
    """
    Scan for processes and fire events

    Example Config

    .. code-block:: yaml

        beacons:
          ps:
            - processes:
                salt-master: running
                mysql: stopped

    The config above sets up beacons to check that
    processes are running or stopped.
    """
    ret = []
    procs = []
    for proc in psutil.process_iter():
        try:
            _name = proc.name()
        except psutil.NoSuchProcess:
            # The process is now gone
            continue
        if _name not in procs:
            procs.append(_name)

    _config = {}
    list(map(_config.update, config))

    for process in _config.get("processes", {}):
        ret_dict = {}
        if _config["processes"][process] == "running":
            if process in procs:
                ret_dict[process] = "Running"
                ret.append(ret_dict)
        elif _config["processes"][process] == "stopped":
            if process not in procs:
                ret_dict[process] = "Stopped"
                ret.append(ret_dict)
        elif process not in procs:
            ret_dict[process] = False
            ret.append(ret_dict)
    return ret
