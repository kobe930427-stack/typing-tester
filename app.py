
from flask import Flask, render_template, jsonify, request
import sqlite3

app = Flask(__name__)
DATABASE = 'typing_tester.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# 資料庫自動升級機制：確保 history 表有 username 欄位
def upgrade_db():
    conn = get_db_connection()
    try:
        # 測試看看能不能讀取 username，如果不行就會觸發 exception
        conn.execute('SELECT username FROM history LIMIT 1')
    except sqlite3.OperationalError:
        # 欄位不存在，自動新增 `username` 欄位，預設值為 'Gamer'
        conn.execute('ALTER TABLE history ADD COLUMN username TEXT DEFAULT "Gamer"')
        conn.commit()
        print("⚡ 資料庫已成功升級：已加入 username 欄位！")
    finally:
        conn.close()

# 啟動時自動檢查並升級資料庫
upgrade_db()

@app.route('/')
def index():
    return render_template('index.html')

# API 1：根據難易度取得隨機文章
@app.route('/api/get-passage', methods=['GET'])
def get_passage():
    difficulty = request.args.get('difficulty', 'easy')
    conn = get_db_connection()
    passage = conn.execute(
        'SELECT content FROM passages WHERE difficulty = ? ORDER BY RANDOM() LIMIT 1', 
        (difficulty,)
    ).fetchone()
    conn.close()
    return jsonify({'content': passage['content'] if passage else "No passage found."})

# API 2：儲存測試結果（未完成不儲存機制）
@app.route('/api/save-result', methods=['POST'])
def save_result():
    data = request.json
    wpm = data.get('wpm')
    accuracy = data.get('accuracy')
    difficulty = data.get('difficulty', 'easy')
    username = data.get('username', '匿名玩家')
    is_completed = data.get('is_completed', False) # 接收前端傳來的完成狀態
    
    # 🎯 核心防線：如果玩家沒有打完整篇文章，直接拒絕寫入資料庫，不列入排行！
    if not is_completed:
        return jsonify({'status': 'ignored', 'message': '未完成文章，不計入排行榜'})
    
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO history (wpm, accuracy, difficulty, username) VALUES (?, ?, ?, ?)', 
        (wpm, accuracy, difficulty, username)
    )
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

# API 3：取得神人排行榜（依 WPM 排序前 10 名）
@app.route('/api/get-leaderboard', methods=['GET'])
def get_leaderboard():
    conn = get_db_connection()
    records = conn.execute('''
        SELECT username, wpm, accuracy, difficulty, datetime(created_at, 'localtime') as ts 
        FROM history 
        ORDER BY wpm DESC, accuracy DESC 
        LIMIT 10
    ''').fetchall()
    conn.close()
    return jsonify([{
        'username': r['username'],
        'wpm': r['wpm'], 
        'accuracy': r['accuracy'], 
        'difficulty': r['difficulty'].upper(), 
        'date': r['ts']
    } for r in records])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
