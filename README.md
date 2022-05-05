# LSP-ltex-ls

Latex/Markdown grammar check support for Sublime's LSP plugin provided through [valentjn/ltex-ls](https://github.com/valentjn/ltex-ls).

## Installation

1. Install [LSP](https://packagecontrol.io/packages/LSP) via Package Control. Make sure a x64-version of `java` is in path and `JAVA_HOME` is set.
2. Install this plugin.
3. Restart Sublime.

Note: Currently LSP ignores non-workspace files. Add the folder to Sublime Text to enable the Server.

## Configuration

Here are some ways to configure the package and the language server.

- From `Preferences > Package Settings > LSP > Servers > LSP-ltex-ls`
- Project-specific configuration.
  From the command palette run `Project: Edit Project` and add your settings in:

  ```js
  {
     "settings": {
        "LSP": {
           "ltex-ls": {
              "settings": {
                 // Put your settings here
              }
           }
        }
     }
  }
  ```

### Language Configuration
- Set the language string in the server settings
- Use magic comments in code, see https://valentjn.github.io/vscode-ltex/docs/advanced-usage.html#magic-comments

### Limitations

This version lacks in comparison to [vscode-ltex](https://github.com/valentjn/vscode-ltex) the possibility to add exceptions (rules, words, …) on a per-project basis. (Maybe added in the future.)
