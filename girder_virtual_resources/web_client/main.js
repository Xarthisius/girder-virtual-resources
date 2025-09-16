// I love javascript

import './stylesheets/blank.styl';
import FolderSymlinkWidget from './views/FolderSymlinkWidget';

const { getCurrentUser } = girder.auth;
const { wrap } = girder.utilities.PluginUtils;
const FolderListWidget = girder.views.widgets.FolderListWidget;
const EditFolderWidget = girder.views.widgets.EditFolderWidget;

wrap(FolderListWidget, 'render', function (render) {
    render.call(this);

    this.collection.each((folder) => {
        console.log('Folder name:', folder.cid, folder.get('name'), folder.get('isSymlink'));
        // if isSymlink change icon
        if (folder.get('isSymlink')) {
            this.$(`.g-folder-list-link[g-folder-cid="${folder.cid}"] i.icon-folder`)
              .removeClass('icon-folder').addClass('icon-export');
        }
    });

    return this;
});


wrap(EditFolderWidget, 'render', function (render) {
    render.call(this);

    const folderSymlinkWidget = new FolderSymlinkWidget({
        parentView: this,
        folder: this.folder
    }).render();

    this.$('.modal-body>.g-validation-failed-message').before(folderSymlinkWidget.el);

    return this;
});

wrap(EditFolderWidget, 'updateFolder', function (updateFolder) {
    var fields = arguments[1];
    const currentUser = getCurrentUser();
    if (currentUser && currentUser.get('admin')) {
        fields.isSymlink = this.$('input#enable-symlink').is(':checked');
        fields.symlinkTargetId = fields.isSymlink ? this.$('input#g-symlink-target-id').val() : null;
        fields.symlinkTargetId = fields.symlinkTargetId === '' ? null : fields.symlinkTargetId;
    }
    updateFolder.call(this, fields);
    return this;
});

wrap(EditFolderWidget, 'createFolder', function (createFolder) {
    var fields = arguments[1];
    const currentUser = getCurrentUser();
    if (currentUser && currentUser.get('admin')) {
        fields.isSymlink = this.$('input#enable-symlink').is(':checked');
        fields.symlinkTargetId = fields.isSymlink ? this.$('input#g-symlink-target-id').val() : null;
        fields.symlinkTargetId = fields.symlinkTargetId === '' ? null : fields.symlinkTargetId;
    }
    createFolder.call(this, fields);
    return this;
});
