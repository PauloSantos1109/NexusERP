import csv
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QDate
import qtawesome as qta
from services.vendas_service import obter_metricas_bi, obter_vendas_detalhadas

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(30, 30, 30, 30)
        self.layout_principal.setSpacing(20)

        # --- SEÇÃO DE FILTROS ---
        self.setup_filtros()

        # --- SEÇÃO DE CARDS (MÉTRICAS) ---
        self.setup_cards()
        
        self.layout_principal.addStretch()
        
        # Preenche os dados ao abrir a página
        self.atualizar()

    def setup_filtros(self):
        layout_filtros_master = QVBoxLayout()
        
        # Linha 1: Datas e Seletor de Produto
        linha1 = QHBoxLayout()
        self.dt_inicio = QDateEdit(QDate.currentDate().addDays(-30))
        self.dt_inicio.setCalendarPopup(True)
        self.dt_fim = QDateEdit(QDate.currentDate())
        self.dt_fim.setCalendarPopup(True)
        
        self.cb_produto = QComboBox()
        self.cb_produto.setEditable(True) 
        self.cb_produto.setMinimumWidth(200)
        
        linha1.addWidget(QLabel("De:")); linha1.addWidget(self.dt_inicio)
        linha1.addWidget(QLabel("Até:")); linha1.addWidget(self.dt_fim)
        linha1.addWidget(QLabel("Produto:")); linha1.addWidget(self.cb_produto)
        
        # Linha 2: Categoria, Qtd, Valor e Lucro
        linha2 = QHBoxLayout()
        self.cb_cat = QComboBox()
        self.cb_cat.setEditable(True)
        self.cb_cat.setMinimumWidth(150)
        
        self.num_qtd = QSpinBox(); self.num_qtd.setPrefix("Qtd Min: ")
        self.num_valor = QDoubleSpinBox(); self.num_valor.setPrefix("Valor Min: R$ "); self.num_valor.setMaximum(99999)
        self.num_lucro = QDoubleSpinBox(); self.num_lucro.setPrefix("Lucro Min: R$ "); self.num_lucro.setMaximum(99999)
        
        linha2.addWidget(QLabel("Categoria:")); linha2.addWidget(self.cb_cat)
        linha2.addWidget(self.num_qtd)
        linha2.addWidget(self.num_valor)
        linha2.addWidget(self.num_lucro)

        # Linha 3: Botões (Filtro e Exportação)
        linha_btns = QHBoxLayout()
        btn_filtrar = QPushButton(qta.icon("fa5s.filter", color="white"), " APLICAR FILTROS")
        btn_filtrar.setStyleSheet("background-color: #3b82f6; padding: 10px 20px; font-weight: bold;")
        btn_filtrar.clicked.connect(self.atualizar)
        
        self.btn_exportar = QPushButton(qta.icon("fa5s.file-csv", color="white"), " EXPORTAR CSV")
        self.btn_exportar.setStyleSheet("background-color: #10b981; padding: 10px 20px; font-weight: bold;")
        self.btn_exportar.clicked.connect(self.exportar_dados)
        
        linha_btns.addWidget(btn_filtrar)
        linha_btns.addWidget(self.btn_exportar)
        linha_btns.addStretch()

        layout_filtros_master.addLayout(linha1)
        layout_filtros_master.addLayout(linha2)
        layout_filtros_master.addLayout(linha_btns)
        
        self.layout_principal.addLayout(layout_filtros_master)
        
        # Preenche as listas de produtos e categorias
        self.carregar_filtros_combo()

    def setup_cards(self):
        self.cards_layout = QHBoxLayout()
        
        self.card_faturamento = self.criar_card("FATURAMENTO TOTAL", "R$ 0,00", "#10b981")
        self.card_vendas = self.criar_card("TOTAL VENDAS (QTD)", "0", "#3b82f6")
        self.card_lucro = self.criar_card("LUCRO ESTIMADO", "R$ 0,00", "#8b5cf6")
        self.card_desconto = self.criar_card("TOTAL DESCONTOS", "R$ 0,00", "#f59e0b")

        self.cards_layout.addWidget(self.card_faturamento)
        self.cards_layout.addWidget(self.card_vendas)
        self.cards_layout.addWidget(self.card_lucro)
        self.cards_layout.addWidget(self.card_desconto)
        
        self.layout_principal.addLayout(self.cards_layout)

    def criar_card(self, titulo, valor, cor_borda):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #1e293b;
                border-radius: 10px;
                border-left: 5px solid {cor_borda};
                padding: 15px;
            }}
        """)
        layout = QVBoxLayout(card)
        
        lbl_tit = QLabel(titulo)
        lbl_tit.setStyleSheet("font-size: 11px; color: #94a3b8; font-weight: bold;")
        
        lbl_val = QLabel(valor)
        lbl_val.setStyleSheet("font-size: 22px; color: #ffffff; font-weight: 900;")
        lbl_val.setObjectName("valor") 
        
        layout.addWidget(lbl_tit)
        layout.addWidget(lbl_val)
        return card

    def atualizar(self):
        d1 = self.dt_inicio.date().toString("yyyy-MM-dd")
        d2 = self.dt_fim.date().toString("yyyy-MM-dd")
        
        # Pega valores dos seletores
        cat = self.cb_cat.currentText() if self.cb_cat.currentText() != "Todas" else None
        prod = self.cb_produto.currentText() if self.cb_produto.currentText() != "Todos" else None
        
        metricas = obter_metricas_bi(
            d1, d2, 
            categoria=cat,
            produto=prod,
            qtd_min=self.num_qtd.value() if self.num_qtd.value() > 0 else None,
            valor_min=self.num_valor.value() if self.num_valor.value() > 0 else None,
            lucro_min=self.num_lucro.value() if self.num_lucro.value() > 0 else None
        )

        # CORREÇÃO: Aplicando os dados nos cards
        if metricas:
            fatur, desc, qtd, lucro = metricas
            # Tratamento de None para não quebrar a formatação
            fatur = fatur or 0.0
            desc = desc or 0.0
            qtd = qtd or 0
            lucro = lucro or 0.0

            self.card_faturamento.findChild(QLabel, "valor").setText(f"R$ {fatur:,.2f}")
            self.card_vendas.findChild(QLabel, "valor").setText(str(qtd))
            self.card_lucro.findChild(QLabel, "valor").setText(f"R$ {lucro:,.2f}")
            self.card_desconto.findChild(QLabel, "valor").setText(f"R$ {desc:,.2f}")

    def carregar_filtros_combo(self):
        try:
            from services.estoque_service import listar_produtos_com_calculos
            self.cb_produto.clear()
            self.cb_cat.clear()
            self.cb_produto.addItem("Todos")
            self.cb_cat.addItem("Todas")
            
            categorias = set()
            produtos = listar_produtos_com_calculos()
            
            for p in produtos:
                # Ajustado para pegar o dado correto independente da estrutura do service
                nome = p['dados'][1] if isinstance(p, dict) else p[1]
                cat = p['dados'][2] if isinstance(p, dict) else p[2]
                self.cb_produto.addItem(nome)
                if cat: categorias.add(cat)
                
            for c in sorted(categorias):
                self.cb_cat.addItem(c)
        except Exception as e:
            print(f"Erro ao carregar combos: {e}")

    def exportar_dados(self):
        vendas = obter_vendas_detalhadas()
        if not vendas:
            QMessageBox.warning(self, "Aviso", "Não há dados para exportar.")
            return

        caminho, _ = QFileDialog.getSaveFileName(self, "Exportar Vendas", "vendas_nexus.csv", "CSV Files (*.csv)")
        if caminho:
            try:
                with open(caminho, mode='w', newline='', encoding='utf-8-sig') as file:
                    writer = csv.writer(file, delimiter=';')
                    writer.writerow(['ID', 'DATA/HORA', 'PRODUTO', 'QUANTIDADE', 'VALOR TOTAL'])
                    writer.writerows(vendas)
                QMessageBox.information(self, "Sucesso", "Exportado com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro: {str(e)}")