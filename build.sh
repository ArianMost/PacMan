#!/bin/bash

set -e

echo "Building Pac-Man..."

rm -rf build dist

uv run pyinstaller --clean --noconfirm pacman.spec

echo "Build complete."
echo "Executable: dist/pacman/pacman"
