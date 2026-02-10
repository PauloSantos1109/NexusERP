from database.db import get_connection
from services.estoque_service import listar_produtos_com_calculos
from datetime import datetime
from database.db import get_connection

def realizar_venda(id_produto, qtd_venda, desconto=0.0):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT nome, quantidade, preco_venda FROM produtos WHERE id = ?", (id_produto,))
        p = cursor.fetchone()
        
        if not p or p[1] < qtd_venda:
            return False, "Estoque insuficiente!"

        total = (qtd_venda * p[2]) - desconto
        
        # O SQLITE faz o commit de tudo junto se usarmos o context manager ou commit manual no fim
        cursor.execute("UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?", (qtd_venda, id_produto))
        cursor.execute("INSERT INTO vendas (produto_id, quantidade, valor_total, desconto) VALUES (?,?,?,?)", 
                       (id_produto, qtd_venda, total, desconto))
        
        conn.commit()
        return True, "Venda concluída!"
    except Exception as e:
        conn.rollback() # Cancela tudo se der erro
        return False, f"Erro: {str(e)}"
    finally:
        conn.close()

def atualizar(self):
    # Atualiza o combo de produtos
    self.cb.clear()
    for p in listar_produtos_com_calculos():
        dados = p['dados']
        # dados[0] = ID, dados[1] = Nome, dados[2] = Cat, dados[3] = Subcat...
        nome_display = f"{dados[1]} ({dados[3]})" # Exibe: Nome (Subcategoria)
        self.cb.addItem(nome_display, dados[0])

def obter_vendas_detalhadas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT v.data_venda, p.nome, p.categoria, v.quantidade, v.valor_total, v.desconto
        FROM vendas v JOIN produtos p ON v.produto_id = p.id ORDER BY v.data_venda DESC
    """)
    res = cursor.fetchall()
    conn.close()
    return res

def obter_metricas_bi(d1, d2, categoria=None, produto=None, qtd_min=None, valor_min=None, lucro_min=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Base da query com os cálculos de métricas
    q = """SELECT SUM(v.valor_total), SUM(v.desconto), SUM(v.quantidade), 
           SUM(v.valor_total - (p.preco_custo * v.quantidade)) 
           FROM vendas v JOIN produtos p ON v.produto_id = p.id 
           WHERE v.data_venda BETWEEN ? AND ?"""
    
    parametros = [f"{d1} 00:00:00", f"{d2} 23:59:59"]

    # Filtros Dinâmicos
    if categoria and categoria != "Todas":
        q += " AND p.categoria LIKE ?"
        parametros.append(f"%{categoria}%")
    
    if produto:
        q += " AND p.nome LIKE ?"
        parametros.append(f"%{produto}%")
        
    if qtd_min:
        q += " AND v.quantidade >= ?"
        parametros.append(qtd_min)
        
    if valor_min:
        q += " AND v.valor_total >= ?"
        parametros.append(valor_min)

    # Filtro de Lucro (calculado na hora)
    if lucro_min:
        q += " AND (v.valor_total - (p.preco_custo * v.quantidade)) >= ?"
        parametros.append(lucro_min)

    cursor.execute(q, parametros)
    res = cursor.fetchone()
    conn.close()
    return res

def excluir_venda(id_venda):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vendas WHERE id = ?", (id_venda,))
    conn.commit()
    conn.close()

def obter_vendas_detalhadas():
    conn = get_connection()
    cursor = conn.cursor()
    # Adicionamos v.id no início para a tabela conseguir excluir
    cursor.execute("""
        SELECT v.id, v.data_venda, p.nome, v.quantidade, v.valor_total 
        FROM vendas v JOIN produtos p ON v.produto_id = p.id 
        ORDER BY v.data_venda DESC
    """)
    res = cursor.fetchall()
    conn.close()
    return res

def listar_vendas_por_data(data_filtro=None):
    """
    Busca vendas no banco. Se data_filtro for None, busca as de hoje.
    Formato esperado da data: 'YYYY-MM-DD'
    """
    if data_filtro is None:
        data_filtro = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Buscamos as vendas filtrando pela coluna data_venda
    # Usamos date() do SQLite para comparar apenas o dia, ignorando a hora
    query = """
        SELECT v.id, p.nome, v.quantidade, v.valor_total, v.data_venda
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        WHERE date(v.data_venda) = ?
        ORDER BY v.data_venda DESC
    """
    cursor.execute(query, (data_filtro,))
    vendas = cursor.fetchall()
    conn.close()
    return vendas