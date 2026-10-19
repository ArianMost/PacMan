set -e

echo "Building Pac-Man..."

rm -rf build dist

uv run pyinstaller --clean --noconfirm pacman.spec

cp config.json dist/pacman/
cp -r audio dist/pacman/audio
mkdir -p dist/pacman/src
cp -r src/images dist/pacman/src/images

python3 - <<'PY'
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

package_dir = Path("dist/pacman")
archive = Path("dist/pacman-linux.zip")

with ZipFile(archive, "w", ZIP_DEFLATED) as zip_file:
    for path in package_dir.rglob("*"):
        if path.is_file():
            zip_file.write(path, path.relative_to("dist"))

print(f"Created {archive}")
PY

echo "Build complete."
echo "Linux package: dist/pacman-linux.zip"
