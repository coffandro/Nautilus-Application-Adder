/* extension.js
 *
 * GNOME Shell Extension: Nautilus Application Adder
 * 
 * This extension automatically installs and manages the Python Nautilus extension
 * that adds right-click context menu entries to add/remove executables from your 
 * applications list.
 *
 * When enabled: Installs the Python Nautilus extension and restarts Nautilus
 * When disabled: Removes the Python Nautilus extension and restarts Nautilus
 */

import GLib from 'gi://GLib';
import Gio from 'gi://Gio';

import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class NautilusApplicationAdderExtension extends Extension {
    constructor(metadata) {
        super(metadata);
        this._extensionDir = null;
        this._nautilusExtensionDir = null;
        this._nautilusSubDir = null;
    }

    enable() {
        this._extensionDir = this.path;
        const home = GLib.get_home_dir();
        this._nautilusExtensionDir = GLib.build_filenamev([home, '.local', 'share', 'nautilus-python', 'extensions']);
        this._nautilusSubDir = GLib.build_filenamev([this._nautilusExtensionDir, 'NautilusApplications']);

        this._installNautilusExtension();
    }

    disable() {
        this._removeNautilusExtension();
        this._extensionDir = null;
        this._nautilusExtensionDir = null;
        this._nautilusSubDir = null;
    }

    _installNautilusExtension() {
        try {
            // Create directories if they don't exist
            this._ensureDirectory(this._nautilusExtensionDir);
            this._ensureDirectory(this._nautilusSubDir);

            // Copy extension files
            this._copyFile('NautilusApplications.py', this._nautilusSubDir);
            this._copyFile('window.py', this._nautilusSubDir);
            this._copyFile('NautliusApplications-runner.py', this._nautilusExtensionDir);

            // Create config file if it doesn't exist
            this._createConfigFile();

            // Restart Nautilus to load the extension
            this._restartNautilus();

            console.log('Nautilus Application Adder: Extension installed successfully');
        } catch (e) {
            console.error(`Nautilus Application Adder: Failed to install extension: ${e.message}`);
        }
    }

    _removeNautilusExtension() {
        try {
            // Remove the extension files
            this._deleteFile(GLib.build_filenamev([this._nautilusExtensionDir, 'NautliusApplications-runner.py']));
            this._deleteDirectory(this._nautilusSubDir);

            // Restart Nautilus to unload the extension
            this._restartNautilus();

            console.log('Nautilus Application Adder: Extension removed successfully');
        } catch (e) {
            console.error(`Nautilus Application Adder: Failed to remove extension: ${e.message}`);
        }
    }

    _ensureDirectory(path) {
        const dir = Gio.File.new_for_path(path);
        if (!dir.query_exists(null)) {
            dir.make_directory_with_parents(null);
        }
    }

    _copyFile(filename, destDir) {
        const srcPath = GLib.build_filenamev([this._extensionDir, 'nautilus-extension', filename]);
        const destPath = GLib.build_filenamev([destDir, filename]);
        
        const srcFile = Gio.File.new_for_path(srcPath);
        const destFile = Gio.File.new_for_path(destPath);

        srcFile.copy(destFile, Gio.FileCopyFlags.OVERWRITE, null, null);
    }

    _deleteFile(path) {
        const file = Gio.File.new_for_path(path);
        if (file.query_exists(null)) {
            file.delete(null);
        }
    }

    _deleteDirectory(path) {
        const dir = Gio.File.new_for_path(path);
        if (!dir.query_exists(null)) {
            return;
        }

        // Delete all files in the directory first
        const enumerator = dir.enumerate_children('standard::name', Gio.FileQueryInfoFlags.NONE, null);
        let info;
        while ((info = enumerator.next_file(null)) !== null) {
            const childPath = GLib.build_filenamev([path, info.get_name()]);
            this._deleteFile(childPath);
        }
        enumerator.close(null);

        // Now delete the directory
        dir.delete(null);
    }

    _createConfigFile() {
        const configPath = GLib.build_filenamev([this._nautilusSubDir, 'config.json']);
        const configFile = Gio.File.new_for_path(configPath);

        // Only create if it doesn't exist
        if (configFile.query_exists(null)) {
            return;
        }

        const config = {
            items: {
                _comment: 'Items to include in the context menu',
                AddToLocal: true,
                RemoveFromLocal: true
            }
        };

        const [success, tag] = configFile.replace_contents(
            JSON.stringify(config, null, 4),
            null,
            false,
            Gio.FileCreateFlags.REPLACE_DESTINATION,
            null
        );
    }

    _restartNautilus() {
        try {
            // Use nautilus -q to quit nautilus gracefully
            // It will restart automatically when needed
            GLib.spawn_command_line_async('nautilus -q');
        } catch (e) {
            console.log(`Nautilus Application Adder: Could not restart Nautilus: ${e.message}`);
        }
    }
}
