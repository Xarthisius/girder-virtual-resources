#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pathlib
from operator import itemgetter
import shutil

from girder import events
from girder.api import access
from girder.constants import TokenScope, AccessType
from girder.exceptions import ValidationException
from girder.models.file import File
from girder.models.folder import Folder
from girder.models.item import Item

from . import VirtualObject, validate_event


class VirtualItem(VirtualObject):
    def __init__(self):
        super(VirtualItem, self).__init__()
        self.resourceName = "virtual_item"
        name = "virtual_resources"

        events.bind("rest.get.item.before", name, self.get_child_items)
        events.bind("rest.post.item.before", name, self.create_item)
        events.bind("rest.get.item/:id.before", name, self.get_item_info)
        events.bind("rest.put.item/:id.before", name, self.rename_item)
        events.bind("rest.delete.item/:id.before", name, self.remove_item)
        events.bind("rest.post.item/:id/copy.before", name, self.copy_item)
        # events.bind("rest.get.item/:id/download.before", name, self.file_download)  # in Vfile
        events.bind("rest.get.item/:id/files.before", name, self.get_child_files)
        # PUT/DELETE /item/:id/metadata
        events.bind("rest.get.item/:id/rootpath.before", name, self.item_root_path)

    @access.public(scope=TokenScope.DATA_READ)
    @validate_event(level=AccessType.READ)
    def get_child_items(self, event, path, root, user=None):
        response = [
            Item().filter(self.vItem(obj, root), user=user)
            for obj in path.iterdir()
            if obj.is_file()
        ]
        event.preventDefault().addResponse(sorted(response, key=itemgetter("name")))

    @access.user(scope=TokenScope.DATA_WRITE)
    @validate_event(level=AccessType.WRITE)
    def create_item(self, event, path, root, user=None):
        params = event.info["params"]
        new_path = path / params["name"]
        with open(new_path, "a"):
            os.utime(new_path.as_posix())
        event.preventDefault().addResponse(
            Item().filter(self.vItem(new_path, root), user=user)
        )

    @access.public(scope=TokenScope.DATA_READ)
    @validate_event(level=AccessType.READ)
    def get_item_info(self, event, path, root, user=None):
        event.preventDefault().addResponse(
            Item().filter(self.vItem(path, root), user=user)
        )

    @access.user(scope=TokenScope.DATA_WRITE)
    @validate_event(level=AccessType.WRITE)
    def rename_item(self, event, path, root, user=None):
        self.is_file(path, root["_id"])
        new_path = path.with_name(event.info["params"]["name"])
        path.rename(new_path)
        event.preventDefault().addResponse(
            Item().filter(self.vItem(new_path, root), user=user)
        )

    @access.user(scope=TokenScope.DATA_WRITE)
    @validate_event(level=AccessType.WRITE)
    def remove_item(self, event, path, root, user=None):
        self.is_file(path, root["_id"])
        path.unlink()
        event.preventDefault().addResponse({"message": "Deleted item %s." % path.name})

    @access.user(scope=TokenScope.DATA_WRITE)
    @validate_event(level=AccessType.WRITE)
    def copy_item(self, event, path, root, user=None):
        # TODO: folderId is not passed properly, but that's vanilla girder's fault...
        self.is_file(path, root["_id"])
        name = event.info["params"].get("name") or path.name  # TODO: cross origin?
        path, new_root_id = self.path_from_id(event.info["params"]["folderId"])
        if str(new_root_id) != str(root["_id"]):
            new_root = Folder().load(new_root_id, user=user, level=AccessType.WRITE)
        else:
            new_root = root
        new_path = path / name
        shutil.copy(path.as_posix(), new_path.as_posix())
        event.preventDefault().addResponse(
            Item().filter(self.vItem(new_path, new_root), user=user)
        )

    @access.public(scope=TokenScope.DATA_READ)
    @validate_event(level=AccessType.READ)
    def get_child_files(self, event, path, root, user=None):
        event.preventDefault().addResponse(
            [File().filter(self.vFile(path, root), user=user)]
        )

    @access.public(scope=TokenScope.DATA_READ)
    @validate_event(level=AccessType.READ)
    def item_root_path(self, event, path, root, user=None):
        root_path = pathlib.Path(root["fsPath"])
        response = [
            dict(type="item", object=Item().filter(self.vItem(path, root), user=user))
        ]
        path = path.parent
        while path != root_path:
            response.append(
                dict(
                    type="folder",
                    object=Folder().filter(self.vFolder(path, root), user=user),
                )
            )
            path = path.parent

        response.append(dict(type="folder", object=Folder().filter(root, user=user)))
        girder_rootpath = Folder().parentsToRoot(root, user=user)
        response += girder_rootpath[::-1]
        response.pop(0)
        event.preventDefault().addResponse(response[::-1])
