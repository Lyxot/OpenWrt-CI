适用于 x86_64 的 OpenWrt 固件，基于 [LEDE](https://github.com/coolsnowwolf/lede) 构建

## 固件下载
自动构建 [Releases](https://github.com/Lyxot/OpenWrt-CI/releases)

## 固件信息
- 内核版本: Linux 6.12 LTS
- 管理地址: 10.1.1.10
- 分区大小: 64M 内核 + 960M 根分区
- O3 编译优化
- Argon 主题
- 插件：
  | | | |
  | ------------ | ------------ | ------------ |
  | AdguardHome | IP/MAC 绑定 | 自动重启 |
  | Easytier | 文件传输 | Passwall2 |
  | 策略路由 | 定时唤醒 | 网络唤醒 |
  | TTYD | Turbo ACC | UPNP | 
- 其它：
  | | | |
  | ------------ | ------------ | ------------ |
  | apk 包管理器 | btrfs 文件系统 | firewall4 防火墙 |
  | IPv6 | 透明网桥 | 移除 autosamba |
  | 移除 KMS 服务器 | r8125/r8126 RSS 驱动 | 端口聚合 |
  | shortcut-fe 快速转发 | wireguard | iperf/iperf3 |
  | ppp-multilink | tcping | unzip |
  | xz | bash | qemu-ga | 