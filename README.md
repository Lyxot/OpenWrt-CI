适用于 x86_64 的 OpenWrt 固件，基于 [ImmortalWrt](https://github.com/immortalwrt/immortalwrt) 构建

## 固件下载
自动构建 [Releases](https://github.com/Lyxot/OpenWrt-CI/releases)
每周一自动更新

## 固件信息
- 内核版本: Linux 6.6 LTS
- 管理地址: 10.1.1.10
- 分区大小: 64M 内核 + 960M 根分区
- O3 编译优化
- Argon 主题
- 插件：
  | | | |
  | ------------ | ------------ | ------------ |
  | Adguard Home | Easytier | Passwall2 |
  | 定时重启 | 定时唤醒 | 网络唤醒 |
  | 终端 | 策略路由 | UPNP |
  | IP/MAC 绑定 | iPerf3 服务器 | Argon 主题设置 |
- 其它：
  - apk 包管理器
  - firewall4 防火墙
  - 链路聚合
  - wireguard
  - qemu-ga