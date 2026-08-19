#!/usr/bin/env bash

set -euo pipefail

ci_dir="${1:-CI}"
release_tag="${2:-snapshot}"
custom_feed_name="${CUSTOM_FEED_NAME:-smpackage}"
custom_feed_url="${CUSTOM_FEED_URL:-https://github.com/kenzok8/small-package.git}"
version_repo="${VERSION_REPO:-https://github.com/${GITHUB_REPOSITORY:-Lyxot/OpenWrt-CI}/releases}"

cmake_patch="$ci_dir/patches/100-cmake-cross-find.patch"
if [[ ! -f "$ci_dir/config.patch" || ! -f "$ci_dir/busybox.py" || ! -f "$cmake_patch" ]]; then
    echo "CI configuration is incomplete: $ci_dir" >&2
    exit 1
fi

# CMake 4.4 may search the build host's staged headers and libraries before
# the target sysroot. In a parallel build this creates a race and can link
# target packages against host libraries. Exclude only the host include/lib
# directories while keeping staged host programs such as Ninja discoverable.
if ! grep -Fq 'CMAKE_IGNORE_PATH="$(STAGING_DIR_HOST)/include;' include/cmake.mk; then
    patch --batch --forward -p1 < "$cmake_patch"
fi
grep -Fq 'CMAKE_IGNORE_PATH="$(STAGING_DIR_HOST)/include;' include/cmake.mk || {
    echo "Unable to isolate CMake target dependency lookup" >&2
    exit 1
}

if ! grep -q "^src-git ${custom_feed_name} " feeds.conf.default; then
    printf 'src-git %s %s\n' "$custom_feed_name" "$custom_feed_url" >> feeds.conf.default
fi

./scripts/feeds update -a

while IFS= read -r feed; do
    [[ -z "$feed" || "$feed" == "$custom_feed_name" ]] && continue
    ./scripts/feeds install -a -p "$feed"
done < <(./scripts/feeds list -n)

default_custom_packages=(
    luci-app-easytier
    luci-app-iperf3-server
    luci-app-ota
    luci-app-passwall2
)

if [[ -n "${CUSTOM_PACKAGES:-}" ]]; then
    read -r -a custom_packages <<< "$CUSTOM_PACKAGES"
else
    custom_packages=("${default_custom_packages[@]}")
fi

# Keep repeated local runs equivalent to a clean Actions workspace: only
# expose the explicitly selected third-party packages and their dependencies.
custom_install_dir="package/feeds/$custom_feed_name"
if [[ -d "$custom_install_dir" ]]; then
    find "$custom_install_dir" -mindepth 1 -maxdepth 1 -type l -delete
fi
./scripts/feeds install -p "$custom_feed_name" "${custom_packages[@]}"

cp "$ci_dir/config.patch" .config
python3 "$ci_dir/busybox.py" package/utils/busybox/Config-defaults.in

# Prefer the newest toolchain offered by the checked-out upstream tree. This
# keeps snapshots current without hard-coding a compiler version forever; set
# AUTO_LATEST_TOOLCHAIN=0 to preserve a version selected in CI/config.patch.
if [[ "${AUTO_LATEST_TOOLCHAIN:-1}" == "1" ]]; then
    newest_gcc="$(
        sed -n 's/^[[:space:]]*config GCC_USE_VERSION_\([0-9][0-9]*\)$/\1/p' \
            toolchain/gcc/Config.in | sort -n | tail -n1
    )"
    newest_binutils="$(
        sed -n 's/^[[:space:]]*config BINUTILS_USE_VERSION_\([0-9_][0-9_]*\)$/\1/p' \
            toolchain/binutils/Config.in | sort -V | tail -n1
    )"
    [[ -n "$newest_gcc" && -n "$newest_binutils" ]] || {
        echo "Unable to discover the upstream toolchain versions" >&2
        exit 1
    }

    sed -i -E \
        -e '/^(# )?CONFIG_GCC_USE_(DEFAULT_)?VERSION_[0-9]+(=y| is not set)$/d' \
        -e '/^CONFIG_GCC_USE_DEFAULT_VERSION=y$/d' \
        -e '/^(# )?CONFIG_BINUTILS_USE_VERSION_[0-9_]+(=y| is not set)$/d' \
        .config
    printf 'CONFIG_GCC_USE_VERSION_%s=y\n' "$newest_gcc" >> .config
    printf 'CONFIG_BINUTILS_USE_VERSION_%s=y\n' "$newest_binutils" >> .config
    echo "Selected latest upstream toolchain: GCC $newest_gcc, binutils ${newest_binutils//_/.}"
fi

version="${release_tag#v}"
printf 'CONFIG_VERSION_NUMBER="%s"\n' "$version" >> .config
printf 'CONFIG_VERSION_REPO="%s"\n' "$version_repo" >> .config
make defconfig

board="$(sed -n 's/^CONFIG_TARGET_BOARD="\([^"]*\)"/\1/p' .config)"
subtarget="$(sed -n 's/^CONFIG_TARGET_SUBTARGET="\([^"]*\)"/\1/p' .config)"
[[ -n "$board" && -n "$subtarget" ]] || {
    echo "Unable to resolve target board/subtarget from .config" >&2
    exit 1
}
echo "Prepared OpenWrt target: $board/$subtarget"
