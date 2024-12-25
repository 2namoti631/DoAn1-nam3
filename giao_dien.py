import pandas as pd
import streamlit as st
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline
import networkx as nx
from pyvis.network import Network
from datetime import datetime
from graph.graph_final import create_reddit_graph_v3

# Bước 1: Phân tích cảm xúc sơ bộ bằng VADER
def analyze_vader(df, text_column):
    analyzer = SentimentIntensityAnalyzer()
    results = []

    for text in df[text_column]:
        # Chuyển đổi giá trị thành chuỗi nếu nó không phải chuỗi
        if isinstance(text, str):
            score = analyzer.polarity_scores(text)
        else:
            score = analyzer.polarity_scores(str(text))  # Chuyển đổi thành chuỗi nếu là float, NaN, etc.

        compound = score['compound']
        if compound > 0.5:
            sentiment = "Positive"
        elif compound < -0.5:
            sentiment = "Negative"
        else:
            sentiment = "Unclear"
        results.append(sentiment)
    
    df.loc[:, 'VADER Sentiment'] = results
    return df

# Bước 2: Phân tích sâu hơn bằng Transformers
def analyze_transformers(df, text_column):
    classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    transformer_results = []

    for text in df[text_column]:
        try:
            result = classifier(text)[0]
            label = result['label']
            transformer_results.append(label)
        except Exception as e:
            transformer_results.append("Error")
    
    df.loc[:, 'Transformers Sentiment'] = transformer_results
    return df

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

# Hàm tính tỉ lệ cảm xúc
def calculate_vader_ratios(df):
    sentiment_counts = df['VADER Sentiment'].value_counts()
    total_comments = len(df)

    positive_ratio = sentiment_counts.get('Positive', 0) / total_comments * 100
    negative_ratio = sentiment_counts.get('Negative', 0) / total_comments * 100
    unclear_ratio = sentiment_counts.get('Unclear', 0) / total_comments * 100

    return positive_ratio, negative_ratio, unclear_ratio

# Hàm tìm tác giả có nhiều bình luận nhất
def find_top_author(df):
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

            # Phân tích cảm xúc bằng VADER và Transformers
            filtered_df = analyze_vader(filtered_df, 'Content')
            filtered_df = analyze_transformers(filtered_df, 'Content')

            st.write("### Dữ liệu với kết quả phân tích cảm xúc:")
            st.dataframe(filtered_df, width=1500)

            # Tính tỉ lệ cảm xúc
            positive_ratio, negative_ratio, unclear_ratio = calculate_vader_ratios(filtered_df)
            st.write("### Tỉ lệ cảm xúc trong các bình luận:")
            st.write("##### Tỉ lệ cảm xúc trong bài viết theo pp Vader:")
            st.write(f"Tỉ lệ cảm xúc Positive: {positive_ratio:.2f}%")
            st.write(f"Tỉ lệ cảm xúc Negative: {negative_ratio:.2f}%")
            st.write(f"Tỉ lệ cảm xúc Unclear: {unclear_ratio:.2f}%")

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
            st.write(f"Số bình luận score điểm từ 50-100: {between_50_and_100}")
            st.write(f"Số bình luận score dưới 50: {above_50}")
            st.write(f"Tác giả bình luận nhiều nhất: {top_author} với {top_author_comment_count} bình luận ")
        else:
            st.error(f"Comment_ID '{input_post_id}' không phải của một bài viết hợp lệ. Vui lòng nhập lại.")
