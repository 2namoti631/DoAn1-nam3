import pandas as pd
import networkx as nx
from pyvis.network import Network

def create_reddit_graph(file_path, output_html="post_graph.html"):
    # Đọc dữ liệu từ file CSV
    data = pd.read_csv(file_path)

    # Tạo đồ thị có hướng để thể hiện mối quan hệ cha - con
    G = nx.DiGraph()  
    node_sizes = {}

    # Thêm các nút và cạnh vào đồ thị
    for _, row in data.iterrows():
        node_id = str(row["Comment_ID"])  # ID của bình luận hoặc bài viết
        parent_id = str(row["Parent_ID"]) if pd.notnull(row["Parent_ID"]) else None  # ID của bình luận cha

        # Kiểm tra xem đây là Post hay Comment
        if row["Type"] == "Post":
            author = str(row["Author"])
            # Thêm nút cho bài viết
            G.add_node(node_id, type="Post", content=row["Content"], author=author)
            node_sizes[node_id] = row['Score']
        elif row["Type"] == "Comment":
            author = str(row["Author"])
            # Thêm nút cho bình luận
            G.add_node(node_id, type="Comment", content=row["Content"], author=author)
            node_sizes[node_id] = row['Score']

            # Thêm cạnh từ bình luận cha đến bình luận con nếu có parent_id
            if parent_id and parent_id in G:
                G.add_edge(parent_id, node_id)

    # Tạo đồ thị với pyvis
    nt = Network(width="1000px", height="800px", directed=True)
    nt.from_nx(G)

    # Đặt màu sắc và kích thước cho các node
    for node in nt.nodes:
        node_type = G.nodes[node['id']]["type"]
        node_score = node_sizes[node['id']]
        
        # Đặt màu sắc dựa trên loại node
        node['color'] = "lightblue" if node_type == "Post" else "lightgreen"

        # Điều chỉnh kích thước node
        if node_score > 100:
            node['size'] = 17
        elif 50 <= node_score <=100:
            node['size'] = 13
        else:
            node['size'] = 6

        # Đặt tiêu đề node hiển thị tác giả và nội dung khi di chuột qua
        content = G.nodes[node['id']]["content"]
        author = G.nodes[node['id']]["author"]
        node['title'] = f"Author: {author}\nContent: {content}"

    # Lưu đồ thị vào file HTML
    nt.save_graph(output_html)
    print(f"Đồ thị đã được lưu vào '{output_html}'")

