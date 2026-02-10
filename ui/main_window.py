import qtawesome as qta
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QSize
from services.estoque_service import listar_produtos_com_calculos, inserir_produto, excluir_produto
from ui.vendas_window import VendasPage
from ui.dashboard_window import DashboardPage
from services.estoque_service import (
    listar_produtos_com_calculos, 
    inserir_produto, 
    excluir_produto,
    listar_produtos_filtrados  # <--- ADICIONE ESTA LINHA
)

# CSS BLINDADO - Focado em alto contraste e isolamento de componentes
ESTILO = """
    /* 1. FUNDO GERAL E TEXTO BASE */
    QMainWindow { background-color: #0f172a; }
    QWidget { 
        color: #ffffff; 
        font-family: 'Segoe UI', sans-serif; 
        font-size: 14px; 
    }
    
    /* 2. SIDEBAR - Forçando cores escuras para os botões não sumirem */
    #Sidebar { 
        background-color: #1e293b; 
        border-right: 1px solid #334155; 
    }
    
    #MenuBtn { 
        background-color: #1e293b; 
        text-align: left; 
        padding: 15px; 
        font-weight: bold; 
        color: #94a3b8; 
        border: none;
        border-bottom: 1px solid #334155;
    }
    #MenuBtn:hover { background-color: #334155; color: #ffffff; }
    #MenuBtn:checked { 
        background-color: #0f172a; 
        color: #3b82f6; 
        border-left: 5px solid #3b82f6; 
    }

    /* 3. TABELAS - Resolvendo o fundo branco das suas fotos */
    QTableWidget { 
        background-color: #1e293b; 
        alternate-background-color: #24344d;
        gridline-color: #334155; 
        color: #ffffff;
        border: 1px solid #334155;
    }
    QHeaderView::section { 
        background-color: #334155; 
        color: #3b82f6; 
        padding: 10px; 
        font-weight: bold; 
        border: 1px solid #1e293b;
    }

    /* 4. CAMPOS DE DATA E INPUTS */
    QDateEdit, QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 4px;
        padding: 5px;
        color: #ffffff;
    }

    /* 5. O CALENDÁRIO (FIX DEFINITIVO) */
    /* Forçamos o fundo branco e texto preto APENAS na grade de dias */
    QCalendarWidget QAbstractItemView:enabled {
        background-color: white;
        color: #333333; /* Texto dos dias em cinza escuro */
        selection-background-color: #3b82f6;
        selection-color: white;
    }

    /* Cabeçalho do calendário (Mês e Ano) */
    QCalendarWidget QWidget#qt_calendar_navigationbar {
        background-color: #1e293b;
    }
    
    /* Nome dos dias (Mon, Tue...) */
    QCalendarWidget QWidget {
        alternate-background-color: #edf2f7;
        color: #333333;
    }

    /* Botões de navegação do calendário */
    QCalendarWidget QToolButton {
        color: white;
        background-color: transparent;
        font-weight: bold;
    }
    QDialog { 
        background-color: #0f172a; 
    }

    QDialog QLabel { 
        color: #ffffff; 
    } 
    QDialog QLineEdit, QDialog QSpinBox, QDialog QDoubleSpinBox {
        background-color: #1e293b;
        color: #ffffff;
        border: 1px solid #334155;
    }
"""

class CadastroDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cadastrar Produto")
        self.setStyleSheet(ESTILO)
        layout = QFormLayout(self)
        
        # Campos de texto e categoria
        self.n = QLineEdit() 
        self.c = QComboBox() 
        self.c.addItems(["Construção", "Elétrica", "Hidráulica", "Acabamento", "Ferragens", "Ferramentas", "Pintura", "Outros"])
        self.c.setEditable(True) 
        self.sub = QLineEdit() 
        
        # Campos numéricos
        self.q = QSpinBox(maximum=999)
        self.cu = QDoubleSpinBox(maximum=99999) # Custo
        self.p_lucro = QDoubleSpinBox(maximum=1000) # % Lucro
        self.v = QDoubleSpinBox(maximum=99999) # Venda
        
        # Configurações visuais dos campos de preço
        self.cu.setPrefix("R$ ")
        self.p_lucro.setSuffix(" %")
        self.p_lucro.setValue(100) # Inicia com 100% por padrão
        self.v.setPrefix("R$ ")
        
        # --- AQUI ESTÁ A CONEXÃO QUE DAVA ERRO ---
        self.cu.valueChanged.connect(self.calcular_venda)
        self.p_lucro.valueChanged.connect(self.calcular_venda)
        
        # Adicionando ao layout
        layout.addRow("Nome:", self.n)
        layout.addRow("Categoria:", self.c)
        layout.addRow("Subcategoria:", self.sub)
        layout.addRow("Qtd:", self.q)
        layout.addRow("Custo R$:", self.cu)
        layout.addRow("Lucro %:", self.p_lucro)
        layout.addRow("Venda R$:", self.v)
        
        btn = QPushButton("SALVAR")
        btn.setStyleSheet("background-color: #3b82f6; padding: 10px; font-weight: bold;")
        btn.clicked.connect(self.accept)
        layout.addRow(btn)

    # --- ESTA FUNÇÃO PRECISA ESTAR EXATAMENTE AQUI (INDENTADA) ---
    def calcular_venda(self):
        custo = self.cu.value()
        porcentagem = self.p_lucro.value()
        
        # Cálculo: Custo + (Custo * %)
        venda_final = custo * (1 + (porcentagem / 100))
        
        # Bloqueia sinais para não dar loop infinito ao setar o valor
        self.v.blockSignals(True)
        self.v.setValue(venda_final)
        self.v.blockSignals(False)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NEXUS ERP - Sistema de Gestão")
        self.resize(1150, 750)
        self.setStyleSheet(ESTILO)

        self.central = QWidget()
        self.setCentralWidget(self.central)
        l_geral = QHBoxLayout(self.central)
        l_geral.setContentsMargins(0,0,0,0)
        l_geral.setSpacing(0)

        # SIDEBAR
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(220)
        self.l_side = QVBoxLayout(self.sidebar)
        
        logo = QLabel("NEXUS ERP")
        logo.setStyleSheet("font-size: 20px; font-weight: bold; color: white; padding: 20px;")
        logo.setAlignment(Qt.AlignCenter)
        self.l_side.addWidget(logo)

        self.btn_dash = self.criar_btn(" Dashboard", "fa5s.chart-line", 0)
        self.btn_est = self.criar_btn(" Estoque", "fa5s.boxes", 1)
        self.btn_ven = self.criar_btn(" Vendas", "fa5s.shopping-cart", 2)
        
        self.l_side.addStretch()
        l_geral.addWidget(self.sidebar)

        # CONTEÚDO
        self.stack = QStackedWidget()
        self.pag_dash = DashboardPage()
        self.pag_est = self.setup_est()
        self.pag_ven = VendasPage(self)
        
        self.stack.addWidget(self.pag_dash)
        self.stack.addWidget(self.pag_est)
        self.stack.addWidget(self.pag_ven)
        
        l_geral.addWidget(self.stack)
        self.mudar_pagina(0)

    def criar_btn(self, t, i, idx):
        icon = qta.icon(i, color='#94a3b8')
        btn = QPushButton(icon, t)
        btn.setObjectName("MenuBtn")
        btn.setCheckable(True)
        btn.setIconSize(QSize(20, 20))
        btn.clicked.connect(lambda: self.mudar_pagina(idx))
        self.l_side.addWidget(btn)
        return btn

    def mudar_pagina(self, idx):
        self.stack.setCurrentIndex(idx)
        self.btn_dash.setChecked(idx == 0)
        self.btn_est.setChecked(idx == 1)
        self.btn_ven.setChecked(idx == 2)
        
        # Ajusta cores dos ícones ao clicar
        btns = [self.btn_dash, self.btn_est, self.btn_ven]
        icons = ["fa5s.chart-line", "fa5s.boxes", "fa5s.shopping-cart"]
        for i, b in enumerate(btns):
            cor = '#3b82f6' if i == idx else '#94a3b8'
            b.setIcon(qta.icon(icons[i], color=cor))

        if idx == 0: self.pag_dash.atualizar()
        if idx == 1: self.carregar_est()

    def setup_est(self):
        p = QWidget(); l = QVBoxLayout(p); l.setContentsMargins(30,30,30,30)
        
        # --- CABEÇALHO ---
        topo = QHBoxLayout()
        tit = QLabel("Gerenciamento de Estoque")
        tit.setStyleSheet("font-size: 24px; font-weight: bold;")
        btn_novo = QPushButton(qta.icon("fa5s.plus", color="white"), " NOVO PRODUTO")
        btn_novo.setStyleSheet("background-color: #3b82f6; padding: 10px 20px; font-weight: bold; border-radius: 5px;")
        btn_novo.clicked.connect(self.add_p)
        topo.addWidget(tit); topo.addStretch(); topo.addWidget(btn_novo)
        l.addLayout(topo)

        # --- PAINEL DE FILTROS ---
        filtros_frame = QFrame()
        filtros_frame.setStyleSheet("background-color: #1e293b; border-radius: 8px; padding: 10px; margin-top: 10px;")
        fl_layout = QVBoxLayout(filtros_frame)
        
        # Linha 1: Busca Rápida (Nome/ID) e Categorias
        linha1 = QHBoxLayout()
        self.f_busca = QLineEdit(); self.f_busca.setPlaceholderText("Buscar por Nome ou ID...")
        self.f_cat = QComboBox(); self.f_cat.addItems(["Todos","Construção", "Elétrica", "Hidráulica", "Acabamento", "Ferragens", "Ferramentas", "Pintura", "Outros"])
        self.f_sub = QLineEdit(); self.f_sub.setPlaceholderText("Subcategoria...")
        
        linha1.addWidget(QLabel("Busca:")); linha1.addWidget(self.f_busca, 3)
        linha1.addWidget(QLabel("Categoria:")); linha1.addWidget(self.f_cat, 1)
        linha1.addWidget(QLabel("Subcat:")); linha1.addWidget(self.f_sub, 1)
        fl_layout.addLayout(linha1)

        # Linha 2: Valores e Quantidades
        linha2 = QHBoxLayout()
        self.f_custo = QDoubleSpinBox(); self.f_custo.setPrefix("Custo Mín: R$ "); self.f_custo.setMaximum(99999)
        self.f_venda = QDoubleSpinBox(); self.f_venda.setPrefix("Venda Mín: R$ "); self.f_venda.setMaximum(99999)
        self.f_qtd = QSpinBox(); self.f_qtd.setPrefix("Qtd Mín: "); self.f_qtd.setMaximum(9999)
        
        btn_filtrar = QPushButton(qta.icon("fa5s.search", color="white"), " FILTRAR")
        btn_filtrar.setStyleSheet("background-color: #334155; padding: 8px; font-weight: bold; border: 1px solid #3b82f6;")
        btn_filtrar.clicked.connect(self.carregar_est) # Agora ele chama a busca com filtros
        
        btn_limpar = QPushButton("LIMPAR")
        btn_limpar.clicked.connect(self.limpar_filtros)

        linha2.addWidget(self.f_custo); linha2.addWidget(self.f_venda); linha2.addWidget(self.f_qtd)
        linha2.addWidget(btn_filtrar); linha2.addWidget(btn_limpar)
        fl_layout.addLayout(linha2)
        
        l.addWidget(filtros_frame)

        # --- TABELA ---
        self.tab = QTableWidget(0, 8)
        self.tab.setHorizontalHeaderLabels(["ID", "PRODUTO", "CATEGORIA", "SUBCAT", "QTD", "CUSTO", "VENDA", "TOTAL"])
        self.tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        l.addWidget(self.tab)
        
        return p

    def carregar_est(self):
        # Captura os valores da interface
        id_p = None
        nome_p = self.f_busca.text()
        
        categoria_selecionada = self.f_cat.currentText()
        if categoria_selecionada == "Todos":
            categoria_selecionada = None


        # Se o que foi digitado for apenas números, tratamos como ID também
        if nome_p.isdigit():
            id_p = int(nome_p)
            nome_p = None
            
        # Chama o serviço com os filtros
        items = listar_produtos_filtrados(
            id_p=id_p,
            nome=nome_p if nome_p else None,
            cat=categoria_selecionada, # <--- Usa a variável tratada
            sub=self.f_sub.text() if self.f_sub.text() else None,
            custo_min=self.f_custo.value() if self.f_custo.value() > 0 else None,
            venda_min=self.f_venda.value() if self.f_venda.value() > 0 else None,
            qtd_min=self.f_qtd.value() if self.f_qtd.value() > 0 else None
        )
        

        self.tab.setRowCount(0)
        for r, i in enumerate(items):
            self.tab.insertRow(r)
            d = i['dados']
            self.tab.setItem(r, 0, QTableWidgetItem(str(d[0])))
            self.tab.setItem(r, 1, QTableWidgetItem(str(d[1])))
            self.tab.setItem(r, 2, QTableWidgetItem(str(d[2])))
            self.tab.setItem(r, 3, QTableWidgetItem(str(d[3])))
            self.tab.setItem(r, 4, QTableWidgetItem(str(d[4])))
            self.tab.setItem(r, 5, QTableWidgetItem(f"R$ {d[5]:.2f}"))
            self.tab.setItem(r, 6, QTableWidgetItem(f"R$ {d[6]:.2f}"))
            self.tab.setItem(r, 7, QTableWidgetItem(f"R$ {i['total_item']:.2f}"))

        self.tab.setRowCount(0)
        for r, i in enumerate(items):
            self.tab.insertRow(r)
            d = i['dados']
            self.tab.setItem(r, 0, QTableWidgetItem(str(d[0])))
            self.tab.setItem(r, 1, QTableWidgetItem(str(d[1])))
            self.tab.setItem(r, 2, QTableWidgetItem(str(d[2])))
            self.tab.setItem(r, 3, QTableWidgetItem(str(d[3])))
            self.tab.setItem(r, 4, QTableWidgetItem(str(d[4])))
            self.tab.setItem(r, 5, QTableWidgetItem(f"R$ {d[5]:.2f}"))
            self.tab.setItem(r, 6, QTableWidgetItem(f"R$ {d[6]:.2f}"))
            self.tab.setItem(r, 7, QTableWidgetItem(f"R$ {i['total_item']:.2f}"))

    def add_p(self):
        d = CadastroDialog()
        if d.exec():
            # Captura os dados do diálogo corretamente
            nome = d.n.text()
            categoria = d.c.currentText()
            subcategoria = d.sub.text()
            quantidade = d.q.value()
            custo = d.cu.value()
            venda = d.v.value() # Este valor já vem calculado do Dialog

            # Chama o serviço passando os 6 parâmetros necessários
            inserir_produto(nome, categoria, subcategoria, quantidade, custo, venda)
            
            # Atualiza as telas
            self.carregar_est()
            self.pag_ven.atualizar()

            if nome: # Validação simples
                inserir_produto(nome, categoria, subcategoria, quantidade, custo, venda)
                self.carregar_est()
                self.pag_ven.atualizar()

    def excluir_p(self):
        # 1. Pega a linha selecionada
        row = self.tab.currentRow()
        
        # 2. Verifica se realmente há uma linha selecionada
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione um produto na tabela para excluir.")
            return

        # 3. Pega o ID e o Nome (opcional, para deixar a mensagem mais clara)
        try:
            id_p = self.tab.item(row, 0).text()
            nome_p = self.tab.item(row, 1).text()
            
            # 4. Pergunta com mais clareza
            pergunta = QMessageBox.question(
                self, 
                "Confirmar Exclusão", 
                f"Tem certeza que deseja excluir o produto:\n\nID: {id_p}\nNome: {nome_p}?",
                QMessageBox.Yes | QMessageBox.No
            )

            if pergunta == QMessageBox.Yes:
                # 5. Chama o serviço de exclusão
                excluir_produto(int(id_p))
                
                # 6. Atualiza a interface
                self.carregar_est()
                # Se tiver a página de vendas aberta, atualiza ela também
                if hasattr(self, 'pag_ven'):
                    self.pag_ven.atualizar()
                
                QMessageBox.information(self, "Sucesso", "Produto excluído com sucesso!")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível excluir o produto: {str(e)}")
            

    def limpar_filtros(self):
        self.f_busca.clear()
        self.f_cat.setCurrentIndex(0)
        self.f_sub.clear()
        self.f_custo.setValue(0)
        self.f_venda.setValue(0)
        self.f_qtd.setValue(0)
        self.carregar_est()


    def calcular_venda(self):
        """Calcula o valor de venda baseado no custo + lucro %"""
        custo = self.cu.value()
        porcentagem = self.p_lucro.value()
        
        # Fórmula: Venda = Custo + (Custo * Porcentagem / 100)
        venda = custo * (1 + (porcentagem / 100))
        
        # Bloqueia sinais temporariamente para não criar loop infinito
        self.v.blockSignals(True)
        self.v.setValue(venda)
        self.v.blockSignals(False)