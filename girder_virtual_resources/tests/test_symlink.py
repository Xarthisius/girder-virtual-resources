import pytest
from bson.objectid import ObjectId
from girder.exceptions import ValidationException
from girder.models.folder import Folder
from pytest_girder.assertions import assertStatus, assertStatusOk


@pytest.mark.plugin("virtual_resources")
def test_symlink(server, user, admin, private_folder, public_folder):
    # create a single item and a folder in private_folder
    req = server.request(
        method="POST",
        path="/folder",
        user=user,
        params={
            "name": "subfolder",
            "parentType": "folder",
            "parentId": private_folder["_id"],
        },
    )
    assertStatusOk(req)
    subfolder = req.json
    req = server.request(
        method="POST",
        path="/item",
        user=user,
        params={"name": "item", "folderId": private_folder["_id"]},
    )
    assertStatusOk(req)
    item = req.json

    # create a symlink to the item in the public folder
    req = server.request(
        method="POST",
        path="/folder",
        user=admin,
        params={
            "name": "symlink_folder",
            "parentType": "folder",
            "parentId": public_folder["_id"],
            "isSymlink": True,
            "symlinkTargetId": private_folder["_id"],
        },
    )
    assertStatusOk(req)
    symlink_folder = req.json

    # check if folder listing works
    req = server.request(
        method="GET",
        path="/folder",
        params={"parentType": "folder", "parentId": symlink_folder["_id"]},
        user=user,
    )
    assertStatusOk(req)
    assert len(req.json) == 1
    assert req.json[0]["_id"] == subfolder["_id"]

    # check if item listing works
    req = server.request(
        method="GET",
        path="/item",
        params={"folderId": symlink_folder["_id"]},
        user=user,
    )
    assertStatusOk(req)
    assert len(req.json) == 1
    assert req.json[0]["_id"] == item["_id"]

    req = server.request(
        method="GET",
        path="/resource/lookup",
        params={
            "path": f"/collection/test_collection/{public_folder['name']}/symlink_folder/subfolder"
        },
        user=user,
    )
    assertStatusOk(req)
    assert req.json["_id"] == subfolder["_id"]


@pytest.mark.plugin("virtual_resources")
def test_validation(server, admin, private_folder, public_folder):
    with pytest.raises(ValidationException) as exc:
        private_folder["isSymlink"] = "blah"
        Folder().save(private_folder)
    assert "isSymlink must be a boolean" in str(exc.value)

    with pytest.raises(ValidationException) as exc:
        private_folder["isSymlink"] = True
        private_folder["symlinkTargetId"] = "notanid"
        Folder().save(private_folder)
    assert "symlinkTargetId must be an ObjectId" in str(exc.value)

    req = server.request(
        method="PUT",
        path=f"/folder/{private_folder['_id']}",
        user=admin,
        params={
            "isSymlink": True,
            "symlinkTargetId": "notanid",
        },
    )
    assertStatus(req, 400)
    assert "symlinkTargetId must be an ObjectId" in req.json["message"]

    with pytest.raises(ValidationException) as exc:
        private_folder["isSymlink"] = True
        private_folder["symlinkTargetId"] = private_folder["_id"]
        Folder().save(private_folder)
    assert "A folder may not symlink to itself." in str(exc.value)

    with pytest.raises(ValidationException) as exc:
        private_folder["isSymlink"] = True
        private_folder["symlinkTargetId"] = ObjectId()
        Folder().save(private_folder)
    assert "symlinkTargetId must reference a valid folder" in str(exc.value)


@pytest.mark.plugin("virtual_resources")
def test_no_new_children(server, admin, private_folder, public_folder):
    req = server.request(
        method="PUT",
        path=f"/folder/{private_folder['_id']}",
        user=admin,
        params={
            "isSymlink": True,
            "symlinkTargetId": public_folder["_id"],
        },
    )
    assertStatusOk(req)

    req = server.request(
        method="POST",
        path="/item",
        user=admin,
        params={"name": "item", "folderId": private_folder["_id"]},
    )
    assertStatus(req, 400)
    assert "You may not place items under a symlink folder." in req.json["message"]

    req = server.request(
        method="POST",
        path="/folder",
        user=admin,
        params={
            "name": "subfolder",
            "parentType": "folder",
            "parentId": private_folder["_id"],
        },
    )
    assertStatus(req, 400)
    assert "You may not place folders under a symlink folder." in req.json["message"]


@pytest.mark.plugin("virtual_resources")
def test_no_child_items(server, admin, private_folder, public_folder):
    req = server.request(
        method="POST",
        path="/item",
        user=admin,
        params={"name": "item", "folderId": private_folder["_id"]},
    )
    assertStatusOk(req)

    req = server.request(
        method="PUT",
        path=f"/folder/{private_folder['_id']}",
        user=admin,
        params={
            "isSymlink": True,
            "symlinkTargetId": public_folder["_id"],
        },
    )
    assertStatus(req, 400)
    assert "Symlink folders may not contain child items." in req.json["message"]


@pytest.mark.plugin("virtual_resources")
def test_no_child_folders(server, admin, private_folder, public_folder):
    req = server.request(
        method="POST",
        path="/folder",
        user=admin,
        params={
            "name": "subfolder",
            "parentType": "folder",
            "parentId": private_folder["_id"],
        },
    )
    assertStatusOk(req)

    req = server.request(
        method="PUT",
        path=f"/folder/{private_folder['_id']}",
        user=admin,
        params={
            "isSymlink": True,
            "symlinkTargetId": public_folder["_id"],
        },
    )
    assertStatus(req, 400)
    assert "Symlink folders may not contain child folders." in req.json["message"]


@pytest.mark.plugin("virtual_resources")
def test_no_target_if_not_symlink(server, admin, private_folder, public_folder):
    req = server.request(
        method="PUT",
        path=f"/folder/{private_folder['_id']}",
        user=admin,
        params={
            "isSymlink": False,
            "symlinkTargetId": public_folder["_id"],
        },
    )
    assertStatusOk(req)
    private_folder = req.json
    assert private_folder.get("symlinkTargetId") is None
