# 🖥️ 复古 BBS 模拟器

一个运行在终端中的 80 年代风格公告板系统（BBS），支持本地留言板、用户管理，并能**通过 Telnet 连接真实世界现存 BBS 站点**。所有数据存储在虚拟软盘镜像 (`bbs_data.flp`) 中，复古味十足。

![Python版本](https://img.shields.io/badge/python-3.6+-blue.svg)
![许可证](https://img.shields.io/badge/license-MIT-green.svg)
![平台](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

---

## ✨ 功能特点

- **复古终端界面** – 绿色字符、ASCII 艺术标题、菜单交互，模拟老式 CRT 显示器。
- **软盘镜像存储** – 所有数据（用户、留言、连接日志）保存在 FAT12 格式的 `.flp` 文件中，可挂载查看。
- **本地 BBS 功能** – 用户注册/登录、查看公告、发布留言、浏览所有留言、在线用户列表。
- **Telnet 连接真实 BBS** – 支持连接现存 BBS 站点（如 `bbs.byr.cn`、`newsmth.org` 等），可选择字符编码（GBK/UTF-8/BIG5），实时显示收发日志，并**自动记录每次连接的完整对话到软盘中的独立日志文件**（格式：`bbs_messages_YYYYMMDD_HHMMSS_服务器.txt`）。
- **详细连接日志与进度** – 连接过程分 4 步展示（解析主机、连接、协商、就绪），并伴有进度条。
- **管理员工具** – 删除指定用户及其所有留言；清理 7 天前的连接日志文件，释放软盘空间。
- **跨平台** – 纯 Python 实现，仅依赖 `FATtools` 库，易于安装。

---

## 📸 截图

![登录界面](screenshots/login.png)

![主菜单](screenshots/main_menu.png)

![留言板](screenshots/message_board.png)

---

## 🚀 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/qi-cre/BBS-APP.git
cd BBS-APP
2. 安装依赖
pip install -r requirements.txt
或手动安装：
pip install FATtools
python bbs_final.py

📖 使用说明
登录：输入用户名（新用户自动注册）。

主菜单：

1 – 查看公告

2 – 留言板（浏览/发布）

3 – 用户列表

4 – 退出

5 – 连接真实 BBS（Telnet）

6 – 管理员工具

连接真实 BBS 示例
选择 5。

输入地址（如 bbs.byr.cn），端口默认 23。

选择编码（北邮人使用 GBK，水木社区也常用 GBK）。

查看四步日志和进度条，连接成功后即可交互。

输入 quit 或 exit 断开连接，对话内容自动保存到软盘中的日志文件。

管理员工具
删除用户：列出所有用户，选择编号后删除该用户及其所有留言。

清理垃圾：删除软盘中所有 7 天前创建的连接日志文件（文件名符合 bbs_messages_* 格式）。

🗂️ 数据存储
软盘镜像：bbs_data.flp（1.44MB，FAT12）

核心文件：

bbs_users.txt – 用户列表

bbs_messages.txt – 全局留言板

bbs_log_index.txt – 日志文件索引

连接日志：每次 Telnet 连接生成一个新文件，命名如 bbs_messages_20250822_143022_bbs.byr.cn.txt，记录完整会话。

你可以使用任何支持 FAT 的工具挂载该镜像查看或备份数据。

🌐 已知可用的 BBS 站点
站点名称	地址	端口	常用编码
北邮人	bbs.byr.cn	23	GBK
水木社区	newsmth.org	23	GBK
东华大学	bbs.ndhu.edu.tw	23	BIG5
白云黄鹤（华中科大）	bbs.whnet.edu.cn	23	GBK
枫林驿站	bbs.fenglin.info	2323	GBK
RetroBoard	bbs.retroboardbbs.com	2323	UTF-8
❓ 常见问题
Q: 连接 BBS 时乱码怎么办？
A: 请在连接时选择正确的编码（GBK 或 BIG5）。如果仍有问题，建议在 Windows Terminal 中运行以支持 ANSI 颜色。

Q: 如何备份数据？
A: 直接复制 bbs_data.flp 文件即可，它包含了所有数据。

Q: 软盘空间不足怎么办？
A: 使用管理员工具中的“清理垃圾文件”功能，删除 7 天前的日志文件，释放空间。

🤝 贡献
欢迎提交 Issue 和 Pull Request！如果你有新的功能建议或发现 Bug，请随时提出。

📜 许可证
本项目采用 MIT 许可证。

🙏 致谢
感谢所有仍在运行的真实 BBS 站点，延续了网络文化。

感谢 Python 社区和 FATtools 库的开发者。

Happy BBSing! 📟
