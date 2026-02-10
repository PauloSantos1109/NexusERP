import sqlite3
import os

def forcar_criacao():
    db_name = "sistema.db"
    
    # Se o arquivo já existir, ele vai apenas garantir as tabelas
    print(f"Tentando criar/conectar ao banco: {os.path.abspath(db_name)}")
    
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # Criando a tabela de produtos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                categoria TEXT,
                subcategoria TEXT,
                quantidade INTEGER DEFAULT 0,
                preco_custo REAL DEFAULT 0.0,
                preco_venda REAL DEFAULT 0.0
            )
        """)
        
        # Criando a tabela de vendas
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
        print("✅ Banco de dados e tabelas criados com SUCESSO!")
        
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")

if __name__ == "__main__":
    forcar_criacao()