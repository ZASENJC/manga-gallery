# MangaGallery: 基于 Alist + Rclone + Flask 的云端相册系统

这是一个轻量级、前后端分离的相册解决方案。它利用 Alist 挂载网盘作为无限存储后端，通过 Rclone 将其挂载到本地，最后由 Python Flask 提供极速的 Web 访问体验。

## 核心特性

- **无限存储**：通过 WebDAV 对接阿里云盘、123盘、NAS 等，不占用服务器本地空间。
- **本地极速**：自动生成本地缩略图缓存，浏览体验如同本地相册。
- **双端适配**：瀑布流布局，完美支持 PC 和移动端访问。
- **隐私保护**：内置公开/隐藏双相册模式，支持后台管理。

## 目录结构

建议将所有文件部署在 `/opt/mangaphotos` 目录下：

```text
/opt/mangaphotos/
├── gallery.py          # 前台展示服务
├── admin.py            # 后台管理服务
├── templates/          # HTML 模板目录
│   ├── gallery.html
│   ├── login.html
│   └── admin.html
├── local_cache/        # 缩略图缓存 (自动生成)
└── storage/            # Rclone 挂载点
```
详细教程：[构建无限容量的云端漫画相册]([https://](https://qunq.de/feed/16))
