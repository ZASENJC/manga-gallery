import os, shutil
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
# ================= 配置区 =================
app.secret_key = 'CHANGE_THIS_TO_RANDOM_STRING'  # 👈 请修改随机密钥
ADMIN_PASSWORD = 'admin123'                      # 👈 请修改后台密码
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLOUD_ROOT = os.path.join(BASE_DIR, 'storage')
PUBLIC_FOLDER = os.path.join(CLOUD_ROOT, 'public')
HIDDEN_FOLDER = os.path.join(CLOUD_ROOT, 'hidden')
THUMB_FOLDER = os.path.join(BASE_DIR, 'local_cache', 'thumbnails')

os.makedirs(THUMB_FOLDER, exist_ok=True)
for d in [PUBLIC_FOLDER, HIDDEN_FOLDER]:
    if not os.path.exists(d):
        try: os.makedirs(d, exist_ok=True)
        except: pass

# 登录验证装饰器
def login_required(f):
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'): return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else: error = '密码错误'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    def get_files(folder):
        if not os.path.exists(folder): return []
        try:
            files = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')) and not f.startswith('.')]
            files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)), reverse=True)
            return files
        except: return []
    return render_template('admin.html', public_images=get_files(PUBLIC_FOLDER), hidden_images=get_files(HIDDEN_FOLDER))

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    # 支持批量上传
    for file in request.files.getlist('files'):
        if file and file.filename:
            try: file.save(os.path.join(PUBLIC_FOLDER, secure_filename(file.filename)))
            except: pass
    return redirect(url_for('dashboard'))

@app.route('/toggle/<status>/<filename>')
@login_required
def toggle(status, filename):
    # 图片在 Public 和 Hidden 之间移动
    src_dir = PUBLIC_FOLDER if status == 'public' else HIDDEN_FOLDER
    dst_dir = HIDDEN_FOLDER if status == 'public' else PUBLIC_FOLDER
    src, dst = os.path.join(src_dir, filename), os.path.join(dst_dir, filename)
    if os.path.exists(src):
        try: shutil.move(src, dst)
        except: pass
    return redirect(url_for('dashboard'))

@app.route('/delete/<status>/<filename>')
@login_required
def delete(status, filename):
    # 同时删除原图和缩略图缓存
    d = PUBLIC_FOLDER if status == 'public' else HIDDEN_FOLDER
    p, t = os.path.join(d, filename), os.path.join(THUMB_FOLDER, filename)
    if os.path.exists(p): os.remove(p)
    if os.path.exists(t): os.remove(t)
    return redirect(url_for('dashboard'))

@app.route('/thumb/<status>/<filename>')
@login_required
def serve_thumb(status, filename):
    # 后台缩略图逻辑：若本地无缓存，临时生成
    folder = PUBLIC_FOLDER if status == 'public' else HIDDEN_FOLDER
    thumb_path = os.path.join(THUMB_FOLDER, filename)
    if os.path.exists(thumb_path): return send_from_directory(THUMB_FOLDER, filename)
    return send_from_directory(folder, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
