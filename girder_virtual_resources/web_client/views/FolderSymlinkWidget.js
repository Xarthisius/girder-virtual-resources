import FolderSymlinkWidgetTemplate from '../templates/folderSymlinkWidget.pug';

const $ = girder.$;
const _ = girder._;
const View = girder.views.View;
const { getCurrentUser } = girder.auth;

var FolderSymlinkWidget = View.extend({
    initialize: function (settings) {
        this.folder = settings.folder;
    },

    render: function () {
        const currentUser = getCurrentUser();
        const isAdmin = currentUser && currentUser.get('admin');
        if (!this.folder || !isAdmin) {
            this.$el.empty();
            return this;
        }
        const isSymlink = this.folder.get('isSymlink') ? true : false;
        this.$el.html(FolderSymlinkWidgetTemplate({
            isSymlink: isSymlink,
            isAdmin: isAdmin,
            targetId: this.folder.get('symlinkTargetId') || ''
        }));
        this.$('.g-symlink-target').hide();
        if (this.folder && isAdmin) {
            this.$('input#enable-symlink').prop('checked', isSymlink);
            this.$('input#g-symlink-target-id').val(this.folder.get('symlinkTargetId') || null);
            if (isSymlink) {
                this.$('.g-symlink-target').show();
            }
        }
        this.$('input#enable-symlink').on('change', (evt) => {
            if (evt.target.checked) {
                this.$('.g-symlink-target').show();
            } else {
                this.$('.g-symlink-target').hide();
            }
            this.$('input#g-symlink-target-id').val(this.folder.get('symlinkTargetId') || null);
        });
        return this;
    }
});

export default FolderSymlinkWidget;
