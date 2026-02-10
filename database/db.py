# database/db.py
import sqlite3
import os

def get_connection():
    # Isso garante que o banco 'sistema.db' fique na raiz do projeto,
    # não importa de onde você execute o script.
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "..", "sistema.db")
    return sqlite3.connect(db_path)



def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    # Habilita suporte a chaves estrangeiras
    cursor.execute("PRAGMA foreign_keys = ON;")

    
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT,
            subcategoria TEXT,
            tag TEXT,
            quantidade INTEGER DEFAULT 0,
            preco_custo REAL DEFAULT 0.0,
            preco_venda REAL DEFAULT 0.0
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER,
            quantidade INTEGER,
            valor_total REAL,
            desconto REAL,
            data_venda DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(produto_id) REFERENCES produtos(id)
        )
    """)
    conn.commit()
    conn.close()