"""Provide interfaces to manage SBG contexts and pushing to SBG app store"""
#  Copyright (c) 2019 Seven Bridges. See LICENSE

import sevenbridges as sbg

from .version import __version__


def get_profile(profile):
    api = sbg.Api(config=sbg.Config(profile))
    # Least disruptive way to add in our user agent
    api.headers["User-Agent"] = "sbpush/{} via {}".format(__version__, api.headers["User-Agent"])
    return api
