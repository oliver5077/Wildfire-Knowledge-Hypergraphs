import os
import json
from collections import defaultdict

# 定义知识超图的数据结构
knowledge_hypergraph = {
    "hypergraph-data": {
        "name": "fire-events"
    },
    "node-data": {},  # 存储节点信息
    "edge-data": {},  # 存储边信息
    "edge-dict": {}   # 存储边和超边的连接关系
}

# 用于存储实体到唯一 ID 的映射
entity_to_id = {}
current_id = 1

def get_entity_id(entity_name):
    """为实体分配唯一 ID（字符串形式），如果实体已存在则返回现有 ID"""
    global current_id
    if entity_name not in entity_to_id:
        entity_to_id[entity_name] = str(current_id)  # 将 ID 转换为字符串
        current_id += 1
    return entity_to_id[entity_name]

def parse_txt_file(file_path):
    """解析单个 txt 文件并更新知识超图"""
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # 假设文件内容是以特定格式存储的结构化数据
    # 这里需要根据实际文件内容编写解析逻辑
    # 以下是一个示例解析逻辑
    lines = content.split("\n")
    for line in lines:
        if line.startswith("("):  # 假设边和超边的定义以括号开头
            parts = line.strip("()").split(", ")
            relation_type = parts[0].strip('"')
            entities = [e.strip('"') for e in parts[1:]]

            # 为实体分配唯一 ID（字符串形式）
            entity_ids = [get_entity_id(e) for e in entities]

            # 添加边或超边
            edge_id = str(len(knowledge_hypergraph["edge-data"]))  # 边 ID 为字符串
            knowledge_hypergraph["edge-data"][edge_id] = {
                "type": relation_type
            }
            knowledge_hypergraph["edge-dict"][edge_id] = entity_ids
        elif line.startswith("{"):  # 假设边和超边的定义以括号开头
            parts = line.strip("{}").split(", ")
            relation_type = parts[0].strip('"')
            entities = [e.strip('"') for e in parts[1:]]

            # 为实体分配唯一 ID（字符串形式）
            entity_ids = [get_entity_id(e) for e in entities]

            # 添加边或超边
            edge_id = str(len(knowledge_hypergraph["edge-data"]))  # 边 ID 为字符串
            knowledge_hypergraph["edge-data"][edge_id] = {
                "type": relation_type
            }
            knowledge_hypergraph["edge-dict"][edge_id] = entity_ids

def process_txt_files(directory):
    """处理目录下的所有 txt 文件"""
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory, filename)
            parse_txt_file(file_path)

    # 添加节点信息
    for entity_name, entity_id in entity_to_id.items():
        knowledge_hypergraph["node-data"][entity_id] = {
            "name": entity_name
        }

def save_to_json(output_path):
    """将知识超图保存为 JSON 文件"""
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(knowledge_hypergraph, json_file, indent=4)
# 主程序
if __name__ == "__main__":
    # 设置输入目录和输出文件路径
    input_directory = ""  # 替换为你的 txt 文件目录
    output_json_path = "KnowledgeHypergraphs/knowledge_hypergraph.json"  # 输出 JSON 文件路径

    # 处理 txt 文件并生成知识超图
    process_txt_files(input_directory)

    # 保存为 JSON 文件
    save_to_json(output_json_path)

    print(f"知识超图已生成并保存到 {output_json_path}")