import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
from datetime import datetime

# Hàm chuyển đổi thời gian UTC sang datetime
def time_change(time):
    post_time = datetime.utcfromtimestamp(time)
    return post_time

# Hàm tạo đồ thị từ file CSV
def create_reddit_graph_v3(filtered_df, output_html='graph_v2.html'):
    # Tạo đồ thị có hướng
    G = nx.DiGraph()
    node_sizes = {}
    post_time = None

    # Thêm các nút và cạnh vào đồ thị
    for _, row in filtered_df.iterrows():
        node_id = str(row["Comment_ID"])  # ID của bình luận hoặc bài viết
        parent_id = str(row["Parent_ID"]) if pd.notnull(row["Parent_ID"]) else None  # ID của bình luận cha
        current_time = time_change(row['Created_UTC'])

        # Kiểm tra xem đây là Post hay Comment
        if row["Type"] == "Post":
            author = str(row["Author"])
            post_time = current_time.isoformat()
            # Thêm nút cho bài viết
            G.add_node(node_id, type="Post", content=row["Content"], author=author, timestamp=current_time.isoformat())
            node_sizes[node_id] = row['Score']
        elif row["Type"] == "Comment":
            author = str(row["Author"])
            # Thêm nút cho bình luận
            G.add_node(node_id, type="Comment", content=row["Content"], author=author, timestamp=current_time.isoformat())
            node_sizes[node_id] = row['Score']

            # Thêm cạnh từ bình luận cha đến bình luận con nếu có parent_id
            if parent_id and parent_id in G:
                time_diff = (current_time - datetime.fromisoformat(post_time)).total_seconds() / 3600 if post_time else 0
                if time_diff <= 1:
                    edge_color = "red"
                elif 1 < time_diff <= 8:
                    edge_color = 'orange'
                elif 8 < time_diff <= 24:
                    edge_color = "yellow"
                else:
                    edge_color = "gray"

                G.add_edge(parent_id, node_id, color=edge_color)

    # Tạo đồ thị với pyvis
    nt = Network(width="1000px", height="800px", directed=True)
    nt.from_nx(G)

    # Đặt màu sắc và kích thước cho các node
    for node in nt.nodes:
        node_type = G.nodes[node['id']]["type"]
        node_score = node_sizes[node['id']]

        # Đặt màu sắc dựa trên loại node
        if node_type == 'Post':
            node['color'] = "lightblue"
        else:
            node['color'] = "lightgreen"

        # Điều chỉnh kích thước node
        if node_score > 100:
            node['size'] = 17
        elif 50 <= node_score <= 100:
            node['size'] = 13
        else:
            node['size'] = 6

        # Đặt tiêu đề node hiển thị tác giả và nội dung khi di chuột qua
        content = G.nodes[node['id']]["content"]
        author = G.nodes[node['id']]["author"]
        timestamp = G.nodes[node['id']]["timestamp"]
        node['title'] = f"Author: {author}\nContent: {content}\nTimestamp: {timestamp}"

    # Đặt màu cho các cạnh
    for edge in nt.edges:
        edge_color = G.edges[edge['from'], edge['to']]["color"]
        edge["color"] = edge_color

    # Lưu đồ thị vào file HTML
    nt.save_graph(output_html)
    return output_html