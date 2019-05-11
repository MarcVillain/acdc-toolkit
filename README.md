# ACDC Toolkit

## Information

This toolkit was created to help ACDCs by allowing them to use simple commands to do annoying things.

## Install

Requirements:
- Python >= 3.6
- docopt >= 0.6.2

```
42sh$ pip install docopt
42sh$ git clone git@gitlab.com:acdc_epita/toolkit.git
42sh$ mv toolkit ~/.acdc
42sh$ echo 'alias acdc=~/.acdc/toolkit'
```

## Run

```
42sh$ acdc
```

## Contribute

`dev` is for development. `master` is for releases. Don't break `master`.

Commit format: `tag(name):  message`

- **Tag:** feat, refactor, misc or fix.
- **Name:** the actual file or the feature (if more precision is needed, just separate with commas).
- **Message:** Make it short and understandable on its own.
