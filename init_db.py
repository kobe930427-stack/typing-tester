import sqlite3

def init_db():
    conn = sqlite3.connect('typing_tester.db')
    cursor = conn.cursor()
    
    # 刪除舊表以重新結構化
    cursor.execute('DROP TABLE IF EXISTS passages')
    cursor.execute('DROP TABLE IF EXISTS history')
    
    # 1. 建立文章資料表（新增 difficulty 欄位）
    cursor.execute('''
        CREATE TABLE passages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            difficulty TEXT NOT NULL
        )
    ''')
    
    # 2. 建立歷史紀錄資料表
    cursor.execute('''
        CREATE TABLE history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wpm INTEGER NOT NULL,
            accuracy REAL NOT NULL,
            difficulty TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 3. 匯入不同難易度的預設文章
    default_passages = [
        # 簡單：句子短、單字生活化
        ("The quick brown fox jumps over the lazy dog.", "easy"),
        ("Practice makes perfect. Keep typing every day.", "easy"),
        ("Life is short, you need Python.", "easy"),
        
        # 中等：句子較長、包含標點符號
        ("Success is not final, failure is not fatal: it is the courage to continue that counts.", "medium"),
        ("To be or not to be, that is the question. Whether 'tis nobler in the mind to suffer.", "medium"),
        
        # 困難：程式碼偏向、包含特殊符號與複雜排版
        ("const express = require('express'); const app = express(); app.listen(3000);", "hard"),
        ("def my_func(x, y): return [i for i in range(x) if i % y == 0]", "hard")
    ]
    
    for content, difficulty in default_passages:
        cursor.execute("INSERT INTO passages (content, difficulty) VALUES (?, ?)", (content, difficulty))
            
    conn.commit()
    conn.close()
    print("⚡ 資料庫已成功升級！難易度文章已匯入。")

if __name__ == '__main__':
    init_db()
