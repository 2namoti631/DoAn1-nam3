import praw
import csv
# Lấy dữ liệu theo subreddit 
# Hàm kết nối và lấy dữ liệu từ Reddit
def collect_sub_data(subreddit_name, output_file='reddit_data.csv', limit=1000):
  # Thiết lập kết nối đến Reddit
    reddit = praw.Reddit(
        client_id='wqJhXCtoWPylKs0ROJfc8Q',
        client_secret='cGi2d1HDpkkfPSuP1Vw9hZgUvwjK1Q',
        user_agent='graph1/1.0 by nikohn16'
    )

    # Lấy subreddit
    subreddit = reddit.subreddit(subreddit_name)

    # Hàm để xử lý và loại bỏ tiền tố trong ID
    def clean_id(full_id):
        return full_id.split('_')[1] if '_' in full_id else full_id

    # Tạo và mở file CSV để ghi dữ liệu
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Ghi header cho file CSV
        writer.writerow(['Type', 'Comment_ID', 'Parent_ID', 'Author', 'Content', 'Score', 'Created_UTC'])

        # Hàm đệ quy để lấy dữ liệu từ các bình luận ở mọi lớp
        def write_comment_data(comment):
            # Ghi dữ liệu bình luận vào file CSV
            writer.writerow([
                'Comment',
                clean_id(comment.id),
                clean_id(comment.parent_id),  # Xử lý để loại bỏ tiền tố
                comment.author,
                comment.body,
                comment.score,
                comment.created_utc
            ])
            # Lặp qua từng bình luận con của bình luận này
            for reply in comment.replies:
                write_comment_data(reply)  # Gọi đệ quy cho từng bình luận con

        # Lặp qua các bài viết (submission) trong subreddit
        for submission in subreddit.hot(limit=limit):  # Thay đổi limit nếu cần
            # Ghi thông tin bài viết vào file CSV
            writer.writerow([
                'Post',
                clean_id(submission.id),
                None,  # Bài viết không có bình luận cha
                submission.author,
                submission.selftext,
                submission.score,
                submission.created_utc
            ])

            # Lấy và ghi dữ liệu các bình luận
            submission.comments.replace_more(limit=0)  # Tải tất cả bình luận
            for comment in submission.comments:
                write_comment_data(comment)  # Gọi hàm đệ quy cho từng bình luận

    print(f"Dữ liệu đã được lưu vào '{output_file}'")

