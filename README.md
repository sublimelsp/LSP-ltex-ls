# LSP-ltex-ls

> THIS IS STILL WORK-IN-PROGRESS!

Latex/Markdown grammar check support for Sublime's LSP plugin provided through [valentjn/ltex-ls](https://github.com/valentjn/ltex-ls).

## Installation

1. Install [LSP](https://packagecontrol.io/packages/LSP) via Package Control. Make sure ```java``` is in path and ```JAVA_HOME``` is set.
2. Install this plugin.
3. Restart Sublime.

## Configuration

Here are some ways to configure the package and the language server.

- From `Preferences > Package Settings > LSP > Servers > LSP-ltex-ls`
- Project-specific configuration.
  From the command palette run `Project: Edit Project` and add your settings in:

  ```js
  {
     "settings": {
        "LSP": {
           "LSP-ltex-ls": {
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
- Use comments in latex code, e.g.
```latex
This is linted with English grammar.
% LTeX: language=de-DE
Geprüft mit deutscher Grammatik.
```
