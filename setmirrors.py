import json

with open('scripts/projectsmirrors.json', 'r') as f:
    mirrors = json.load(f)

good_mirrors = [
    ("@SF", ["https://downloads.sourceforge.net"]),
    ("@DEBIAN", ["https://ftp.debian.org/debian"]),
    ("@APACHE", ["https://dlcdn.apache.org", "https://archive.apache.org/dist"]),
    ("@GITHUB", ["https://raw.githubusercontent.com"]),
    ("@GNU", ["https://mirrors.rit.edu/gnu", "https://ftp.gnu.org/gnu", "https://ftpmirror.gnu.org"]),
    ("@SAVANNAH", ["https://download.savannah.nongnu.org/releases", "https://cdimage.debian.org/mirror/gnu.org/savannah"]),
    ("@KERNEL", ["https://cdn.kernel.org/pub", "https://mirrors.mit.edu/kernel", "https://mirrors.ustc.edu.cn/kernel.org", "https://mirror.nju.edu.cn/kernel.org"]),
    ("@GNOME", ["https://download.gnome.org/sources"]),
    ("@OPENWRT", ["https://sources.cdn.openwrt.org", "https://sources.openwrt.org"]),
    ("@IMMORTALWRT", ["https://sources-cdn.immortalwrt.org", "https://sources.immortalwrt.org"])
]

for i in good_mirrors:
    for j in range(len(i[1])):
        if i[1][j] in mirrors[i[0]]:
            mirrors[i[0]].remove(i[1][j])
            mirrors[i[0]].insert(j, i[1][j])

with open('scripts/projectsmirrors.json', 'w') as f:
    json.dump(mirrors, f, indent=4)

print(json.dumps(mirrors, indent=4))