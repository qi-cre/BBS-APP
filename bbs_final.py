#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import datetime
import socket
import threading
import re
import subprocess
import importlib.util

# ------------------ 依赖检查 ------------------
REQUIRED_PYTHON = (3, 6)
OPTIONAL_LIBS = {
    'FATtools': 'FATtools',
}

def check_dependencies():
    if sys.version_info < REQUIRED_PYTHON:
        print(f"❌ Python {'.'.join(map(str, REQUIRED_PYTHON))} 或更高版本是必须的。")
        sys.exit(1)

    missing = []
    for name, pkg in OPTIONAL_LIBS.items():
        if importlib.util.find_spec(pkg) is None:
            missing.append((name, pkg))

    if missing:
        print("⚠️  以下库未安装（必须）：")
        for name, pkg in missing:
            print(f"   - {name} (pip install {pkg})")
        if sys.stdin.isatty():
            choice = input("是否自动安装？(y/N): ").strip().lower()
            if choice == 'y':
                for name, pkg in missing:
                    print(f"正在安装 {pkg} ...")
                    try:
                        subprocess.run([sys.executable, '-m', 'pip', 'install', pkg], check=True)
                        print(f"✅ {name} 安装成功")
                    except subprocess.CalledProcessError:
                        print(f"❌ {name} 安装失败，请手动安装: pip install {pkg}")
                        sys.exit(1)
            else:
                print("缺少必要库，程序退出。")
                sys.exit(1)
        else:
            print("非交互环境，请手动安装所需库。")
            sys.exit(1)
    else:
        print("✅ 依赖检查通过")

check_dependencies()

# ------------------ 导入 FATtools ------------------
try:
    from FATtools.Volume import vopen, FAT
    FATTOOLS_AVAILABLE = True
except ImportError:
    FATTOOLS_AVAILABLE = False
    print("⚠️ FATtools 导入失败，将使用本地文件存储。")

# ------------------ 软盘镜像配置 ------------------
FLOPPY_IMAGE = "bbs_data.flp"
IMAGE_SIZE = 1440 * 1024
USE_FLOPPY = False

DATA_DIR = "floppy_data"
os.makedirs(DATA_DIR, exist_ok=True)

def ensure_floppy():
    global USE_FLOPPY
    if not FATTOOLS_AVAILABLE:
        print("⚠️ FATtools 不可用，使用本地存储。")
        USE_FLOPPY = False
        return

    if not os.path.exists(FLOPPY_IMAGE):
        print(f"📀 创建软盘镜像 {FLOPPY_IMAGE} ...")
        with open(FLOPPY_IMAGE, 'wb') as f:
            f.write(b'\0' * IMAGE_SIZE)

        formatted = False
        try:
            if hasattr(FAT, 'create'):
                FAT.create(FLOPPY_IMAGE, size=IMAGE_SIZE, type='fat12')
                formatted = True
                print("✅ 格式化成功（FAT.create）")
            elif hasattr(FAT, '__call__'):
                fat = FAT(FLOPPY_IMAGE, create=True, size=IMAGE_SIZE, type='fat12')
                formatted = True
                print("✅ 格式化成功（FAT()）")
        except Exception as e:
            print(f"FATtools 格式化尝试失败: {e}")

        if not formatted:
            try:
                vol = vopen(FLOPPY_IMAGE, 'r+b')
                if hasattr(vol, 'format'):
                    vol.format('fat12')
                    formatted = True
                    print("✅ 格式化成功（vol.format）")
                vol.close()
            except Exception as e:
                print(f"vopen format 尝试失败: {e}")

        if not formatted:
            try:
                subprocess.run(['mkfs.fat', FLOPPY_IMAGE], check=True, capture_output=True)
                formatted = True
                print("✅ 格式化成功（mkfs.fat）")
            except:
                pass

        if formatted:
            USE_FLOPPY = True
            try:
                vol = vopen(FLOPPY_IMAGE, 'r+b')
                with vol.open('/bbs_users.txt', 'w') as f:
                    f.write("访客\n管理员\n")
                ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                with vol.open('/bbs_messages.txt', 'w') as f:
                    f.write(f"{ts}|系统|欢迎来到复古BBS！\n")
                with vol.open('/bbs_system.log', 'w') as f:
                    f.write(f"{ts}|系统|系统启动|日志初始化\n")
                vol.close()
                print("✅ 软盘镜像初始化成功。")
            except Exception as e:
                print(f"❌ 初始化数据失败: {e}")
                USE_FLOPPY = False
        else:
            print("⚠️ 自动格式化失败，将使用本地文件存储。")
            USE_FLOPPY = False
    else:
        try:
            vol = vopen(FLOPPY_IMAGE, 'r+b')
            vol.close()
            USE_FLOPPY = True
        except:
            print("⚠️ 软盘镜像损坏，将使用本地文件存储。")
            USE_FLOPPY = False

