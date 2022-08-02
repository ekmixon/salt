"""
Feature flags
"""
import logging

log = logging.getLogger(__name__)


class Features:
    def __init__(self, _features=None):
        self.features = {} if _features is None else _features
        self.setup = False

    def setup_features(self, opts):
        if not self.setup:
            self.features.update(opts.get("features", {}))
        else:
            log.warn("Features already setup")

    def get(self, key, default=None):
        return self.features.get(key, default)


features = Features()
setup_features = features.setup_features
