import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, Scrollbar, Menu, simpledialog
from tkinter.ttk import Treeview, Progressbar
import os
import shutil
import sys

# 获取资源路径（支持打包后的路径）
def get_resource_path(relative_path):
    """获取资源文件的绝对路径，支持PyInstaller打包环境"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# 规范化路径
def normalize_path(path):
    """将路径中的斜杠统一转换为反斜杠"""
    return path.replace('/', '\\')

# 创建主窗口
root = tk.Tk()
root.title("文件夹移动工具")
try:
    root.iconbitmap(get_resource_path('Fmanager.ico'))
except Exception as e:
    print(f"主窗口图标加载失败: {e}")

# 第一栏：目标文件夹路径输入
path_label = tk.Label(root, text="目标文件夹路径：")
path_label.grid(row=0, column=0, padx=10, pady=10)

path_entry = tk.Entry(root, width=50)
path_entry.grid(row=0, column=1, padx=10, pady=10)

def select_path():
    """选择目标文件夹并更新路径输入框"""
    path = filedialog.askdirectory()
    path_entry.delete(0, tk.END)
    path_entry.insert(0, normalize_path(path))

select_button = tk.Button(root, text="选择文件夹", command=select_path)
select_button.grid(row=0, column=2, padx=10, pady=10)

# 第二栏：显示模式选择
mode_label = tk.Label(root, text="选择显示模式：")
mode_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

mode_var = tk.IntVar(value=1)

mode_radio1 = tk.Radiobutton(root, text="只显示一级子文件夹名", variable=mode_var, value=1)
mode_radio1.grid(row=1, column=1, sticky="w", pady=2)

mode_radio2 = tk.Radiobutton(root, text="只显示二级子文件夹名", variable=mode_var, value=2)
mode_radio2.grid(row=2, column=1, sticky="w", pady=2)

# 模式3：自定义层级
mode3_frame = tk.Frame(root)
mode3_frame.grid(row=3, column=1, sticky="w", pady=2)
mode_radio3 = tk.Radiobutton(mode3_frame, text="只显示", variable=mode_var, value=3)
mode_radio3.pack(side="left")
custom_level_entry = tk.Entry(mode3_frame, width=3)
custom_level_entry.pack(side="left", padx=5)
custom_level_entry.insert(0, "3")
tk.Label(mode3_frame, text="级子文件夹名").pack(side="left")

mode_radio4 = tk.Radiobutton(root, text="按树形结构动态展开（自动预加载）", variable=mode_var, value=4)
mode_radio4.grid(row=4, column=1, sticky="w", pady=2)

# 确认按钮
def confirm():
    """确认选择并显示文件夹列表"""
    path = normalize_path(path_entry.get())
    mode = mode_var.get()
    if not path:
        messagebox.showerror("错误", "请输入目标文件夹路径")
        return
    list_dirs(path, mode)

confirm_button = tk.Button(root, text="确认", command=confirm)
confirm_button.grid(row=5, column=1, padx=10, pady=10)

# 显示文件夹列表的逻辑
def select_target_path(entry):
    """选择操作目标路径并更新输入框"""
    path = filedialog.askdirectory()
    entry.delete(0, tk.END)
    entry.insert(0, normalize_path(path))

def list_dirs(path, mode):
    """根据模式显示文件夹列表"""
    try:
        path = normalize_path(path)
        result_window = Toplevel(root)
        result_window.title("显示结果")
        result_window.geometry("600x600")
        result_window.minsize(600, 600)
        try:
            result_window.iconbitmap(get_resource_path('Fmanager.ico'))
        except Exception as e:
            print(f"二级窗口图标加载失败: {e}")

        # 顶部框架：操作选择和右键菜单
        top_frame = tk.Frame(result_window)
        top_frame.pack(anchor="w", fill="x", padx=10, pady=10)

        # 操作选择
        operation_frame = tk.Frame(top_frame)
        operation_frame.pack(side="left", padx=10, anchor="nw")
        operation_label = tk.Label(operation_frame, text="选择操作：")
        operation_label.pack(anchor="w")
        operation_var = tk.IntVar(value=1)
        tk.Radiobutton(operation_frame, text="复制到", variable=operation_var, value=1).pack(anchor="w")
        tk.Radiobutton(operation_frame, text="剪切到", variable=operation_var, value=2).pack(anchor="w")

        # 模式4专属：右键菜单选项
        if mode == 4:
            menu_frame = tk.Frame(top_frame)
            menu_frame.pack(side="left", padx=10, anchor="nw")
            menu_label = tk.Label(menu_frame, text="右键菜单：")
            menu_label.pack(anchor="w")
            menu_var = tk.IntVar(value=0)
            tk.Radiobutton(menu_frame, text="全选一级子文件夹", variable=menu_var, value=1).pack(anchor="w")
            tk.Radiobutton(menu_frame, text="全选二级子文件夹", variable=menu_var, value=2).pack(anchor="w")
            tk.Radiobutton(menu_frame, text="全选自定义层级", variable=menu_var, value=3).pack(anchor="w")
            custom_level_entry_inner = tk.Entry(menu_frame, width=5)
            custom_level_entry_inner.pack(anchor="w", pady=5)
            custom_level_entry_inner.insert(0, "3")

        # 目标路径输入
        target_frame = tk.Frame(result_window)
        target_frame.pack(anchor="nw", fill="x", padx=10, pady=5)
        target_path_label = tk.Label(target_frame, text="目标路径：")
        target_path_label.pack(side="left")
        target_path_entry = tk.Entry(target_frame, width=50)
        target_path_entry.pack(side="left", padx=5)
        tk.Button(target_frame, text="选择", command=lambda: select_target_path(target_path_entry)).pack(side="left")

        # Treeview展示文件夹
        tree_frame = tk.Frame(result_window)
        tree_frame.pack(expand=True, fill="both", pady=10)
        scrollbar = Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        tree = Treeview(tree_frame, yscrollcommand=scrollbar.set, selectmode="extended")
        tree.pack(expand=True, fill="both")
        scrollbar.config(command=tree.yview)

        # 根据模式填充Treeview
        if mode == 1:
            tree["columns"] = ("path", "type")
            tree.heading("#0", text="文件夹名")
            tree.heading("path", text="文件路径")
            tree.heading("type", text="类型")
            tree.column("#0", width=150)
            tree.column("path", width=300)
            tree.column("type", width=80, anchor="center")
            level1_dirs = sorted([entry.name for entry in os.scandir(path) if entry.is_dir()])
            for dir_name in level1_dirs:
                full_path = normalize_path(os.path.join(path, dir_name))
                tree.insert("", "end", text=dir_name, values=(full_path, "文件夹"))
            def get_full_path(item):
                return normalize_path(tree.item(item, "values")[0])

        elif mode == 2:
            tree["columns"] = ("path", "type")
            tree.heading("#0", text="文件夹名")
            tree.heading("path", text="文件路径")
            tree.heading("type", text="类型")
            tree.column("#0", width=150)
            tree.column("path", width=300)
            tree.column("type", width=80, anchor="center")
            level1_dirs = sorted([entry.name for entry in os.scandir(path) if entry.is_dir()])
            for level1_dir in level1_dirs:
                level1_path = normalize_path(os.path.join(path, level1_dir))
                level2_dirs = sorted([entry.name for entry in os.scandir(level1_path) if entry.is_dir()])
                for level2_dir in level2_dirs:
                    full_path = normalize_path(os.path.join(level1_path, level2_dir))
                    tree.insert("", "end", text=level2_dir, values=(full_path, "文件夹"))
            def get_full_path(item):
                return normalize_path(tree.item(item, "values")[0])

        elif mode == 3:
            tree["columns"] = ("path", "type")
            tree.heading("#0", text="文件夹名")
            tree.heading("path", text="文件路径")
            tree.heading("type", text="类型")
            tree.column("#0", width=150)
            tree.column("path", width=300)
            tree.column("type", width=80, anchor="center")
            try:
                level = int(custom_level_entry.get())
                if level < 1:
                    raise ValueError
            except ValueError:
                messagebox.showerror("错误", "请输入有效的层级数")
                level = 3
            def scan_level(current_path, current_level, max_level):
                if current_level > max_level:
                    return []
                dirs = []
                for entry in sorted(os.scandir(current_path), key=lambda x: x.name):
                    if entry.is_dir():
                        if current_level == max_level:
                            dirs.append((entry.name, normalize_path(entry.path)))
                        else:
                            dirs.extend(scan_level(entry.path, current_level + 1, max_level))
                return dirs
            custom_dirs = scan_level(path, 1, level)
            for dir_name, dir_path in custom_dirs:
                tree.insert("", "end", text=dir_name, values=(dir_path, "文件夹"))
            def get_full_path(item):
                return normalize_path(tree.item(item, "values")[0])

        elif mode == 4:
            tree["columns"] = ("type")
            tree.heading("#0", text="文件夹结构")
            tree.heading("type", text="类型")
            tree.column("type", anchor="center")
            def load_tree(parent_item, parent_path):
                try:
                    for entry in sorted(os.scandir(parent_path), key=lambda x: x.name):
                        if entry.is_dir():
                            item = tree.insert(parent_item, "end", text=entry.name, values=("文件夹"), open=False)
                            load_tree(item, normalize_path(os.path.join(parent_path, entry.name)))
                except Exception as e:
                    print(f"无法访问 {parent_path}: {e}")
            level1_dirs = sorted([entry.name for entry in os.scandir(path) if entry.is_dir()])
            for dir_name in level1_dirs:
                item = tree.insert("", "end", text=dir_name, values=("文件夹"), open=False)
                load_tree(item, normalize_path(os.path.join(path, dir_name)))
            def get_full_path(item):
                path_parts = []
                while item:
                    text = tree.item(item, "text")
                    path_parts.append(text)
                    item = tree.parent(item)
                return normalize_path(os.path.join(path, *reversed(path_parts)))

        # 模式1、2、3：右键菜单（复制、重命名）
        if mode in (1, 2, 3):
            context_menu = Menu(tree, tearoff=0)
            def copy_filename():
                selected_item = tree.focus()
                if selected_item:
                    filename = tree.item(selected_item, "text")
                    result_window.clipboard_clear()
                    result_window.clipboard_append(filename)
            def copy_filepath():
                selected_item = tree.focus()
                if selected_item:
                    filepath = tree.item(selected_item, "values")[0]
                    result_window.clipboard_clear()
                    result_window.clipboard_append(filepath)
            def rename_folder():
                selected_item = tree.focus()
                if selected_item:
                    old_name = tree.item(selected_item, "text")
                    old_path = tree.item(selected_item, "values")[0]
                    parent_dir = os.path.dirname(old_path)
                    rename_window = Toplevel(root)
                    rename_window.title("重命名")
                    try:
                        rename_window.iconbitmap(get_resource_path('Fmanager.ico'))
                    except Exception as e:
                        print(f"重命名窗口图标加载失败: {e}")
                    tk.Label(rename_window, text="请输入新的文件夹名：").pack(padx=20, pady=10)
                    entry_var = tk.StringVar(value=old_name)
                    entry = tk.Entry(rename_window, textvariable=entry_var, width=30)
                    entry.pack(padx=20, pady=5)
                    entry.select_range(0, tk.END)
                    entry.focus_set()
                    button_frame = tk.Frame(rename_window)
                    button_frame.pack(pady=10)
                    def on_ok():
                        nonlocal new_name
                        new_name = entry_var.get()
                        rename_window.destroy()
                    def on_cancel():
                        nonlocal new_name
                        new_name = None
                        rename_window.destroy()
                    new_name = None
                    tk.Button(button_frame, text="确定", command=on_ok).pack(side="left", padx=10)
                    tk.Button(button_frame, text="取消", command=on_cancel).pack(side="left", padx=10)
                    rename_window.transient(result_window)
                    rename_window.grab_set()
                    rename_window.wait_window()
                    if new_name and new_name != old_name:
                        try:
                            new_path = normalize_path(os.path.join(parent_dir, new_name))
                            os.rename(old_path, new_path)
                            tree.item(selected_item, text=new_name, values=(new_path, "文件夹"))
                        except Exception as e:
                            messagebox.showerror("重命名失败", str(e))
            context_menu.add_command(label="复制文件夹名", command=copy_filename)
            context_menu.add_command(label="复制文件路径", command=copy_filepath)
            context_menu.add_separator()
            context_menu.add_command(label="重命名", command=rename_folder)
            def show_context_menu(event):
                item = tree.identify_row(event.y)
                if item:
                    tree.focus(item)
                    tree.selection_set(item)
                    context_menu.post(event.x_root, event.y_root)
            tree.bind("<Button-3>", show_context_menu)

        # 全选/全不选/复制路径功能
        def select_all():
            for item in tree.get_children():
                tree.selection_add(item)
            update_selected_count()
        def deselect_all():
            tree.selection_remove(tree.selection())
            selected_count_label.config(text="已选择 0 个文件夹")
        def copy_selected_paths():
            selected_items = tree.selection()
            if not selected_items:
                return
            paths = [get_full_path(item) for item in selected_items]
            paths_text = "\n".join(paths)
            result_window.clipboard_clear()
            result_window.clipboard_append(paths_text)
        button_frame = tk.Frame(result_window)
        button_frame.pack(pady=5)
        tk.Button(button_frame, text="全选", command=select_all).pack(side="left", padx=5)
        tk.Button(button_frame, text="全不选", command=deselect_all).pack(side="left", padx=5)
        tk.Button(button_frame, text="复制所选文件地址", command=copy_selected_paths).pack(side="left", padx=5)

        selected_count_label = tk.Label(result_window, text="已选择 0 个文件夹")
        selected_count_label.pack(pady=5)
        def update_selected_count(event=None):
            selected_count = len(tree.selection())
            selected_count_label.config(text=f"已选择 {selected_count} 个文件夹")
        tree.bind("<<TreeviewSelect>>", update_selected_count)

        # 模式4：右键菜单功能
        if mode == 4:
            def select_level(level):
                tree.selection_remove(tree.selection())
                if level == 1:
                    for item in tree.get_children():
                        tree.selection_add(item)
                elif level == 2:
                    for top_item in tree.get_children():
                        for child in tree.get_children(top_item):
                            tree.selection_add(child)
                update_selected_count()
            def select_custom_level():
                try:
                    level = int(custom_level_entry_inner.get())
                    if level < 1:
                        raise ValueError
                    tree.selection_remove(tree.selection())
                    select_recursive(tree, "", level)
                    update_selected_count()
                except ValueError:
                    messagebox.showerror("错误", "请输入有效的层级数")
            def select_recursive(tree, parent, level):
                if level == 0:
                    return
                for item in tree.get_children(parent):
                    if level == 1:
                        tree.selection_add(item)
                    select_recursive(tree, item, level - 1)
            def on_menu_change(*args):
                menu_value = menu_var.get()
                if menu_value == 1:
                    select_level(1)
                elif menu_value == 2:
                    select_level(2)
                elif menu_value == 3:
                    select_custom_level()
            menu_var.trace("w", on_menu_change)
            def on_right_click(event):
                item = tree.identify_row(event.y)
                if item:
                    if item in tree.selection():
                        tree.selection_remove(item)
                    else:
                        for child in tree.get_children(item):
                            if child not in tree.selection():
                                tree.selection_add(child)
                    update_selected_count()
            tree.bind("<Button-3>", on_right_click)

        # 执行操作
        def execute_operation():
            """执行复制或剪切操作"""
            selected_items = tree.selection()
            if not selected_items:
                messagebox.showerror("错误", "请至少选择一个文件夹")
                return
            target_path = normalize_path(target_path_entry.get())
            if not target_path:
                messagebox.showerror("错误", "请输入目标路径")
                return
            operation = operation_var.get()
            selected_folders = [get_full_path(item) for item in selected_items]
            total_tasks = len(selected_folders)
            progress_window = Toplevel(root)
            progress_window.title("任务进度")
            progress_window.geometry("300x100")
            try:
                progress_window.iconbitmap(get_resource_path('Fmanager.ico'))
            except:
                pass
            tk.Label(progress_window, text="正在执行任务...").pack(pady=10)
            progress_bar = Progressbar(progress_window, orient="horizontal", length=200, mode="determinate")
            progress_bar.pack(pady=10)
            progress_bar["maximum"] = total_tasks
            completed_tasks = []
            for i, folder in enumerate(selected_folders):
                try:
                    folder_name = os.path.basename(folder)
                    if operation == 1:
                        shutil.copytree(folder, normalize_path(os.path.join(target_path, folder_name)))
                        completed_tasks.append(f"文件夹 '{folder_name}' 已复制到 '{target_path}'")
                    elif operation == 2:
                        shutil.move(folder, target_path)
                        completed_tasks.append(f"文件夹 '{folder_name}' 已移动到 '{target_path}'")
                except Exception as e:
                    completed_tasks.append(f"操作 '{folder_name}' 失败: {e}")
                progress_bar["value"] = i + 1
                progress_window.update()
            progress_window.destroy()
            result_window_final = Toplevel(root)
            result_window_final.title("任务完成情况")
            result_window_final.geometry("400x300")
            try:
                result_window_final.iconbitmap(get_resource_path('Fmanager.ico'))
            except:
                pass
            result_listbox = tk.Listbox(result_window_final, selectmode="extended")
            result_listbox.pack(expand=True, fill="both")
            for task in completed_tasks:
                result_listbox.insert(tk.END, task)
            scrollbar = Scrollbar(result_window_final, orient="vertical")
            scrollbar.config(command=result_listbox.yview)
            scrollbar.pack(side="right", fill="y")
            result_listbox.config(yscrollcommand=scrollbar.set)

        tk.Button(result_window, text="执行", command=execute_operation).pack(pady=10)

    except FileNotFoundError:
        messagebox.showerror("错误", f"路径 '{path}' 不存在")
    except NotADirectoryError:
        messagebox.showerror("错误", f"'{path}' 不是一个目录")
    except PermissionError:
        messagebox.showerror("错误", f"没有权限访问 '{path}'")

# 运行主循环
root.mainloop()