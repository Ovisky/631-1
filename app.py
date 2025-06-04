from flask import Flask, render_template, request, redirect, url_for
import json
from datetime import datetime
import markdown
import os

app = Flask(__name__)

# ======== 博客数据处理 =========

def load_posts():
    with open('data/posts.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_post_by_id(post_id):
    posts = load_posts()
    for post in posts:
        if post['id'] == post_id:
            return post
    return None

def save_post(new_post):
    posts = load_posts()
    new_post['id'] = max([p['id'] for p in posts] or [0]) + 1
    new_post['date'] = datetime.now().strftime('%Y-%m-%d')
    posts.append(new_post)
    with open('data/posts.json', 'w', encoding='utf-8') as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)
# ======== 删除数据 =========
def delete_post(post_id):
    posts = load_posts()
    posts = [p for p in posts if p['id'] != post_id]
    with open('data/posts.json', 'w', encoding='utf-8') as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)

    # 同时删除关联评论
    comments = load_comments()
    comments.pop(str(post_id), None)
    with open('data/comments.json', 'w', encoding='utf-8') as f:
        json.dump(comments, f, indent=2, ensure_ascii=False)
#添加删除评论
def delete_comment(post_id, index):
    comments = load_comments()
    post_comments = comments.get(str(post_id), [])
    if 0 <= index < len(post_comments):
        del post_comments[index]
        comments[str(post_id)] = post_comments
        with open('data/comments.json', 'w', encoding='utf-8') as f:
            json.dump(comments, f, indent=2, ensure_ascii=False)


# ======== 评论数据处理 =========

def load_comments():
    with open('data/comments.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_comment(post_id, name, comment):
    comments = load_comments()
    post_id = str(post_id)
    if post_id not in comments:
        comments[post_id] = []
    comments[post_id].append({
        'name': name,
        'comment': comment,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M')
    })
    with open('data/comments.json', 'w', encoding='utf-8') as f:
        json.dump(comments, f, indent=2, ensure_ascii=False)

@app.route('/delete_post/<int:post_id>')
def delete_post_route(post_id):
    delete_post(post_id)
    return redirect(url_for('index'))

@app.route('/delete_comment/<int:post_id>/<int:index>')
def delete_comment_route(post_id, index):
    delete_comment(post_id, index)
    return redirect(url_for('post', post_id=post_id))

# ======== 路由设置 =========

@app.route('/')
def index():
    posts = load_posts()
    return render_template('index.html', posts=posts)

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    post = get_post_by_id(post_id)
    if not post:
        return "博客未找到", 404

    if request.method == 'POST':
        name = request.form.get('name')
        comment = request.form.get('comment')
        if name and comment:
            save_comment(post_id, name, comment)
            return redirect(url_for('post', post_id=post_id))

    post['html_content'] = markdown.markdown(
        post['content'], extensions=['fenced_code', 'tables']
    )
    comments = load_comments().get(str(post_id), [])
    return render_template('post.html', post=post, comments=comments)

@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        if title and content:
            save_post({'title': title, 'content': content})
            return redirect(url_for('index'))
    return render_template('write.html')




# ======== 启动入口 =========

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render 会设置 PORT 环境变量
    app.run(debug=False, host='0.0.0.0', port=port)
