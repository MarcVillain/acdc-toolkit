#!/bin/bash

SCRIPT_DIR="$(readlink -f "$(dirname "$0")")"
PROJECT_DIR="$(readlink -f "$SCRIPT_DIR/../..")"
source "$PROJECT_DIR/packaging/config"
BUILD_DIR="$(mktemp -d)"
trap "{ rm -rf '$BUILD_DIR'; }" EXIT

# installing into a temp directory

FULL_PKG_NAME="$PKG_NAME""_$PKG_VERSION-$PKG_BUILD"
mkdir "$BUILD_DIR/$FULL_PKG_NAME"

cd "$PROJECT_DIR"
export PREFIX
INTERACTIVE=false ROOT="$BUILD_DIR/$FULL_PKG_NAME" INSTALL_TYPE='debian-package' ./install

# building DEBIAN/ dir

cd "$BUILD_DIR"

mkdir "$BUILD_DIR/$FULL_PKG_NAME/DEBIAN"
"$PROJECT_DIR/tools/substitute" "$SCRIPT_DIR/control.in" "$FULL_PKG_NAME/DEBIAN/control" \
				'NAME' "$PKG_NAME" \
				'VERSION' "$PKG_VERSION" \
				'BUILD' "$PKG_BUILD" \
				'DESCRIPTION' "$PKG_DESCRIPTION"

# building archive

dpkg-deb --build "$FULL_PKG_NAME"
mv *.deb "$SCRIPT_DIR"
