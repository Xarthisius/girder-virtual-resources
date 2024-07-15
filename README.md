## Girder Virtual Resources
Girder Plugin exposing physical folders and files as Girder objects.

### How does it work?

This plugin introduces an abstraction layer atop Girder's REST API via `rest.*.before` events. It enhances the fundamental Folder model by incorporating two additional attributes: `fsPath` (accessible to administrators) and `isMapping` (accessible to users possessing READ permissions for the folder). The `fsPath` attribute enables the mapping of an existing Folder to a physical directory, thereby designating it as a root virtual folder. Subsequent REST operations intended to list, read, delete, etc., any root virtual folder or its contents are intercepted and translated into corresponding filesystem operations using the appropriate path.

### How to use it?

To begin the setup process for the plugin, initiate the installation by executing the following command:

```
pip install girder-virtual-resources
```

After successfully installing the plugin, proceed to activate it. This can be accomplished through the Admin console of Girder. Navigate to the console, locate the plugin management section, and enable the `Virtual Resources` plugin to complete the setup.