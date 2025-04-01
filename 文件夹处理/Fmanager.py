import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, Scrollbar
from tkinter.ttk import Treeview, Progressbar
import os
import shutil
import sys


def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


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
    path = filedialog.askdirectory()
    path_entry.delete(0, tk.END)
    path_entry.insert(0, path)


select_button = tk.Button(root, text="选择文件夹", command=select_path)
select_button.grid(row=0, column=2, padx=10, pady=10)


# 第二栏：显示模式选择
mode_label = tk.Label(root, text="选择显示模式：")
mode_label.grid(row=1, column=0, padx=10, pady=10)

mode_var = tk.IntVar(value=1)
mode_radio1 = tk.Radiobutton(root, text="只显示一级子文件夹名", variable=mode_var, value=1)
mode_radio1.grid(row=1, column=1, sticky="w")
mode_radio2 = tk.Radiobutton(root, text="只显示二级子文件夹名", variable=mode_var, value=2)
mode_radio2.grid(row=2, column=1, sticky="w")
mode_radio3 = tk.Radiobutton(root, text="按树形结构动态展开（自动预加载）", variable=mode_var, value=3)
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


# 显示文件夹列表的逻辑 indirect
def select_target_path(entry):
    path = filedialog.askdirectory()
    entry.delete(0, tk.END)
    entry.insert(0, path)


def list_dirs(path, mode):
    try:
        result_window = Toplevel(root)
        result_window.title("显示结果")
        result_window.geometry("400x500")
        result_window.minsize(400, 500)
        try:
            result_window.iconbitmap(get_resource_path('Fmanager.ico'))
        except Exception as e:
            print(f"二级窗口图标加载失败: {e}")

        # 操作选择
        operation_var = tk.IntVar(value=1)
        operation_label = tk.Label(result_window, text="选择操作：")
        operation_label.pack(anchor="w", padx=10, pady=5)
        tk.Radiobutton(result_window, text="复制到", variable=operation_var, value=1).pack(anchor="w", padx=20)
        tk.Radiobutton(result_window, text="剪切到", variable=operation_var, value=2).pack(anchor="w", padx=20)

        # 目标路径输入
        target_path_label = tk.Label(result_window, text="目标路径：")
        target_path_label.pack(anchor="w", padx=10, pady=5)
        target_path_entry = tk.Entry(result_window, width=50)
        target_path_entry.pack(anchor="w", padx=10)
        tk.Button(result_window, text="选择目标路径", command=lambda: select_target_path(target_path_entry)).pack(anchor="w", padx=10)

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

            def get_full_path(item):
                text = tree.item(item, "text")
                level1, level2 = text.split("/")
                return os.path.join(path, level1, level2)

        elif mode == 3:
            tree["columns"] = ("type")
            tree.heading("#0", text="文件夹结构")
            tree.heading("type", text="类型")
            tree.column("type", anchor="center")

            def load_tree(parent_item, parent_path):
                try:
                    for entry in sorted(os.scandir(parent_path), key=lambda x: x.name):
                        if entry.is_dir():
                            item = tree.insert(parent_item, "end", text=entry.name, values=("文件夹"), open=False)
                            load_tree(item, os.path.join(parent_path, entry.name))
                except Exception as e:
                    print(f"无法访问 {parent_path}: {e}")

            level1_dirs = sorted([entry.name for entry in os.scandir(path) if entry.is_dir()])
            for dir_name in level1_dirs:
                item = tree.insert("", "end", text=dir_name, values=("文件夹"), open=False)
                load_tree(item, os.path.join(path, dir_name))

            def get_full_path(item):
                path_parts = []
                while item:
                    text = tree.item(item, "text")
                    path_parts.append(text)
                    item = tree.parent(item)
                return os.path.join(path, *reversed(path_parts))

        # 全选/全不选功能
        def select_all():
            for item in tree.get_children():
                tree.selection_add(item)

        def deselect_all():
            tree.selection_remove(tree.selection())  # 移除所有当前选择的项目
            selected_count_label.config(text="已选择 0 个文件夹")

        button_frame = tk.Frame(result_window)
        button_frame.pack(pady=5)
        tk.Button(button_frame, text="全选", command=select_all).pack(side="left", padx=5)
        tk.Button(button_frame, text="全不选", command=deselect_all).pack(side="left", padx=5)

        selected_count_label = tk.Label(result_window, text="已选择 0 个文件夹")
        selected_count_label.pack(pady=5)

        def update_selected_count(event=None):
            selected_count = len(tree.selection())
            selected_count_label.config(text=f"已选择 {selected_count} 个文件夹")

        tree.bind("<<TreeviewSelect>>", update_selected_count)

        # 右键选择子文件夹
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
                        shutil.copytree(folder, os.path.join(target_path, folder_name))
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