#!/bin/bash

SCRIPT_DIR="$(readlink -f "$(dirname "$0")")"
PROJECT_DIR="$(readlink -f "$SCRIPT_DIR/../..")"
source "$PROJECT_DIR/packaging/config"
BUILD_DIR="$(mktemp -d)"
trap "{ rm -r '$BUILD_DIR'; }" EXIT

# installing into an archive

mkdir -p "$BUILD_DIR/$PKG_NAME-$PKG_VERSION"

cd "$PROJECT_DIR"
export PREFIX
INTERACTIVE=false ROOT="$BUILD_DIR/$PKG_NAME-$PKG_VERSION" ./install

cd "$BUILD_DIR"
tar --remove-files -cjf files.tar.xz "$PKG_NAME-$PKG_VERSION"

# building PKGBUILD

cd "$SCRIPT_DIR"

"$PROJECT_DIR/tools/substitute" PKGBUILD.in "$BUILD_DIR/PKGBUILD" \
								'NAME' "$PKG_NAME" \
								'VERSION' "$PKG_VERSION" \
								'BUILD' "$PKG_BUILD" \
								'DESCRIPTION' "$PKG_DESCRIPTION" \
								'URL' "$PKG_URL" \
								'PREFIX' "$PREFIX"

cd "$BUILD_DIR"

updpkgsums

# building package

makepkg -rfc
mv "$BUILD_DIR/$PKG_NAME"*.pkg.* "$SCRIPT_DIR"
