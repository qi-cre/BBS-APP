# 🖥️ 复古 BBS 模拟器（CLI 版）

一个运行在终端中的 80 年代风格公告板系统（BBS），支持本地留言板、用户管理，并能**通过 Telnet 连接真实世界现存 BBS 站点**。所有数据存储在虚拟软盘镜像 (`bbs_data.flp`) 中，并支持**启动拨号**功能，模拟老式电话拨号音。

![Python版本](https://img.shields.io/badge/python-3.6+-blue.svg)
![许可证](https://img.shields.io/badge/license-MIT-green.svg)
![平台](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

---

## ✨ 功能特点

- **复古终端界面** – 绿色字符、ASCII 艺术标题、菜单交互，模拟老式 CRT 显示器。
- **启动拨号音效** – 程序启动时首先进入拨号环节，显示虚拟号码列表，输入号码或序号即可播放真实的 DTMF 双频拨号音（支持 `sounddevice` 或 `winsound` 模拟）。
- **软盘镜像存储** – 所有数据（用户、留言、连接日志）保存在 FAT12 格式的 `.flp` 文件中，可挂载查看。
- **本地 BBS 功能** – 用户注册/登录、查看公告、发布留言、浏览所有留言、在线用户列表。
- **Telnet 连接真实 BBS** – 支持连接现存 BBS 站点（如 `bbs.byr.cn`、`newsmth.org` 等），可选择字符编码（GBK/UTF-8/BIG5），实时显示收发日志，并**自动记录每次连接的完整对话到软盘中的独立日志文件**（格式：`bbs_messages_YYYYMMDD_HHMMSS_服务器.txt`）。
- **详细连接日志与进度** – 连接过程分 4 步展示（解析主机、连接、协商、就绪），并伴有进度条。
- **管理员工具** – 删除指定用户及其所有留言；清理 7 天前的连接日志文件，释放软盘空间。
- **站点扫描** – 支持扫描预置站点列表（含多所高校）、手动输入单个站点、从文件加载站点列表（每行 `host:port`）。
- **跨平台** – 纯 Python 实现，依赖 `FATtools` 和可选 `sounddevice`+`numpy`（用于真实拨号音），易于安装。

---

## 📸 截图

（你可以在这里放入终端截图，例如启动拨号、主菜单、留言板等）

---

## 🚀 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/你的用户名/retro-bbs.git
cd retro-bbs
2. 安装依赖
必需依赖
bash
pip install -r requirements.txt
或手动安装：

bash
pip install FATtools
可选依赖（用于真实 DTMF 拨号音）
bash
pip install sounddevice numpy
若不安装，程序会降级为 winsound.Beep（仅 Windows）或提示。

3. 运行
bash
python bbs_final.py
程序首次运行会自动创建 bbs_data.flp 软盘镜像（FAT12 格式）。

📖 使用说明
启动过程
拨号环节：程序启动后首先进入拨号界面，显示 5 个虚拟号码列表，输入序号（如 1）自动填入对应号码，或直接输入完整号码，按下回车播放拨号音。

若跳过（直接回车），则直接进入登录。

登录：输入用户名（新用户自动注册）。

主菜单：显示功能列表。

主菜单功能
1 – 查看公告

2 – 留言板（浏览/发布）

3 – 用户列表

4 – 退出

5 – 连接真实 BBS（Telnet）– 此处可选择再次拨号，然后选择站点或手动输入地址。

6 – 管理员工具（删除用户、清理日志）

7 – 扫描可用 BBS 站点（支持预置列表、手动输入、从文件加载）

连接真实 BBS 示例
选择 5。

可选再次拨号（输入号码播放 DTMF）。

从扫描结果中选择站点，或手动输入地址和端口。

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

bbs_system.log – 系统操作日志

连接日志：每次 Telnet 连接生成一个新文件，命名如 bbs_messages_20250822_143022_bbs.byr.cn.txt，记录完整会话。

如果软盘镜像不可用（如 FATtools 故障），程序会自动降级到本地目录 floppy_data/，功能不受影响。

🌐 常用 BBS 站点（含高校）
站点名称	地址	端口	常用编码	备注
北邮人	bbs.byr.cn	23	GBK	活跃
水木社区	newsmth.org	23	GBK	活跃
东华大学	bbs.ndhu.edu.tw	23	BIG5	台湾
白云黄鹤	bbs.whnet.edu.cn	23	GBK	华中科大
枫林驿站	bbs.fenglin.info	2323	GBK	
RetroBoard	bbs.retroboardbbs.com	2323	UTF-8	国际
A-Net Online	mystic-anet.online	23	UTF-8	国际
20 For Beers	20forbeers.com	1337	UTF-8	国际
清华大学	bbs.tsinghua.edu.cn	23	GBK	可能关闭
北京大学	bbs.pku.edu.cn	23	GBK	可能关闭
南京大学	bbs.nju.edu.cn	23	GBK	可能关闭
浙江大学	bbs.zju.edu.cn	23	GBK	可能关闭
复旦大学	bbs.fudan.edu.cn	23	GBK	可能关闭
上海交通大学	bbs.sjtu.edu.cn	23	GBK	可能关闭
中国科学技术大学	bbs.ustc.edu.cn	23	GBK	可能关闭
西安交通大学	bbs.xjtu.edu.cn	23	GBK	可能关闭
武汉大学	bbs.whu.edu.cn	23	GBK	可能关闭
中山大学	bbs.sysu.edu.cn	23	GBK	可能关闭
四川大学	bbs.scu.edu.cn	23	GBK	可能关闭
山东大学	bbs.sdu.edu.cn	23	GBK	可能关闭
东南大学	bbs.seu.edu.cn	23	GBK	可能关闭
厦门大学	bbs.xmu.edu.cn	23	GBK	可能关闭
南开大学	bbs.nankai.edu.cn	23	GBK	可能关闭
天津大学	bbs.tju.edu.cn	23	GBK	可能关闭
吉林大学	bbs.jlu.edu.cn	23	GBK	可能关闭
兰州大学	bbs.lzu.edu.cn	23	GBK	可能关闭
电子科技大学	bbs.uestc.edu.cn	23	GBK	可能关闭
华中科技大学	bbs.hust.edu.cn	23	GBK	可能关闭
哈尔滨工业大学	bbs.hit.edu.cn	23	GBK	可能关闭
提示：部分高校 BBS 可能已停止外部访问，扫描结果仅供参考。

❓ 常见问题
Q: 连接 BBS 时乱码怎么办？
A: 请在连接时选择正确的编码（GBK 或 BIG5）。如果仍有问题，建议在 Windows Terminal 中运行以支持 UTF-8。

Q: 如何备份数据？
A: 直接复制 bbs_data.flp 文件即可，它包含了所有数据。

Q: 软盘空间不足怎么办？
A: 使用管理员工具中的“清理垃圾文件”功能，删除 7 天前的日志文件，释放空间。

Q: 如何获得真实的 DTMF 拨号音？
A: 安装 sounddevice 和 numpy（pip install sounddevice numpy），程序会自动使用它们合成双频音效。

Q: 程序启动时可以不拨号吗？
A: 可以，在拨号界面直接回车跳过即可。

Q: 终端显示出现乱码或菜单文字异常（如“月端”等）？
A: 这是终端编码或字体设置问题，请尝试以下方法：

在 PowerShell 中运行 $OutputEncoding = [System.Text.Encoding]::UTF8 和 [Console]::OutputEncoding = [System.Text.Encoding]::UTF8。

建议使用 Windows Terminal（推荐）并设置字体为 Cascadia Code PL 或 Consolas，字符集选择 UTF-8。

如果问题依旧，可在运行前设置环境变量 $env:NO_COLOR=1 禁用颜色（但不会影响中文）。

Q: 如何调整终端的复古显示效果？
A: 在 Windows Terminal 中，打开配置文件（如 PowerShell）的“外观”设置，开启 “复古风格的终端效果”（会添加扫描线和亮度变化）。同时，可设置光标形状为下划线（在“光标”部分选择），字体推荐 Cascadia Code 或 3270 等复古等宽字体，字号建议 16~18，行高 1.2 可获得更佳体验。

🤝 贡献
欢迎提交 Issue 和 Pull Request！如果你有新的功能建议或发现 Bug，请随时提出。

📜 许可证
本项目采用 MIT 许可证。

🙏 致谢
感谢所有仍在运行的真实 BBS 站点，延续了网络文化。

感谢 Python 社区和 FATtools、sounddevice 等库的开发者。

Happy BBSing! 📟