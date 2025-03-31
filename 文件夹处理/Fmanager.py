import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, Scrollbar
from tkinter.ttk import Treeview, Progressbar, Style
import os
import shutil

# 创建主窗口
root = tk.Tk()
root.title("文件夹移动工具")

try:
    root.iconbitmap('Fmanager.ico')  # 更改主窗口图标
except:
    pass

# 第一栏：目标文件夹路径输入
path_label = tk.Label(root, text="目标文件夹路径：")
path_label.grid(row=0, column=0, padx=10, pady=10)

path_entry = tk.Entry(root, width=50)
path_entry.grid(row=0, column=1, padx=10, pady=10)

def select_path():
    path = filedialog.askdirectory()
    path_entry.delete(0, tk.END)
    path_entry.insert(0, path)

select_button = tk.Button(root, text="选择文件夹", command=select_path)
select_button.grid(row=0, column=2, padx=10, pady=10)

# 第二栏：显示模式选择
mode_label = tk.Label(root, text="选择显示模式：")
mode_label.grid(row=1, column=0, padx=10, pady=10)

mode_var = tk.IntVar()
mode_var.set(1)  # 默认选择第一个选项

mode_radio1 = tk.Radiobutton(root, text="只显示一级子文件夹名", variable=mode_var, value=1)
mode_radio1.grid(row=1, column=1, sticky="w")

mode_radio2 = tk.Radiobutton(root, text="只显示二级子文件夹名", variable=mode_var, value=2)
mode_radio2.grid(row=2, column=1, sticky="w")

mode_radio3 = tk.Radiobutton(root, text="按树形结构动态展开", variable=mode_var, value=3)
mode_radio3.grid(row=3, column=1, sticky="w")

# 确认按钮
def confirm():
    path = path_entry.get()
    mode = mode_var.get()
    if not path:
        messagebox.showerror("错误", "请输入目标文件夹路径")
        return
    list_dirs(path, mode)

confirm_button = tk.Button(root, text="确认", command=confirm)
confirm_button.grid(row=4, column=1, padx=10, pady=10)

