from flask import Flask, request, jsonify, send_file, render_template
import yt_dlp
import os

app = Flask(__name__)

# 設定下載的檔案儲存路徑
DOWNLOAD_PATH = './tmp/downloads'

# 如果沒有該資料夾則創建它
if not os.path.exists(DOWNLOAD_PATH):
    os.makedirs(DOWNLOAD_PATH)

@app.route('/', methods=['GET', 'POST'])
def download_video():
    if request.method == 'POST':
        data = request.get_json()
        url = data.get('url')
        download_type = data.get('type')

        if not url or not download_type:
            return jsonify({'error': 'Missing URL or download type'}), 400

        try:
            # 處理 MP3 下載
            if download_type == 'mp3':
                video_info = yt_dlp.YoutubeDL().extract_info(url, download=False)
                output_file = f"{DOWNLOAD_PATH}{video_info['title']}.mp3"
                ydl_opts = {
                    'format':'bestaudio/best',
                    'keepvideo':False,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': output_file,
                }
            # 處理 MP4 下載
            elif download_type == 'mp4':
                output_file = f"{DOWNLOAD_PATH}%(title)s.%(ext)s"
                ydl_opts = {
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio',
                    'outtmpl': output_file,
                    'quiet': True,
                }
            else:
                return jsonify({'error': 'Invalid download type'}), 400

            # 使用 yt-dlp 下載影片或音訊
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # 回傳下載完成的文件，供用戶下載
            return send_file(output_file, as_attachment=True)

        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return render_template('index.html')
if __name__ == '__main__':
    app.run(debug=True)
