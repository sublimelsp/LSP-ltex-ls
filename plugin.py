from LSP.plugin import AbstractPlugin
from LSP.plugin import register_plugin
from LSP.plugin import unregister_plugin
from LSP.plugin import Response
from LSP.plugin.core.typing import Optional, Dict
import os
import sublime


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

    def m_ltex_workspaceSpecificConfiguration(self, params, request_id):
        session = self.weaksession()
        if not session:
            return
        result = []
        for item in params['items']:
            print(item)
            result.append({
                "dictionary": {},
                "disabledRules": {},
                "enabledRules": {},
                "hiddenFalsePositives": {},
                })
        session.send_response(Response(request_id, result))

    def m_ltex_progress(self, params):
        # notification do not require a response
        settings = sublime.load_settings("LSP-ltex-ls.sublime-settings")
        if not settings.get('settings').get('ltex.statusBarItem'):
            return
        if not params or not params['operation']:
            return
        if params['operation'] == 'checkDocument':
            if (params['progress'] == 0):
                sublime.status_message('ltex-ls: checking: {}'
                                       .format(params['uri']))
            else:
                sublime.status_message('ltex-ls: finished: {}'
                                       .format(params['uri']))
        else:
            sublime.status_message('ltex-ls: unknown operation')


def plugin_loaded() -> None:
    register_plugin(LTeXLs)


def plugin_unloaded() -> None:
    unregister_plugin(LTeXLs)
