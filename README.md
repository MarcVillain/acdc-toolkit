# ACDC Toolkit

## Information

This toolkit was created to help ACDCs (Assistant CDieze Caml) by allowing them to use simple commands to do annoying things.

## Install

### Arch Linux

Add this to your `/etc/pacman.conf`:
```
[epita-acdc]
SigLevel = Optional TrustAll
Server = https://gitlab.com/Fiksd/epita-acdc-pkgs/raw/master/
```

Then install with:
```
sudo pacman -Syu acdc-toolkit
```

### Debian, Ubuntu, ...

Download the .deb package file from https://github.com/MarcVillain/acdc-toolkit/releases/latest.

You can install it using *gdebi*:
```
sudo apt-get install gdebi-core
sudo gdebi acdc-toolkit_stable.deb
```

### Other Systems

Requirements:
- *pipenv* or *pip*
- *pyenv* or its dependencies (see https://github.com/pyenv/pyenv/wiki/Common-build-problems#prerequisites)

```
git clone git@github.com:MarcVillain/acdc-toolkit.git
cd acdc-toolkit
sudo ./install
acdc # the first run will install the remaining tools
```

## Run

```
42sh$ acdc
```

## Contribute

`dev` is for development. `master` is for releases. Don't break `master`.

Commit format: `tag(name):  message`

- **tag:** feat, refactor, misc or fix.
- **name:** the actual file or the feature (if more precision is needed, just separate with commas).
- **message:** Make it short and understandable on its own.

## Authors

- Marc Villain (marc.villain@epita.fr)
- Alex van Vliet (alex.van-vliet@epita.fr)
- Julien Loctaux (julien.loctaux@epita.fr)
