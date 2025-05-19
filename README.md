适用于 x86_64 的 OpenWrt 固件，基于 [ImmortalWrt](https://github.com/immortalwrt/immortalwrt) 构建

## 固件下载
<a href="https://github.com/Lyxot/OpenWrt-CI/releases"><img src="https://img.shields.io/github/release/Lyxot/OpenWrt-CI"/>  <img src="https://img.shields.io/github/downloads/Lyxot/OpenWrt-CI/total"/></a>

每周一、周五自动更新

## 固件信息
- 内核版本: Linux 6.12 LTS
- 管理地址: 10.1.1.10
- 分区大小: 64M 内核 + 960M 根分区
- Argon 主题
- 编译优化:
  - O3 编译优化
  - LTO 优化
  - MOLD 链接器
- 插件:
  | | | |
  | ------------ | ------------ | ------------ |
  | Adguard Home | Easytier | Passwall2 |
  | 定时重启 | 定时唤醒 | 网络唤醒 |
  | 终端 | 策略路由 | UPNP |
  | iPerf3 服务器 | Daed | WireGuard |
- 其它:
  - OTA 更新
  - firewall4 防火墙
  - 链路聚合
  - eBPF
  - qemu-ga