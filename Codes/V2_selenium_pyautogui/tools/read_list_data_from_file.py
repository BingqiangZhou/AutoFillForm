import os
import ast
import yaml

def get_valid_number(max_num):
    while True:
        # 请求用户输入
        user_input = input(f"请输入一个介于1到{max_num}之间的数字: ")

        try:
            # 尝试将输入转换为整数
            number = int(user_input)
            # 检查数字是否在0到10之间
            if 0 <= number <= max_num:
                return number
            else:
                print(f"错误：数字必须在1到{max_num}之间，请重新输入。")
        except ValueError:
            # 如果转换失败，说明输入不是整数
            print("错误：请输入一个有效的数字。")

def list_yaml_files(directory):
    """
    List all YAML files in the given directory.
    Args:
    directory (str): The path to the directory to search for YAML files.
    
    Returns:
    list: A list of paths to YAML files.
    """
    # 初始化一个列表来存放找到的YAML文件
    yaml_files = []

    # 遍历目录中的所有文件和子目录
    for item in os.listdir(directory):
        # 检查文件名是否以.yaml或.yml结尾
        if item.endswith('.yaml') or item.endswith('.yml'):
            # 将匹配的文件添加到列表中
            # yaml_files.append(os.path.join(directory, item))
            yaml_files.append(item)

    return yaml_files

def select_file_in_floder(floder_path):
    file_list = list_yaml_files(floder_path)
    file_num = len(file_list)
    if len(file_list) > 1:
        print("找到以下规则文件，请选择规则文件序号")
        for index, file_path in enumerate(file_list):
            print(index+1, "\t", file_path)
        input_file_num = get_valid_number(file_num)
        return file_list[input_file_num - 1]
    elif file_num == 0:
        print("找到一个规则文件，已自动选择该文件数据作为规则")
        return file_list[0]
    else:
        print("未找到规则文件")
        return None

def read_txt_file_to_list_object(file_path):
    # Reading the data from the file
    with open(file_path, 'r', encoding="utf-8") as file:
        data_from_file = file.read()

    # Evaluating the string to convert it into a Python object
    question_infos = ast.literal_eval(data_from_file)
    return question_infos

def read_yaml_file(file_path):
    # Reading the data from the file
    with open(file_path, 'r', encoding="utf-8") as file:
        data_from_file = yaml.safe_load(file)

    return data_from_file

def read_list_data_from_file(floder_path):
    file_name = select_file_in_floder(floder_path)
    if file_name is not None:
        file_path = os.path.join(floder_path, file_name)
        list_info = read_txt_file_to_list_object(file_path)
        # list_info = read_yaml_file(file_path)
        print(file_path, list_info)
        return list_info
    else:
        return None
    
def read_data_from_yaml_file(floder_path):
    file_name = select_file_in_floder(floder_path)
    if file_name is not None:
        file_path = os.path.join(floder_path, file_name)
        # list_info = read_txt_file_to_list_object(file_path)
        list_info = read_yaml_file(file_path)
        # print(file_path, list_info)
        return list_info
    else:
        return None


if __name__ == "__main__":
    floder_path = "../rules"
    read_list_data_from_file(floder_path)

