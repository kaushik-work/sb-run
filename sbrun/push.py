#  Copyright (c) 2019 Seven Bridges. See LICENSE

import sevenbridges.errors as sbgerr

from ruamel.yaml import YAML

from .profiles import get_profile

import logging
logger = logging.getLogger(__name__)
logging.getLogger("sevenbridges.http.client").propagate = False
logging.getLogger("urllib3.connectionpool").propagate = False

fast_load = YAML(typ='safe')


def push_to_sbpla(cwl: dict, commit_message: str,
                  profile: str=None, user: str=None, project: str=None, app_id: str=None):

    app_path = f"{user}/{project}/{app_id}"

    api = get_profile(profile)

    cwl["sbg:revisionNotes"] = commit_message
    try:
        app = api.apps.get(app_path)
        logger.debug("Creating revised app: {}".format(app_path))
        return api.apps.create_revision(
            id=app_path,
            raw=cwl,
            revision=app.revision + 1
        )
    except sbgerr.NotFound:
        logger.debug("Creating new app: {}".format(app_path))
        return api.apps.install_app(
            id=app_path,
            raw=cwl
        )
