from flask import Flask, send_from_directory, abort, render_template_string
import os

app = Flask(__name__)

# PDF 기본 디렉토리
PDF_ROOT_DIR = os.path.join(app.root_path, "static", "pdf_storage")

# HTML 템플릿
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>PDF Viewer</title>
</head>
<body>
    <h1>📁 PDF Categories</h1>
    <ul>
        {% for category in categories %}
            <li><a href="/browse/{{ category }}">{{ category }}</a></li>
        {% endfor %}
    </ul>
</body>
</html>
"""

CATEGORY_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ category }} - PDF List</title>
</head>
<body>
    <h1>{{ category }} 문서 목록</h1>
    <ul>
        {% for file in files %}
            <li><a href="/pdf/{{ category }}/{{ file }}" target="_blank">{{ file }}</a></li>
        {% endfor %}
    </ul>
    <a href="/">← 카테고리로 돌아가기</a>
</body>
</html>
"""

@app.route('/')
def index():
    if not os.path.exists(PDF_ROOT_DIR):
        return "PDF 디렉터리가 존재하지 않습니다."
    categories = [d for d in os.listdir(PDF_ROOT_DIR) if os.path.isdir(os.path.join(PDF_ROOT_DIR, d))]
    return render_template_string(TEMPLATE, categories=categories)

@app.route('/browse/<category>')
def browse_category(category):
    category_path = os.path.join(PDF_ROOT_DIR, category)
    if not os.path.exists(category_path):
        abort(404)
    files = [f for f in os.listdir(category_path) if f.endswith(".pdf")]
    return render_template_string(CATEGORY_TEMPLATE, category=category, files=files)

@app.route('/pdf/<category>/<filename>')
def serve_pdf(category, filename):
    category_path = os.path.join(PDF_ROOT_DIR, category)
    file_path = os.path.join(category_path, filename)
    if os.path.exists(file_path):
        return send_from_directory(category_path, filename)
    else:
        abort(404)

if __name__ == '__main__':
    app.run(port=8000, debug=True)
