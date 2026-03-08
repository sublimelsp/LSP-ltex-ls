from __future__ import annotations

import json
import os
import platform
import shutil
import tarfile
import tempfile
import urllib.error
import urllib.request
import zipfile
from collections.abc import Callable, Mapping
from io import UnsupportedOperation
from typing import Any

import sublime
from LSP.plugin import (
    AbstractPlugin,
    ClientConfig,
    WorkspaceFolder,
    register_plugin,
    unregister_plugin,
)

GITHUB_DL_URL = (
    "https://github.com/valentjn/ltex-ls/releases/download/" + "{0}/ltex-ls-{0}{1}"
)  # Format with Release-Tag
GITHUB_RELEASES_API_URL = (
    "https://api.github.com/repos/valentjn/ltex-" + "ls/releases/latest"
)
SERVER_FOLDER_NAME = "ltex-ls-{}"  # Format with Release-Tag
LATEST_TESTED_RELEASE = "16.0.0"  # Latest testet LTEX-LS release
STORAGE_FOLDER_NAME = "LSP-ltex-ls"
SETTINGS_FILENAME = "LSP-ltex-ls.sublime-settings"

g_latest_github_release = None


def fetch_latest_release() -> None:
    """
    Fetches a the latest release via GitHub API.

    :returns:   Nothing.
    :rtype:     None
    """
    global g_latest_github_release
    if not g_latest_github_release:
        try:
            with urllib.request.urlopen(GITHUB_RELEASES_API_URL) as f:
                data = json.loads(f.read().decode("utf-8"))
                g_latest_github_release = data["tag_name"]
        except urllib.error.URLError:
            pass


fetch_latest_release()


def code_action_insert_settings(server_setting_key: str, value: dict[str, Any]):
    """
    Adds a server setting initiated via custom ltex-la codeAction.
    Merges the settings if already present.
    This function is used for the addToDictionary,... custom commands
    :param      server_setting_key:    The key of the server setting
                                       (in "settings" block)
    :type       server_setting_key:    str
    :param      value:  A dict of "language": [settings] pairs
    :type       value:  dict
    """
    settings = sublime.load_settings(SETTINGS_FILENAME)
    server_settings = settings.get("settings")
    exception_dict = server_settings.get(server_setting_key, {})

    for k, val in value.items():
        language_setting = exception_dict.get(k, [])
        # Remove duplicates
        new_language_setting = list(set(language_setting + val))
        exception_dict[k] = new_language_setting

    server_settings[server_setting_key] = exception_dict
    settings.set("settings", server_settings)
    sublime.save_settings(SETTINGS_FILENAME)


class LTeXLs(AbstractPlugin):
    @classmethod
    def name(cls) -> str:
        return "ltex-ls"

    @classmethod
    def basedir(cls) -> str:
        """
        The directry of this plugin in Package Storage.

        :param      cls:  The class
        :type       cls:  type

        :returns:   The path this plugins base directory
        :rtype:     str
        """
        return os.path.join(cls.storage_path(), STORAGE_FOLDER_NAME)

    @classmethod
    def serverversion(cls) -> str:
        """
        Returns the version of ltex-ls to use. Can be None if
        no version is set in settings and no connection is available and
        and no server is available offline.

        :param      cls:  The class
        :type       cls:  type

        :returns:   The version of ltex-ls to use. Can be None.
        :rtype:     str
        """
        settings = sublime.load_settings(SETTINGS_FILENAME)
        version = settings.get("version")
        if version:
            return version
        # Use latest tested release by default but allow overwriting the
        # behavior.
        if settings.get("allow_untested") and g_latest_github_release:
            return g_latest_github_release
        return LATEST_TESTED_RELEASE

    @classmethod
    def serverdir(cls) -> str:
        """
        The directory of the server. In here are the "bin" and "lib"
        folders.

        :param      cls:  The class
        :type       cls:  type

        :returns:   The server directory if a version can be determined.
                    Else None
        :rtype:     str
        """
        return os.path.join(
            cls.basedir(), SERVER_FOLDER_NAME.format(cls.serverversion())
        )

    @classmethod
    def needs_update_or_installation(cls) -> bool:
        return not os.path.isdir(str(cls.serverdir()))

    @classmethod
    def additional_variables(cls) -> dict[str, str] | None:
        return {
            "script": "ltex-ls.bat" if platform.system() == "Windows" else "ltex-ls",
            "serverdir": cls.serverdir(),
            "serverversion": cls.serverversion(),
        }

    @classmethod
    def install_or_update(cls) -> None:
        if not cls.serverversion():
            return
        if os.path.isdir(cls.basedir()):
            shutil.rmtree(cls.basedir())
        os.makedirs(cls.basedir())
        with tempfile.TemporaryDirectory() as tempdir:
            archive_path = os.path.join(tempdir, "server.tar.gz")

            suffix = ".tar.gz"  # platform-independent release
            if os.getenv("JAVA_HOME") is None:
                p = sublime.platform()
                if p == "osx":
                    suffix = "-mac-x64.tar.gz"
                elif p == "linux":
                    suffix = "-linux-x64.tar.gz"
                elif p == "windows":
                    suffix = "-windows-x64.zip"

            sublime.status_message("ltex-ls: downloading")
            urllib.request.urlretrieve(
                GITHUB_DL_URL.format(cls.serverversion(), suffix), archive_path
            )
            sublime.status_message("ltex-ls: extracting")
            if suffix.endswith("tar.gz"):
                archive = tarfile.open(archive_path, "r:gz")
            elif suffix.endswith(".zip"):
                archive = zipfile.ZipFile(archive_path)
            else:
                raise UnsupportedOperation()
            archive.extractall(tempdir)
            archive.close()
            shutil.move(
                os.path.join(tempdir, SERVER_FOLDER_NAME.format(cls.serverversion())),
                cls.basedir(),
            )
            sublime.status_message(
                f"ltex-ls: installed ltex-ls {cls.serverversion()}"
            )

    @classmethod
    def can_start(
        cls,
        window: sublime.Window,
        initiating_view: sublime.View,
        workspace_folders: list[WorkspaceFolder],
        configuration: ClientConfig,
    ) -> str | None:
        if not os.path.exists(cls.serverdir()):
            return "Download failed or version could not be determined."
        return None

    # Handle custom commands
    def on_pre_server_command(
        self, command: Mapping[str, Any], done_callback: Callable[[], None]
    ) -> bool:
        session = self.weaksession()
        if not session:
            return False

        cmd = command["command"]
        handled = False
        if cmd == "_ltex.addToDictionary":
            code_action_insert_settings(
                "ltex.dictionary", command["arguments"][0]["words"]
            )
            handled = True
        if cmd == "_ltex.hideFalsePositives":
            code_action_insert_settings(
                "ltex.hiddenFalsePositives", command["arguments"][0]["falsePositives"]
            )
            handled = True
        if cmd == "_ltex.disableRules":
            code_action_insert_settings(
                "ltex.disabledRules", command["arguments"][0]["ruleIds"]
            )
            handled = True

        if handled:
            sublime.set_timeout_async(done_callback)
            return True
        return False


def plugin_loaded() -> None:
    register_plugin(LTeXLs)


def plugin_unloaded() -> None:
    unregister_plugin(LTeXLs)
