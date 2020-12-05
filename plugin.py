from LSP.plugin import AbstractPlugin
from LSP.plugin import register_plugin
from LSP.plugin import unregister_plugin
from LSP.plugin.core.typing import Optional, Dict
import os


class LTeXLs(AbstractPlugin):
    @classmethod
    def name(cls) -> str:
        return "ltex-ls"

    @classmethod
    def additional_variables(cls) -> Optional[Dict[str, str]]:
        #  settings = sublime.load_settings("LSP-ltex-ls.sublime-settings")
        java_home = os.environ.get("JAVA_HOME")
        if java_home:
            java_executable = os.path.join(java_home, "bin", "java")
        else:
            java_executable = "java"
        return {
            "java_executable": java_executable,
        }


def plugin_loaded() -> None:
    register_plugin(LTeXLs)


def plugin_unloaded() -> None:
    unregister_plugin(LTeXLs)