# 显示文件夹列表的逻辑
def list_dirs(path, mode):
    try:
        # 创建二级窗口
        result_window = Toplevel(root)
        result_window.title("显示结果")
        result_window.geometry("400x500")
        result_window.minsize(400, 500)

        try:
            result_window.iconbitmap('Fmanager.ico')  # 更改二级窗口图标
        except:
            pass

        # 添加单选按钮和目标路径输入框
        operation_var = tk.IntVar()
        operation_var.set(1)

        operation_label = tk.Label(result_window, text="选择操作：")
        operation_label.pack(anchor="w", padx=10, pady=5)

        copy_radio = tk.Radiobutton(result_window, text="复制到", variable=operation_var, value=1)
        copy_radio.pack(anchor="w", padx=20)

        move_radio = tk.Radiobutton(result_window, text="剪切到", variable=operation_var, value=2)
        move_radio.pack(anchor="w", padx=20)

        target_path_label = tk.Label(result_window, text="目标路径：")
        target_path_label.pack(anchor="w", padx=10, pady=5)

        target_path_entry = tk.Entry(result_window, width=50)
        target_path_entry.pack(anchor="w", padx=10)

        # 创建 Treeview
        tree_frame = tk.Frame(result_window)
        tree_frame.pack(expand=True, fill="both", pady=10)

        scrollbar = Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")

        tree = Treeview(tree_frame, yscrollcommand=scrollbar.set, selectmode="extended")
        tree.pack(expand=True, fill="both")

        scrollbar.config(command=tree.yview)

        # 根据模式填充 Treeview
        if mode == 1:
            tree["columns"] = ("type")
            tree.heading("#0", text="一级子文件夹（按名称升序）")
            tree.heading("type", text="类型")

            level1_dirs = sorted([entry.name for entry in os.scandir(path) if entry.is_dir()])
            for dir_name in level1_dirs:
                tree.insert("", "end", text=dir_name, values=("文件夹"))

            # 模式1的 get_full_path
            def get_full_path(item):
                dir_name = tree.item(item, "text")
                return os.path.join(path, dir_name)

        elif mode == 2:
            tree["columns"] = ("type")
            tree.heading("#0", text="二级子文件夹（按名称升序）")
            tree.heading("type", text="类型")

            level1_dirs = sorted([entry.name for entry in os.scandir(path) if entry.is_dir()])
            for level1_dir in level1_dirs:
                level1_path = os.path.join(path, level1_dir)
                level2_dirs = sorted([entry.name for entry in os.scandir(level1_path) if entry.is_dir()])
                for level2_dir in level2_dirs:
                    tree.insert("", "end", text=f"{level1_dir}/{level2_dir}", values=("文件夹"))

            # 模式2的 get_full_path
            def get_full_path(item):
                text = tree.item(item, "text")  # 格式: "一级文件夹名/二级文件夹名"
                level1, level2 = text.split("/")
                return os.path.join(path, level1, level2)

        elif mode == 3:
            # 模式3：动态展开树形结构
            tree["columns"] = ("type")
            tree.heading("#0", text="文件夹结构（点击 + 展开）")
            tree.heading("type", text="类型")
            tree.column("type", anchor="center")

            # 加载一级文件夹
            level1_dirs = sorted([entry.name for entry in os.scandir(path) if entry.is_dir()])
            for dir_name in level1_dirs:
                dir_path = os.path.join(path, dir_name)
                has_subdirs = any(entry.is_dir() for entry in os.scandir(dir_path))
                item = tree.insert("", "end", text=dir_name, values=("文件夹"), open=False)
                if has_subdirs:
                    tree.insert(item, "end", text="加载中...")

            # 定义展开事件
            def on_tree_open(event):
                item = tree.focus()
                parent_path = get_full_path(item)
                tree.delete(*tree.get_children(item))
                try:
                    for entry in sorted(os.scandir(parent_path), key=lambda x: x.name):
                        if entry.is_dir():
                            sub_path = os.path.join(parent_path, entry.name)
                            has_subdirs = any(e.is_dir() for e in os.scandir(sub_path))
                            sub_item = tree.insert(item, "end", text=entry.name, values=("文件夹"), open=False)
                            if has_subdirs:
                                tree.insert(sub_item, "end", text="加载中...")
                except Exception as e:
                    messagebox.showerror("错误", f"无法访问 {parent_path}: {e}")

            tree.bind("<<TreeviewOpen>>", on_tree_open)

            # 获取完整路径
            def get_full_path(item):
                path_parts = []
                while item:
                    path_parts.append(tree.item(item, "text"))
                    item = tree.parent(item)
                return os.path.join(path, *reversed(path_parts))

        # 全选功能
        def select_all():
            for item in tree.get_children():
                tree.selection_add(item)

        # 全不选功能
        def deselect_all():
            tree.selection_remove(tree.get_children())  # 清空所有选中状态
            selected_count_label.config(text="已选择 0 个文件夹")

        # 创建按钮框架并居中
        button_frame = tk.Frame(result_window)
        button_frame.pack(pady=5)

        select_all_button = tk.Button(button_frame, text="全选", command=select_all)
        select_all_button.pack(side="left", padx=5)

        deselect_all_button = tk.Button(button_frame, text="全不选", command=deselect_all)
        deselect_all_button.pack(side="left", padx=5)

        # 显示已选择文件数量的标签
        selected_count_label = tk.Label(result_window, text="已选择 0 个文件夹")
        selected_count_label.pack(pady=5)

        def update_selected_count(event):
            selected_count = len(tree.selection())
            selected_count_label.config(text=f"已选择 {selected_count} 个文件夹")

        tree.bind("<<TreeviewSelect>>", update_selected_count)

        # 获取所有子文件夹的辅助函数
        def get_all_subfolders(item):
            subfolders = []
            for child in tree.get_children(item):
                subfolders.append(child)
                subfolders.extend(get_all_subfolders(child))  # 递归获取所有子文件夹
            return subfolders

        # 右键点击事件：选择或取消选择子文件夹
        def on_right_click(event):
            item = tree.identify_row(event.y)  # 获取右键点击的项
            if item:
                subfolders = get_all_subfolders(item)  # 获取所有子文件夹
                if subfolders:
                    # 检查子文件夹是否已被选中
                    if any(child in tree.selection() for child in subfolders):
                        # 如果有任意子文件夹被选中，则取消选中所有子文件夹
                        for child in subfolders:
                            tree.selection_remove(child)
                    else:
                        # 否则，选中所有子文件夹
                        for child in subfolders:
                            tree.selection_add(child)
                # 更新选中数量
                update_selected_count(None)

        # 绑定右键点击事件
        tree.bind("<Button-3>", on_right_click)

        # 执行复制或剪切操作的函数
        def execute_operation():
            selected_items = tree.selection()
            if not selected_items:
                messagebox.showerror("错误", "请至少选择一个文件夹")
                return

            target_path = target_path_entry.get()
            if not target_path:
                messagebox.showerror("错误", "请输入目标路径")
                return

            operation = operation_var.get()
            selected_folders = [get_full_path(item) for item in selected_items]

            total_tasks = len(selected_folders)
            if total_tasks == 0:
                messagebox.showerror("错误", "没有选中的文件夹")
                return

            progress_window = Toplevel(root)
            progress_window.title("任务进度")
            progress_window.geometry("300x100")

            progress_label = tk.Label(progress_window, text="正在执行任务...")
            progress_label.pack(pady=10)

            progress_bar = Progressbar(progress_window, orient="horizontal", length=200, mode="determinate")
            progress_bar.pack(pady=10)
            progress_bar["maximum"] = total_tasks

            completed_tasks = []
            for i, folder in enumerate(selected_folders):
                try:
                    folder_name = os.path.basename(folder)
                    if operation == 1:  # 复制
                        shutil.copytree(folder, os.path.join(target_path, folder_name))
                        completed_tasks.append(f"文件夹 '{folder_name}' 已复制到 '{target_path}'")
                    elif operation == 2:  # 剪切
                        shutil.move(folder, target_path)
                        completed_tasks.append(f"文件夹 '{folder_name}' 已移动到 '{target_path}'")
                except Exception as e:
                    completed_tasks.append(f"操作 '{folder_name}' 失败: {e}")
                progress_bar["value"] = i + 1
                progress_window.update()

            progress_window.destroy()

            result_window = Toplevel(root)
            result_window.title("任务完成情况")
            result_window.geometry("400x300")

            result_listbox = tk.Listbox(result_window, selectmode="extended")
            result_listbox.pack(expand=True, fill="both")

            for task in completed_tasks:
                result_listbox.insert(tk.END, task)

            scrollbar = Scrollbar(result_window, orient="vertical")
            scrollbar.config(command=result_listbox.yview)
            scrollbar.pack(side="right", fill="y")
            result_listbox.config(yscrollcommand=scrollbar.set)

        execute_button = tk.Button(result_window, text="执行", command=execute_operation)
        execute_button.pack(pady=10)

    except FileNotFoundError:
        messagebox.showerror("错误", f"路径 '{path}' 不存在")
    except NotADirectoryError:
        messagebox.showerror("错误", f"'{path}' 不是一个目录")
    except PermissionError:
        messagebox.showerror("错误", f"没有权限访问 '{path}'")

# 运行主循环
root.mainloop()