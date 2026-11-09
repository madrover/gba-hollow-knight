#!/usr/bin/env bash
# Replaces the vendored Butano in butano/ with a trimmed copy of the given release.
# Usage (from anywhere): tools/update_butano.sh <version>     e.g. tools/update_butano.sh 21.10.0
# Releases: https://github.com/GValiente/butano/releases
set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Usage: $0 <version>" >&2
    exit 1
fi

version="$1"
project_dir="$(cd "$(dirname "$0")/.." && pwd)"
tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/butano.XXXXXX")"
trap 'rm -rf "$tmp_dir"' EXIT

echo "Downloading Butano $version..."
curl -fsSL "https://github.com/GValiente/butano/archive/refs/tags/$version.tar.gz" | tar xz -C "$tmp_dir"
src="$tmp_dir/butano-$version"

# Keep only what the build needs (engine + common fonts) and the licenses.
new_dir="$tmp_dir/trimmed"
mkdir "$new_dir"
for item in butano common LICENSE licenses README.md .gitignore; do
    cp -R "$src/$item" "$new_dir/"
done
echo "$version" > "$new_dir/VERSION"

rm -rf "$project_dir/butano"
mv "$new_dir" "$project_dir/butano"

echo "Butano $version installed in butano/ ($(du -sh "$project_dir/butano" | cut -f1))."
echo "Rebuild with: make clean && make -j8"
