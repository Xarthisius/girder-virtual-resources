#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path

from girder.constants import AccessType
from girder.models.folder import Folder
from girder.plugin import GirderPlugin, registerPluginStaticContent

from .rest.virtual_file import VirtualFile
from .rest.virtual_folder import VirtualFolder
from .rest.virtual_item import VirtualItem
from .rest.virtual_resource import VirtualResource


class VirtualResourcesPlugin(GirderPlugin):
    DISPLAY_NAME = "Virtual Resources"

    def load(self, info):
        from girder.api.v1.folder import (
            Folder as FolderResource,  # noqa: F401 circular import
        )

        Folder().exposeFields(level=AccessType.READ, fields={"isMapping", "isSymlink"})
        Folder().exposeFields(
            level=AccessType.SITE_ADMIN, fields={"fsPath", "symlinkTargetId"}
        )
        for endpoint in (FolderResource.updateFolder, FolderResource.createFolder):
            (
                endpoint.description.param(
                    "isMapping",
                    "Whether this is a virtual folder.",
                    required=False,
                    dataType="boolean",
                )
                .param("fsPath", "Local filesystem path it maps to.", required=False)
                .param(
                    "isSymlink",
                    "Set to true to create a symlink to another folder.",
                    required=False,
                    dataType="boolean",
                )
                .param(
                    "symlinkTargetId",
                    "The ID of the target folder to which this folder will be a symlink.",
                    required=False,
                    dataType="string",
                )
            )

        info["apiRoot"].virtual_item = VirtualItem()
        virtual_file = VirtualFile()
        info["apiRoot"].virtual_file = virtual_file
        info["apiRoot"].virtual_folder = VirtualFolder()
        info["apiRoot"].virtual_resource = VirtualResource()

        registerPluginStaticContent(
            plugin="virtual_resources",
            css=["/style.css"],
            js=["/girder-plugin-virtual-resources.umd.cjs"],
            staticDir=Path(__file__).parent / "web_client" / "dist",
            tree=info["serverRoot"],
        )
