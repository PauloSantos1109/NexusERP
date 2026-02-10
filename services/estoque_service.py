from database.db import get_connection

def listar_produtos_com_calculos():
    conn = get_connection()
    cursor = conn.cursor()
    # Note que agora o SELECT tem 7 itens:
    cursor.execute("SELECT id, nome, categoria, subcategoria, quantidade, preco_custo, preco_venda FROM produtos")
    produtos = cursor.fetchall()
    conn.close()
    
    processados = []
    for p in produtos:
        # CORREÇÃO: Adicionamos 'sub' na lista de variáveis (totalizando 7)
        id_p, nome, cat, sub, qtd, custo, venda = p 
        
        processados.append({
            "dados": p,
            "total_item": qtd * venda
        })
    return processados



def excluir_produto(id_produto):
    """Remove um produto pelo ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = ?", (id_produto,))
    conn.commit()
    conn.close()


def listar_produtos_filtrados(id_p=None, nome=None, cat=None, sub=None, 
                             custo_min=None, venda_min=None, qtd_min=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT id, nome, categoria, subcategoria, quantidade, preco_custo, preco_venda FROM produtos WHERE 1=1"
    params = []

    if id_p:
        query += " AND id = ?"; params.append(id_p)
    if nome:
        query += " AND nome LIKE ?"; params.append(f"%{nome}%")
    if cat and cat != "Todas":
        query += " AND categoria = ?"; params.append(cat)
    if sub:
        query += " AND subcategoria LIKE ?"; params.append(f"%{sub}%")
    if custo_min:
        query += " AND preco_custo >= ?"; params.append(custo_min)
    if venda_min:
        query += " AND preco_venda >= ?"; params.append(venda_min)
    if qtd_min:
        query += " AND quantidade >= ?"; params.append(qtd_min)

    cursor.execute(query, params)
    produtos = cursor.fetchall()
    conn.close()
    
    return [{"dados": p, "total_item": p[4] * p[6]} for p in produtos]

def inserir_produto(nome, cat, sub, qtd, custo, venda):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO produtos (nome, categoria, subcategoria, quantidade, preco_custo, preco_venda)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nome, cat, sub, qtd, custo, venda))
    conn.commit()
    conn.close()