ensure_floppy()

# ------------------ 数据存储函数（统一接口） ------------------
def read_file(filename, default=None):
    if USE_FLOPPY:
        try:
            vol = vopen(FLOPPY_IMAGE, 'r+b')
            try:
                with vol.open('/' + filename, 'r') as f:
                    content = f.read()
                return content
            except FileNotFoundError:
                if default is not None:
                    with vol.open('/' + filename, 'w') as f:
                        f.write(default)
                    return default
                return None
            finally:
                vol.close()
        except Exception as e:
            print(f"软盘读取错误，改用本地文件: {e}")
            return read_file_local(filename, default)
    else:
        return read_file_local(filename, default)

def write_file(filename, content):
    if USE_FLOPPY:
        try:
            vol = vopen(FLOPPY_IMAGE, 'r+b')
            with vol.open('/' + filename, 'w') as f:
                f.write(content)
            vol.close()
        except Exception as e:
            print(f"软盘写入错误，改用本地文件: {e}")
            write_file_local(filename, content)
    else:
        write_file_local(filename, content)

def append_file(filename, content):
    if USE_FLOPPY:
        try:
            vol = vopen(FLOPPY_IMAGE, 'r+b')
            try:
                with vol.open('/' + filename, 'r') as f:
                    old = f.read()
            except FileNotFoundError:
                old = ''
            with vol.open('/' + filename, 'w') as f:
                f.write(old + content)
            vol.close()
        except Exception as e:
            print(f"软盘追加错误，改用本地文件: {e}")
            append_file_local(filename, content)
    else:
        append_file_local(filename, content)

def delete_file(filename):
    if USE_FLOPPY:
        try:
            vol = vopen(FLOPPY_IMAGE, 'r+b')
            vol.remove('/' + filename)
            vol.close()
        except Exception as e:
            print(f"软盘删除错误，改用本地文件: {e}")
            delete_file_local(filename)
    else:
        delete_file_local(filename)

def read_file_local(filename, default=None):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        if default is not None:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(default)
            return default
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file_local(filename, content):
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def append_file_local(filename, content):
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'a', encoding='utf-8') as f:
        f.write(content)

