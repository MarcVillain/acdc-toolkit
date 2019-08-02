#!/bin/sh

PROJECT_DIR="$(readlink -f "$(dirname "$0")/../..")"
SCRIPT_DIR="$PROJECT_DIR/packaging/pacman"
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

sed "s|@_NAME_@|$PKG_NAME|g ;
	 s|@_VERSION_@|$PKG_VERSION|g ;
	 s|@_BUILD_@|$PKG_BUILD|g ;
     s|@_DESCRIPTION_@|$PKG_DESCRIPTION|g ;
	 s|@_URL_@|$PKG_URL|g ;
	 s|@_PREFIX_@|$PREFIX|g" \
		 PKGBUILD.in > "$BUILD_DIR/PKGBUILD"

cd "$BUILD_DIR"

updpkgsums

# building package

makepkg -rfc
mv "$BUILD_DIR/$PKG_NAME"*.pkg.* "$SCRIPT_DIR"
