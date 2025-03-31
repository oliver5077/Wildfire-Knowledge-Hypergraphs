"""
===================================
Simple hypergraph with convex hulls
===================================

Draw simple hypergraph with convex hulls and manual layout.
"""

import matplotlib.pyplot as plt
import random
import xgi
import json
import networkx as nx
import xgi
import json
import numpy as np
import pandas as pd
# 读取超图数据
with open('KnowledgeHypergraphs/knowledge_hypergraph.json', 'r') as f:
    data = json.load(f)

# 提取节点数据和边数据
nodes = data['node-data']
edges = data['edge-dict']

# 创建一个超图
H = xgi.Hypergraph()

# 添加节点到超图
for node_id, node_info in nodes.items():
    H.add_node(node_id, name=node_info.get('name', f"Node {node_id}"))
    # print(f"添加节点：ID={node_id}, 名称={node_info.get('name', f'Node {node_id}')}")

# 添加边到超图
for edge_id, edge_nodes, in edges.items():
     if len(edge_nodes) != 0:
            H.add_edge(edge_nodes)
    # print(f"添加边：ID={edge_id}, 连接节点={edge_nodes}")

 # 打印超图的节点和边
# print("\n超图的节点和边：")
# print(f"节点数: {len(H.nodes)}, 边数: {len(H.edges)}")
#
# # 打印超图节点的属性
# print("\n节点及其属性：")
# for node_id in H.nodes:
#     print(f"节点 ID: {node_id}, 属性: {H._node[node_id]}")
#
# # 打印超图边的详细信息
# print("\n边的详细信息：")
# for edge_id in H.edges:
#     print(f"边 ID: {edge_id}, 连接的节点: {H.edge[edge_id]}")

# with open('drawfire.json', 'r') as f:
#     data = json.load(f)
# # 提取节点数据和边数据
# nodes = data['node-data']
# edges = data['edge-dict']

#自定义布局，例如使用圆形布局
# fig, ax = plt.subplots(figsize=(10, 10))
# xgi.draw(
#     H,
#     node_size=H.nodes.degree,
#     node_lw=H.nodes.average_neighbor_degree,
#     node_fc=H.nodes.degree,
#     ax=ax,
# hull=True
# );
#统计零散边
# isolated_nodes = H.nodes.isolates()
# print("Number of isolated nodes: ", len(isolated_nodes))
# duplicated_edges = H.edges.duplicates()
# print("Number of duplicated edges: ", len(duplicated_edges))

#柱状图统计
list_of_edges_sizes = H.edges.size.aslist()

df = pd.DataFrame(list_of_edges_sizes, columns=["Edge Size"])
frequency_df = df["Edge Size"].value_counts().reset_index()
frequency_df.columns = ["Edge Size", "Frequency"]
frequency_df = frequency_df.sort_values("Edge Size")
excel_filename = "edge_size_distribution.xlsx"
frequency_df.to_excel(excel_filename, index=False)

ax = plt.subplot(111)
ax.hist(
    list_of_edges_sizes,
    bins=range(min(list_of_edges_sizes), max(list_of_edges_sizes) + 1, 1),
)
ax.set_xlabel("Edge size")
ax.set_ylabel("Frequency")
#
# #节点度统计
list_of_nodes_degrees = H.nodes.degree.aslist()
df = pd.DataFrame(list_of_nodes_degrees, columns=["Node Size"])
frequency_df = df["Node Size"].value_counts().reset_index()
frequency_df.columns = ["Node Size", "Frequency"]
frequency_df = frequency_df.sort_values("Node Size")
excel_filename = "Node_size_distribution.xlsx"
frequency_df.to_excel(excel_filename, index=False)
ax = plt.subplot(111)
ax.hist(
    list_of_nodes_degrees,
     bins=range(min(list_of_nodes_degrees), max(list_of_nodes_degrees) + 1, 1),
)
ax.set_xlabel("Degree")
ax.set_ylabel("Frequency")

#关联矩阵
# I = xgi.incidence_matrix(H, sparse=False)
# plt.spy(I, aspect="auto")
# plt.xlabel("Hyperedges")
# plt.ylabel("Nodes")
#显示name
# fig, ax = plt.subplots(figsize=(10, 8))
# xgi.draw(H, ax=ax)
#  pos = nx.spring_layout(H)
# node_labels = {node_id: H.node[node_id]['name'] for node_id in H.nodes}
# nx.draw_networkx_labels(H.to_networkx(), pos, labels=node_labels, font_size=10, font_color='black', font_weight='bold')
#超图绘制


# 清理超图
# xgi.is_connected(H)
# isolated_nodes = H.nodes.isolates()
# print("Number of isolated nodes: ", len(isolated_nodes))
# duplicated_edges = H.edges.duplicates()
# print("Number of duplicated edges: ", len(duplicated_edges))

# isolated_nodes = [node for node, degree in H.nodes.degree.items() if degree == 0]
# print("Number of isolated_nodes: ", isolated_nodes)
# for node in isolated_nodes:
#     H.remove_node(node, strong=True, remove_empty=True)
# H_cleaned = H.cleanup(
#     multiedges=False, singletons=False, isolates=False, relabel=True, in_place=False
# )
# H_cleaned = H.cleanup(
#     multiedges=True, singletons=True, isolates=False, relabel=True, in_place=False
# )





# 打印超图
edge_order = np.arange(len(H.edges))
cmap = plt.get_cmap('BrBG')
norm = plt.Normalize(vmin=edge_order.min(), vmax=edge_order.max())  # 定义归一化范围
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
pos = xgi.drawing.layout.pairwise_spring_layout(H)

fig, ax = plt.subplots(figsize=(10, 10))
ax, collections = xgi.draw(
    H,
    ax=ax,
hull=True,
radius=0.01,
node_lw = 0.2,
    node_size=H.nodes.degree,
node_fc=H.nodes.degree,
pos = pos
)
node_col, _, edge_col = collections

plt.colorbar(node_col, label="Node degree")
plt.colorbar(edge_col, label="Edge size")



# xgi.draw(H_cleaned, hull=True, edge_fc_cmap=cmap, edge_fc_norm=norm,pos=pos,radius=0.1)
# 绘制超图



#示例超图可视化
# pos = xgi.drawing.layout.barycenter_kamada_kawai_layout(H)
# fig, ax = plt.subplots(figsize=(10, 8))
# xgi.draw(H, ax=ax, hull=True, pos=pos, node_size=15,edge_fc_cmap= 'cividis',radius=0.1)



# pos = xgi.drawing.layout.random_layout(H)
# fig, ax = plt.subplots(figsize=(10, 8))
# xgi.draw(H,ax=ax, node_labels=True,hull=True,node_size=40,pos=pos)

plt.show()