def delete_file_local(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        os.remove(path)

def list_files_local():
    return os.listdir(DATA_DIR)

# ------------------ 日志索引管理 ------------------
def get_log_index():
    content = read_file('bbs_log_index.txt', default="")
    return [line.strip() for line in content.splitlines() if line.strip()]

def add_log_index(filename):
    lines = get_log_index()
    if filename not in lines:
        lines.append(filename)
        write_file('bbs_log_index.txt', '\n'.join(lines))

def remove_log_from_index(filename):
    lines = get_log_index()
    if filename in lines:
        lines.remove(filename)
        write_file('bbs_log_index.txt', '\n'.join(lines))

# ------------------ 系统日志记录 ------------------
def log_event(event_type, user, content):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    log_line = f"{timestamp}|{event_type}|{user}|{content}\n"
    append_file('bbs_system.log', log_line)

# ------------------ 数据加载 ------------------
def load_users():
    content = read_file('bbs_users.txt', default="访客\n管理员\n")
    return [line.strip() for line in content.splitlines() if line.strip()]

def save_users(users):
    write_file('bbs_users.txt', '\n'.join(users))

def load_messages():
    content = read_file('bbs_messages.txt', 
                        default=f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}|系统|欢迎来到复古BBS！\n")
    return [line.strip().split('|') for line in content.splitlines() if line.strip()]

def save_messages(messages):
    content = '\n'.join([f"{ts}|{user}|{msg}" for ts, user, msg in messages])
    write_file('bbs_messages.txt', content)

# ------------------ 复古样式 ------------------
if os.name == 'nt' and not sys.stdout.isatty():
    GREEN = CYAN = WHITE = YELLOW = RED = BLUE = RESET = BOLD = ''
else:
    GREEN = '\033[92m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def clear_screen():
    print("\n" * 50)

def print_header(title):
    border = '=' * (len(title) + 6)
    print(f"{GREEN}{border}")
    print(f"|| {BOLD}{title}{RESET}{GREEN} ||")
    print(f"{border}{RESET}")

def print_menu(options):
    for idx, (key, desc) in enumerate(options.items(), 1):
        print(f"{GREEN}[{idx}] {CYAN}{desc}{RESET}")

def print_progress(step, total=4, width=20):
    ratio = step / total
    filled = int(ratio * width)
    bar = '#' * filled + '-' * (width - filled)
    sys.stdout.write(f"\r进度: [{bar}] {int(ratio*100)}%")
    sys.stdout.flush()

# ------------------ 预置 BBS 站点列表 ------------------
BBS_SITES = [
    {"name": "北邮人", "host": "bbs.byr.cn", "port": 23, "encoding": "gbk"},
    {"name": "水木社区", "host": "newsmth.org", "port": 23, "encoding": "gbk"},
    {"name": "东华大学", "host": "bbs.ndhu.edu.tw", "port": 23, "encoding": "big5"},
    {"name": "白云黄鹤", "host": "bbs.whnet.edu.cn", "port": 23, "encoding": "gbk"},
    {"name": "枫林驿站", "host": "bbs.fenglin.info", "port": 2323, "encoding": "gbk"},
    {"name": "RetroBoard", "host": "bbs.retroboardbbs.com", "port": 2323, "encoding": "utf-8"},
    {"name": "A-Net Online", "host": "mystic-anet.online", "port": 23, "encoding": "utf-8"},
    {"name": "20 For Beers", "host": "20forbeers.com", "port": 1337, "encoding": "utf-8"},
]

# ------------------ BBS 主程序 ------------------
class RetroBBS:
    def __init__(self):
        self.users = load_users()
        self.messages = load_messages()
        self.current_user = None
        self.running = True
        self.telnet_sock = None
        self.current_log_file = None
        self.last_scan_time = 0
        self.scanned_sites = []   # 存储最近扫描到的可用站点
        log_event("系统启动", "系统", f"BBS 启动，用户数: {len(self.users)}")

    def run(self):
        self.login_screen()
        self.show_main_menu()

    def login_screen(self):
        clear_screen()
        ascii_art = r"""
        ██████╗ ██████╗ ███████╗
        ██╔══██╗██╔══██╗██╔════╝
        ██████╔╝██████╔╝███████╗
        ██╔══██╗██╔══██╗╚════██║
        ██████╔╝██████╔╝███████║
        ╚═════╝ ╚═════╝ ╚══════╝
        """
        print(f"{GREEN}{BOLD}{ascii_art}{RESET}")
        print(f"{GREEN}{'='*40}")
        print(f"{CYAN}   欢迎来到 80 年代复古 BBS 系统")
        print(f"{GREEN}{'='*40}{RESET}")
        print(f"\n{YELLOW}当前在线用户：{len(self.users)} 人{RESET}")
        storage_type = "软盘镜像" if USE_FLOPPY else "本地文件"
        print(f"{CYAN}数据存储: {storage_type}{RESET}")
        username = input(f"{GREEN}请输入你的用户名（新用户自动注册）: {RESET}").strip()
        if not username:
            username = "访客"
        if username not in self.users:
            self.users.append(username)
            save_users(self.users)
            log_event("用户注册", username, "新用户注册")
            print(f"{YELLOW}✨ 新用户 {username} 已注册！{RESET}")
        else:
            log_event("用户登录", username, "登录BBS")
        self.current_user = username
        time.sleep(1)

    def show_main_menu(self):
        while self.running:
            clear_screen()
            print_header(f" 欢迎回来，{self.current_user}！")
            print(f"{GREEN}当前时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
            print(f"{GREEN}{'-'*40}")
            print_menu({
                '1': '📢 查看公告',
                '2': '💬 留言板（查看/发布）',
                '3': '👥 用户列表',
                '4': '🚪 退出系统',
                '5': '🌐 连接真实 BBS（Telnet）',
                '6': '🛠️ 管理员工具（删除用户/清理垃圾）',
                '7': '🔍 扫描可用BBS站点'
            })
            choice = input(f"{GREEN}请输入选项编号: {RESET}").strip()
            if choice == '1':
                self.show_announcement()
            elif choice == '2':
                self.message_board()
            elif choice == '3':
                self.user_list()
            elif choice == '4':
                self.logout()
            elif choice == '5':
                self.connect_bbs()
            elif choice == '6':
                self.admin_tools()
            elif choice == '7':
                self.scan_bbs_sites()
            else:
                print(f"{YELLOW}无效选项，请重新输入！{RESET}")
                time.sleep(1)

    def show_announcement(self):
        clear_screen()
        print_header("📢 系统公告")
        print(f"{CYAN}1. 本BBS为纯复古模拟，仅供娱乐。")
        if USE_FLOPPY:
            print(f"2. 所有数据存储于软盘镜像 {FLOPPY_IMAGE} 中。")
        else:
            print(f"2. 所有数据存储于本地目录 {DATA_DIR} 中。")
        print(f"3. 欢迎发布留言，分享你的想法。")
        print(f"4. 系统运行稳定，无广告，无追踪。{RESET}")
        input(f"\n{GREEN}按 Enter 返回主菜单...{RESET}")

    def message_board(self):
        while True:
            clear_screen()
            print_header("💬 留言板")
            if not self.messages:
                print(f"{YELLOW}暂无留言，快来发布第一条吧！{RESET}")
            else:
                for idx, (ts, user, content) in enumerate(self.messages, 1):
                    print(f"{GREEN}[{idx}]{RESET} {CYAN}{user}{RESET} ({YELLOW}{ts}{RESET})")
                    print(f"    {WHITE}{content}{RESET}")
            print(f"\n{GREEN}{'-'*40}")
            print_menu({
                '1': '发布新留言',
                '2': '返回主菜单'
            })
            sub_choice = input(f"{GREEN}请选择: {RESET}").strip()
            if sub_choice == '1':
                self.post_message()
            elif sub_choice == '2':
                break
            else:
                print(f"{YELLOW}无效选择！{RESET}")
                time.sleep(1)

    def post_message(self):
        print(f"\n{YELLOW}正在发布新留言 (输入空行取消)...{RESET}")
        content = input(f"{GREEN}请输入留言内容: {RESET}").strip()
        if not content:
            print(f"{YELLOW}取消发布。{RESET}")
            time.sleep(1)
            return
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        self.messages.append([timestamp, self.current_user, content])
        save_messages(self.messages)
        log_event("发布留言", self.current_user, content)
        print(f"{GREEN}✅ 留言发布成功！{RESET}")
        time.sleep(1)

    def user_list(self):
        clear_screen()
        print_header("👥 用户列表")
        if not self.users:
            print("暂无用户。")
        else:
            for idx, user in enumerate(self.users, 1):
                status = f"{GREEN}● 在线{RESET}" if user == self.current_user else "○ 离线"
                print(f"{GREEN}[{idx}]{RESET} {CYAN}{user}{RESET}  {status}")
        input(f"\n{GREEN}按 Enter 返回主菜单...{RESET}")

    # ------------------ 管理员工具 ------------------
    def admin_tools(self):
        while True:
            clear_screen()
            print_header("🛠️ 管理员工具")
            print_menu({
                '1': '删除用户（及其留言）',
                '2': '清理垃圾文件（7天前的连接日志）',
                '3': '返回主菜单'
            })
            choice = input(f"{GREEN}请选择: {RESET}").strip()
            if choice == '1':
                self.delete_user()
            elif choice == '2':
                self.clean_garbage()
            elif choice == '3':
                break
            else:
                print(f"{YELLOW}无效选择！{RESET}")
                time.sleep(1)

    def delete_user(self):
        clear_screen()
        print_header("🗑️ 删除用户")
        print("当前用户列表：")
        for idx, user in enumerate(self.users, 1):
            print(f"{idx}. {user}")
        try:
            idx = int(input(f"{GREEN}请输入要删除的用户编号: {RESET}").strip())
            if 1 <= idx <= len(self.users):
                user = self.users[idx-1]
                confirm = input(f"确定要删除用户 '{user}' 及其所有留言吗？(y/N): ").strip().lower()
                if confirm == 'y':
                    self.users.pop(idx-1)
                    save_users(self.users)
                    self.messages = [msg for msg in self.messages if msg[1] != user]
                    save_messages(self.messages)
                    log_event("删除用户", self.current_user, user)
                    print(f"✅ 用户 '{user}' 及其留言已删除。")
                else:
                    print("取消操作。")
            else:
                print("编号无效。")
        except ValueError:
            print("请输入数字。")
        input(f"\n{GREEN}按 Enter 返回...{RESET}")

    def clean_garbage(self):
        clear_screen()
        print_header("🧹 清理垃圾文件（7天前的连接日志）")
        logs = get_log_index()
        now = datetime.datetime.now()
        deleted = []
        for fname in logs:
            m = re.match(r'bbs_messages_(\d{8})_(\d{6})_.*\.txt', fname)
            if m:
                date_str = m.group(1) + m.group(2)
                try:
                    dt = datetime.datetime.strptime(date_str, '%Y%m%d%H%M%S')
                    if (now - dt).days >= 7:
                        delete_file(fname)
                        deleted.append(fname)
                except:
                    delete_file(fname)
                    deleted.append(fname)
            else:
                delete_file(fname)
                deleted.append(fname)
        for fname in deleted:
            remove_log_from_index(fname)
        if deleted:
            log_event("清理垃圾", self.current_user, f"删除 {len(deleted)} 个日志文件")
            print(f"✅ 已删除 {len(deleted)} 个过期日志文件：")
            for f in deleted:
                print(f"  - {f}")
        else:
            print("✅ 没有过期日志文件。")
        input(f"\n{GREEN}按 Enter 返回...{RESET}")

    # ------------------ 扫描可用 BBS 站点（灵活） ------------------
    def scan_bbs_sites(self):
        clear_screen()
        print_header("🔍 扫描可用 BBS 站点")

        now = time.time()
        if now - self.last_scan_time < 60:
            remaining = int(60 - (now - self.last_scan_time))
            print(f"{YELLOW}⏳ 距离上次扫描不足一分钟，请等待 {remaining} 秒后再试。{RESET}")
            input(f"\n{GREEN}按 Enter 返回...{RESET}")
            return

        print("请选择扫描方式：")
        print_menu({
            '1': '扫描预置站点',
            '2': '手动输入单个站点测试',
            '3': '从文件加载站点列表（每行 host:port）',
            '4': '返回主菜单'
        })
        choice = input(f"{GREEN}请选择: {RESET}").strip()
        if choice == '4':
            return
        elif choice == '1':
            sites = BBS_SITES
            self._do_scan(sites)
        elif choice == '2':
            host = input(f"{GREEN}请输入主机地址: {RESET}").strip()
            if not host:
                print(f"{YELLOW}取消。{RESET}")
                time.sleep(1)
                return
            port_str = input(f"{GREEN}请输入端口（默认 23）: {RESET}").strip()
            port = int(port_str) if port_str else 23
            sites = [{"name": host, "host": host, "port": port, "encoding": "gbk"}]
            self._do_scan(sites)
        elif choice == '3':
            filepath = input(f"{GREEN}请输入站点列表文件路径（每行 host:port）: {RESET}").strip()
            if not os.path.exists(filepath):
                print(f"{RED}文件不存在。{RESET}")
                time.sleep(1)
                return
            try:
                sites = []
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        parts = line.split(':')
                        if len(parts) == 2:
                            host, port_str = parts
                            port = int(port_str)
                        else:
                            host = parts[0]
                            port = 23
                        sites.append({"name": host, "host": host, "port": port, "encoding": "gbk"})
                if not sites:
                    print(f"{YELLOW}文件中没有有效的站点。{RESET}")
                    time.sleep(1)
                    return
                self._do_scan(sites)
            except Exception as e:
                print(f"{RED}读取文件失败: {e}{RESET}")
                time.sleep(1)
                return
        else:
            print(f"{YELLOW}无效选择。{RESET}")
            time.sleep(1)
            return

    def _do_scan(self, sites):
        print(f"{CYAN}开始扫描，每个站点超时 3 秒...{RESET}\n")
        results = []
        total = len(sites)
        for idx, site in enumerate(sites, 1):
            name = site.get('name', site['host'])
            host = site['host']
            port = site['port']
            sys.stdout.write(f"[{idx}/{total}] 正在测试 {name} ({host}:{port}) ... ")
            sys.stdout.flush()
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                start = time.time()
                sock.connect((host, port))
                elapsed = time.time() - start
                sock.close()
                status = f"{GREEN}✅ 可用 (响应 {elapsed:.2f}s){RESET}"
                results.append((name, host, port, True, elapsed))
            except Exception:
                status = f"{RED}❌ 不可用{RESET}"
                results.append((name, host, port, False, None))
            print(status)

        print(f"\n{GREEN}{'='*50}{RESET}")
        print(f"{CYAN}扫描完成！可用站点：{RESET}")
        available = [r for r in results if r[3]]
        if available:
            # 保存扫描到的可用站点（用于连接界面）
            self.scanned_sites = []
            for name, host, port, _, elapsed in available:
                print(f"  {GREEN}• {name}{RESET} ({host}:{port}) 延迟 {elapsed:.2f}s")
                # 保存到 scanned_sites，编码暂设为 gbk（连接时可再选）
                self.scanned_sites.append({"name": name, "host": host, "port": port, "encoding": "gbk", "delay": elapsed})
        else:
            print(f"{YELLOW}没有检测到可用站点。{RESET}")
            self.scanned_sites = []
        log_event("站点扫描", self.current_user, f"扫描 {total} 个站点，可用 {len(available)} 个")
        self.last_scan_time = time.time()
        input(f"\n{GREEN}按 Enter 返回主菜单...{RESET}")

    # ------------------ Telnet 连接真实 BBS（集成扫描结果） ------------------
    def connect_bbs(self):
        clear_screen()
        print_header("🌐 连接真实 BBS（Telnet）")

        # 如果有扫描到的站点，提供选择
        if self.scanned_sites:
            print(f"{CYAN}发现 {len(self.scanned_sites)} 个最近扫描到的可用站点：{RESET}")
            for idx, site in enumerate(self.scanned_sites, 1):
                name = site['name']
                host = site['host']
                port = site['port']
                delay = site.get('delay', '?')
                print(f"  {idx}. {name} ({host}:{port}) 延迟 {delay:.2f}s" if isinstance(delay, float) else f"  {idx}. {name} ({host}:{port})")
            print("  - 输入 0 手动输入地址")
            choice = input(f"{GREEN}请选择站点编号（或直接输入地址）: {RESET}").strip()
            if choice.isdigit() and int(choice) == 0:
                host = input(f"{GREEN}请输入主机地址: {RESET}").strip()
                if not host:
                    print(f"{YELLOW}取消连接。{RESET}")
                    time.sleep(1)
                    return
                port_str = input(f"{GREEN}端口（默认 23）: {RESET}").strip()
                port = int(port_str) if port_str else 23
            elif choice.isdigit() and 1 <= int(choice) <= len(self.scanned_sites):
                site = self.scanned_sites[int(choice)-1]
                host = site['host']
                port = site['port']
                print(f"{GREEN}使用站点: {site['name']} ({host}:{port}){RESET}")
            else:
                # 尝试作为地址解析
                host = choice
                port = 23
        else:
            # 没有扫描记录，手动输入
            print(f"{CYAN}暂无扫描记录，请手动输入：{RESET}")
            host = input(f"{GREEN}请输入主机地址: {RESET}").strip()
            if not host:
                print(f"{YELLOW}取消连接。{RESET}")
                time.sleep(1)
                return
            port_str = input(f"{GREEN}端口（默认 23）: {RESET}").strip()
            port = int(port_str) if port_str else 23

        print(f"{CYAN}请选择字符编码：1. GBK  2. UTF-8  3. BIG5 (默认GBK){RESET}")
        enc_choice = input(f"{GREEN}请输入数字: {RESET}").strip()
        self.telnet_encoding = 'gbk'
        if enc_choice == '2':
            self.telnet_encoding = 'utf-8'
        elif enc_choice == '3':
            self.telnet_encoding = 'big5'
        print(f"{BLUE}>>> 使用编码: {self.telnet_encoding}{RESET}")

        # 生成日志文件名
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_host = re.sub(r'[^a-zA-Z0-9\-_.]', '_', host)
        log_filename = f"bbs_messages_{timestamp}_{safe_host}.txt"
        add_log_index(log_filename)
        self.current_log_file = log_filename

        steps = [
            ("正在解析主机", lambda: socket.gethostbyname(host)),
            ("正在尝试连接", lambda: self._do_connect(host, port)),
            ("正在协商协议", lambda: time.sleep(0.5)),
            ("连接就绪，开始传输数据", lambda: time.sleep(0.3))
        ]

        print("\n连接日志：")
        sock = None
        for i, (desc, action) in enumerate(steps, 1):
            print(f"{BLUE}[{i}/{len(steps)}] {desc} ...{RESET}")
            try:
                if i == 1:
                    ip = socket.gethostbyname(host)
                    print(f"{GREEN}    ✅ 解析成功 -> {ip}{RESET}")
                elif i == 2:
                    sock = self._do_connect(host, port)
                    print(f"{GREEN}    ✅ 连接成功 (端口 {port}){RESET}")
                else:
                    action()
                    print(f"{GREEN}    ✅ 完成{RESET}")
            except Exception as e:
                print(f"{RED}    ❌ 失败: {e}{RESET}")
                log_event("连接失败", self.current_user, f"{host}:{port} - {e}")
                input(f"\n{GREEN}按 Enter 返回...{RESET}")
                return
            print_progress(i, len(steps))
            time.sleep(0.2)

        print("\n")
        if sock:
            self.telnet_sock = sock
            log_event("连接BBS", self.current_user, f"{host}:{port}")
            self._telnet_interactive(sock, log_filename)
        else:
            print(f"{RED}连接失败{RESET}")

    def _do_connect(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        return sock

    def _telnet_interactive(self, sock, log_filename):
        encoding = getattr(self, 'telnet_encoding', 'gbk')
        def receiver():
            while True:
                try:
                    data = sock.recv(4096)
                    if not data:
                        break
                    try:
                        decoded = data.decode(encoding)
                    except UnicodeDecodeError:
                        decoded = data.decode(encoding, errors='replace')
                    print(decoded, end='', flush=True)
                    append_file(log_filename, decoded)
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"\n{RED}>>> 接收错误: {e}{RESET}")
                    break

        recv_thread = threading.Thread(target=receiver, daemon=True)
        recv_thread.start()

        print(f"{GREEN}>>> 进入交互模式，输入内容发送，输入 'quit' 退出连接{RESET}\n")
        try:
            while True:
                try:
                    user_input = input(f"{GREEN}>> {RESET}")
                except EOFError:
                    break
                if user_input.lower() in ('quit', 'exit', 'close'):
                    sock.send((user_input + '\n').encode('ascii'))
                    break
                sock.send((user_input + '\n').encode('ascii'))
        except KeyboardInterrupt:
            print(f"\n{YELLOW}>>> 用户中断{RESET}")
        finally:
            try:
                sock.close()
            except:
                pass
            print(f"{BLUE}>>> 连接已关闭，日志已保存至: {log_filename}{RESET}")
            log_event("断开BBS", self.current_user, f"日志: {log_filename}")
            input(f"\n{GREEN}按 Enter 返回主菜单...{RESET}")

    def logout(self):
        self.running = False
        if self.telnet_sock:
            try:
                self.telnet_sock.close()
            except:
                pass
        log_event("用户登出", self.current_user, "退出系统")
        clear_screen()
        print(f"{GREEN}{BOLD}感谢使用复古BBS，再见，{self.current_user}！{RESET}")
        time.sleep(2)

# ------------------ 启动 ------------------
if __name__ == "__main__":
    try:
        bbs = RetroBBS()
        bbs.run()
    except KeyboardInterrupt:
        clear_screen()
        print(f"\n{GREEN}👋 已强制退出。{RESET}")
        sys.exit(0)