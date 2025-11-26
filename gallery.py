import os
from flask import Flask, render_template, send_from_directory
from PIL import Image

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 路径配置
CLOUD_ROOT = os.path.join(BASE_DIR, 'storage')
UPLOAD_FOLDER = os.path.join(CLOUD_ROOT, 'public')
THUMB_FOLDER = os.path.join(BASE_DIR, 'local_cache', 'thumbnails')

# 自动创建必要目录
os.makedirs(THUMB_FOLDER, exist_ok=True)

def generate_thumbnail(filename):
    """生成并缓存缩略图，避免重复处理"""
    thumb_path = os.path.join(THUMB_FOLDER, filename)
    original_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if os.path.exists(thumb_path): return
    if not os.path.exists(original_path): return
    
    try:
        with Image.open(original_path) as img:
            if img.mode in ("RGBA", "P"): img = img.convert("RGB")
            # 缩略图尺寸限制为 500px，平衡清晰度与速度
            img.thumbnail((500, 500))
            img.save(thumb_path, "JPEG", quality=85)
    except Exception as e:
        print(f"Thumbnail error: {e}")

@app.route('/')
def index():
    if not os.path.exists(UPLOAD_FOLDER): 
        return "Error: Storage not mounted.", 500
    # 过滤非图片文件并按修改时间倒序排列
    images = [f for f in os.listdir(UPLOAD_FOLDER) 
              if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')) and not f.startswith('.')]
    images.sort(key=lambda x: os.path.getmtime(os.path.join(UPLOAD_FOLDER, x)), reverse=True)
    return render_template('gallery.html', images=images)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供原图访问"""
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/thumb/<filename>')
def thumbnail_file(filename):
    """提供缩略图访问，不存在则自动生成"""
    generate_thumbnail(filename)
    if os.path.exists(os.path.join(THUMB_FOLDER, filename)):
        return send_from_directory(THUMB_FOLDER, filename)
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
