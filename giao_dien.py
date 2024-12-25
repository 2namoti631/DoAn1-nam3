import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
from datetime import datetime
from graph.graph_final import create_reddit_graph_v3

# Hàm lọc dữ liệu với mối quan hệ cha-con đúng
def get_thread_data(df, post_id):
    thread_data = []
    posts = df[df["Comment_ID"] == post_id]
    thread_data.append(posts)
    
    parent_ids = posts["Comment_ID"].tolist()
    
    while parent_ids:
        comments = df[df["Parent_ID"].isin(parent_ids)]
        thread_data.append(comments)
        parent_ids = comments["Comment_ID"].tolist()
    
    return pd.concat(thread_data).drop_duplicates()

# Hàm đếm các bình luận theo điểm số
def count_comments_by_score(df):
    above_100 = df[df['Score'] > 100].shape[0]
    between_50_and_100 = df[(df['Score'] > 50) & (df['Score'] < 100)].shape[0]
    above_50 = df[df['Score'] > 50].shape[0]
    
    return  above_100, between_50_and_100, above_50

# Hàm tìm tác giả có nhiều bình luận nhất
def find_top_author(df):
    # Không cần đọc lại CSV, vì df đã là DataFrame
    author_comment_count = df.groupby('Author').size()
    author_comment_count_sorted = author_comment_count.sort_values(ascending=False)
    top_author = author_comment_count_sorted.idxmax()
    top_author_comment_count = author_comment_count_sorted.max()
    
    return top_author, top_author_comment_count


# Giao diện Streamlit
st.title("Phân Tích Đồ Thị Reddit")
st.sidebar.header("Tùy chọn")

# Tải dữ liệu
uploaded_file = st.sidebar.file_uploader("Tải lên file CSV dữ liệu ", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Làm sạch dữ liệu
    df["Content"] = df["Content"].str.strip()
    df["Comment_ID"] = df["Comment_ID"].astype(str)
    df["Parent_ID"] = df["Parent_ID"].astype(str)

    st.write("### Dữ liệu gốc:")
    st.dataframe(df, width=3000)

    # Lấy danh sách các Comment_ID của bài viết (Type == "Post")
    post_ids = df[df["Type"] == "Post"]["Comment_ID"].unique()
    st.write("### Danh sách id của các bài viết có trong dữ liệu:")
    st.write(post_ids)

    # Người dùng nhập Comment_ID của bài viết
    input_post_id = st.sidebar.text_input("Nhập ID của bài viết:")

    if input_post_id.strip():
        # Kiểm tra Comment_ID có hợp lệ không
        if input_post_id in post_ids:
            st.success(f"Đã chọn bài viết với ID: {input_post_id}")

            # Lọc dữ liệu cho bài viết và các bình luận liên quan với mối quan hệ cha-con đúng
            filtered_df = get_thread_data(df, input_post_id)

            st.write("### Dữ liệu được lọc theo bài viết đã chọn:")
            st.dataframe(filtered_df, width=1500)

            # Tạo và hiển thị đồ thị
            if st.sidebar.button("Tạo đồ thị"):
                output_html = create_reddit_graph_v3(filtered_df)
                st.write("### Đồ thị đã được tạo:")
                with open(output_html, "r") as f:
                    st.components.v1.html(f.read(), height=1000, width=1000, scrolling=True)

            # Tính số lượng bình luận theo điểm số
            above_100, between_50_and_100, above_50 = count_comments_by_score(filtered_df)
            # Tìm tác giả có nhiều bình luận nhất
            top_author, top_author_comment_count = find_top_author(filtered_df)
            st.write("### Phân tích sơ bộ:")
            st.write(f"Số bình luận score trên 100: {above_100} ")
            st.write(f"Số bình luận score điểm từ 50-100:{between_50_and_100}")
            st.write(f"Số bình luận score dưới 50:{above_50}")
            st.write(f"Tác giả bình luận nhiều nhất: {top_author} với {top_author_comment_count} bình luận ")
        else:
            st.error(f"Comment_ID '{input_post_id}' không phải của một bài viết hợp lệ. Vui lòng nhập lại.")
