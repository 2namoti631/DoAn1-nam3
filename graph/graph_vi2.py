import pandas as pd
import networkx as nx
from pyvis.network import Network
from datetime import datetime
# vẽ thể hiện được theo khung giờ bài viết mới được đnăg  

# Thay đổi thời gian UTC sang datetime
def time_change(time):
    post_time = datetime.utcfromtimestamp(time)
    return post_time

# Vẽ biểu đồ thể hiện
def create_reddit_graph_v2(file_path, output_html='graph_v2.html'):
    # Đọc dữ liệu từ file csv
    data = pd.read_csv(file_path)

    # Tạo đồ thị có hướng
    G = nx.DiGraph()
    node_sizes = {}
    post_time = None

    # Thêm các nút và cạnh vào đồ thị
    for _, row in data.iterrows():
        node_id = str(row["Comment_ID"])  # ID của bình luận hoặc bài viết
        parent_id = str(row["Parent_ID"]) if pd.notnull(row["Parent_ID"]) else None  # ID của bình luận cha
        current_time = time_change(row['Created_UTC'])
        
        # Kiểm tra xem đây là Post hay Comment
        if row["Type"] == "Post":
            author = str(row["Author"])
            post_time= current_time.isoformat()
            # Thêm nút cho bài viết
            G.add_node(node_id, type="Post", content=row["Content"], author=author, timestamp=current_time.isoformat())  # Chuyển đổi datetime thành chuỗi
            node_sizes[node_id] = row['Score']
        elif row["Type"] == "Comment":
            author = str(row["Author"])
            # Thêm nút cho bình luận
            G.add_node(node_id, type="Comment", content=row["Content"], author=author, timestamp=current_time.isoformat())  # Chuyển đổi datetime thành chuỗi
            node_sizes[node_id] = row['Score']

            # Thêm cạnh từ bình luận cha đến bình luận con nếu có parent_id
            if parent_id and parent_id in G:
                
                time_diff = ( current_time - datetime.fromisoformat(post_time) ).total_seconds() / 3600  # Chuyển chuỗi về datetime
                if post_time is not None:
                    time_diff = ( current_time - datetime.fromisoformat(post_time) ).total_seconds() / 3600  # Chuyển chuỗi về datetime
                if time_diff <= 1:
                    edge_color = "red"
                elif 1< time_diff <= 8:
                    edge_color = 'orange'
                elif 8 <time_diff <= 24 :
                    edge_color = "yellow"
                elif time_diff > 24:
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
        timestamp = G.nodes[node['id']]["timestamp"]  # Đã là chuỗi ISO
        node['title'] = f"Author: {author}\nContent: {content}\nTimestamp: {timestamp}"

    # Đặt màu cho các cạnh
    for edge in nt.edges:
        edge_color = G.edges[edge['from'], edge['to']]["color"]
        edge["color"] = edge_color

    # Lưu đồ thị vào file HTML
    nt.save_graph(output_html)
    print(f"Đồ thị đã được lưu vào '{output_html}'")
