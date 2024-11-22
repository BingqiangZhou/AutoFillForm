import os
import sys
import shutil
import pyinstxtractor # https://github.com/WithSecureLabs/python-exe-unpacker
import uncompyle6

## 解压exe文件，得到pyc文件
#########################################################################
exe_file = r"E:/Projects/AutoFillForm/V3/Materials/x6.exe"
sys.argv = ['pyinstxtractor', exe_file]
pyinstxtractor.main()
# 恢复当前目录位置
os.chdir("..")

## 从pyc文件中提取校验头，用于后续修复pyc文件
#########################################################################
pyc_dir = os.path.basename(exe_file)+"_extracted"

# 获取pyc文件校验头
pyz_dir = f"{pyc_dir}/PYZ-00.pyz_extracted"
for pyc_file in os.listdir(pyz_dir):
    if pyc_file.endswith(".pyc"):
        file = f"{pyz_dir}/{pyc_file}"
        break
with open(file, "rb") as f:
    head = f.read(4)
list(map(hex, head))

pycfile_tmp_path = "pycfile_tmp"
if os.path.exists("pycfile_tmp"):
    shutil.rmtree("pycfile_tmp")
os.mkdir("pycfile_tmp")

## 修复没有后缀的文件为pyc文件
#########################################################################
# 预处理pyc文件修护校验头
pycfile_tmp_directory = os.path.join(os.getcwd(), pycfile_tmp_path)
# 遍历源目录下的所有文件和文件夹
for filename in os.listdir(pyc_dir):
    source_path = os.path.join(pyc_dir, filename)
    # 检查是否为文件
    if os.path.isfile(source_path):
        # 分割文件名和后缀
        base, ext = os.path.splitext(filename)
        # 如果没有后缀名
        if ext == "":
            # 新文件名添加后缀.pyc
            new_filename = base + ".pyc"
            # 创建目标文件的完整路径
            target_path = os.path.join(pycfile_tmp_directory, new_filename)
            with open(source_path, "rb") as read, open(target_path, "wb") as write:
                write.write(head)
                write.write(b"\0"*12)
                write.write(read.read())

## 反编译pyc文件为py文件
#########################################################################
py_result_path = "py_result"
if not os.path.exists(py_result_path):
    os.mkdir(py_result_path)
for pyc_file in os.listdir(pycfile_tmp_path):
    pyc_file_path = os.path.join(os.getcwd(), pycfile_tmp_path, pyc_file)
    py_file_path = os.path.join(os.getcwd(), py_result_path, pyc_file[:-1])
    with open(py_file_path, 'w') as f:
        uncompyle6.decompile_file(pyc_file_path, f)

    # print('uncompyle6', pyc_file_path, '-o', py_file_path)
    # sys.argv = ['uncompyle6', pyc_file_path, '-o', py_file_path]
    # sys.argv = ['uncompyle6', pyc_file_path, '-o', py_file_path]
    # sys.argv = ['uncompyle6', f'{py_result_path}\{pyc_file}>{pycfile_tmp_path}\{pyc_file[:-1]}']
    # uncompile.main_bin()