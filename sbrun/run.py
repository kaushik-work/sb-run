#  Copyright (c) 2019 Seven Bridges. See LICENSE

import time

import sevenbridges.errors as sbgerr

from .profiles import get_profile

import logging
logger = logging.getLogger(__name__)
logging.getLogger("sevenbridges.http.client").propagate = False
logging.getLogger("urllib3.connectionpool").propagate = False


def run_on_sbpla(profile: str, user: str, project: str, app_id: str,
                 old_task_id=None):

    app_path = f"{user}/{project}/{app_id}"
    user_project = f"{user}/{project}"

    api = get_profile(profile)
    if old_task_id is not None:
        old_task = api.tasks.get(old_task_id)
        task = api.tasks.create(name=f"{time.time()}",
                                project=user_project, app=app_path,
                                inputs=old_task.inputs,
                                run=True)
    else:
        task = api.tasks.create(name=f"{time.time()}", project=user_project, app=app_path, run=False)

    return task
