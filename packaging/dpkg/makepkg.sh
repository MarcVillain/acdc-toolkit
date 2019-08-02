#!/bin/sh

PROJECT_DIR="$(readlink -f "$(dirname "$0")/../..")"
SCRIPT_DIR="$PROJECT_DIR/packaging/dpkg"
source "$PROJECT_DIR/packaging/config"
BUILD_DIR="$(mktemp -d)"
trap "{ rm -r '$BUILD_DIR'; }" EXIT

# installing into a temp directory

FULL_PKG_NAME="$PKG_NAME""_$PKG_VERSION-$PKG_BUILD"
mkdir "$BUILD_DIR/$FULL_PKG_NAME"

cd "$PROJECT_DIR"
export PREFIX
INTERACTIVE=false ROOT="$BUILD_DIR/$FULL_PKG_NAME" ./install

# building DEBIAN/ dir

cd "$BUILD_DIR"

mkdir "$BUILD_DIR/$FULL_PKG_NAME/DEBIAN"
sed "s|@_NAME_@|$PKG_NAME|g ;
	 s|@_VERSION_@|$PKG_VERSION|g ;
	 s|@_BUILD_@|$PKG_BUILD|g ;
     s|@_DESCRIPTION_@|$PKG_DESCRIPTION|g" \
		 "$SCRIPT_DIR/control.in" > "$FULL_PKG_NAME/DEBIAN/control"

# building archive

dpkg-deb --build "$FULL_PKG_NAME"
mv *.deb "$SCRIPT_DIR"
