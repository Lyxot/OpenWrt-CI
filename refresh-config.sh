#!/usr/bin/env bash

set -euo pipefail

ci_dir="${1:-CI}"
config_patch="$ci_dir/config.patch"

[[ -x scripts/diffconfig.sh ]] || {
    echo "Run this script from a prepared OpenWrt source tree" >&2
    exit 1
}
[[ -f "$config_patch" ]] || {
    echo "Configuration patch not found: $config_patch" >&2
    exit 1
}

candidate="$(mktemp)"
trap 'rm -f "$candidate"' EXIT

# Toolchain and firmware version values are selected dynamically by
# prepare-openwrt.sh. Keep only the stable configuration intent here so new
# upstream defaults can flow into the build without rewriting a full .config.
./scripts/diffconfig.sh \
    | sed -E \
        -e '/^(# )?CONFIG_(BINUTILS_USE_VERSION_|BINUTILS_VERSION|GCC_USE_VERSION_|GCC_USE_DEFAULT_VERSION|GCC_VERSION)/d' \
        -e '/^CONFIG_VERSION_(BUG_URL|CODE|DIST|FIRMWARE_URL|HOME_URL|HWREV|MANUFACTURER|MANUFACTURER_URL|NUMBER|PRODUCT|REPO|SUPPORT_URL)=/d' \
    | awk '!seen[$0]++' \
    > "$candidate"

for required in \
    CONFIG_TARGET_x86=y \
    CONFIG_TARGET_x86_64=y \
    CONFIG_TARGET_x86_64_DEVICE_generic=y; do
    grep -Fqx "$required" "$candidate" || {
        echo "Generated configuration patch is missing: $required" >&2
        exit 1
    }
done

changed=false
if ! cmp -s "$candidate" "$config_patch"; then
    install -m 0644 "$candidate" "$config_patch"
    changed=true
    echo "Configuration patch refreshed"
else
    echo "Configuration patch is current"
fi

if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
    printf 'changed=%s\n' "$changed" >> "$GITHUB_OUTPUT"
fi
