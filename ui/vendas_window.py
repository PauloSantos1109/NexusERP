from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
import qtawesome as qta
from services.estoque_service import listar_produtos_com_calculos
from services.vendas_service import realizar_venda, obter_vendas_detalhadas, excluir_venda

class VendasPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.lay = QHBoxLayout(self)
        self.lay.setContentsMargins(30,30,30,30)
        
        # LADO ESQUERDO: FORMULÁRIO
        form = QFrame()
        form.setFixedWidth(280)
        form.setStyleSheet("background-color: #1e293b; border-radius: 10px; padding: 15px;")
        fl = QVBoxLayout(form)
        
        titulo = QLabel("Nova Venda")
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        fl.addWidget(titulo)

        self.cb = QComboBox()
        self.q = QSpinBox(minimum=1, maximum=999)
        self.desc = QDoubleSpinBox(maximum=999)
        btn_vender = QPushButton(" FINALIZAR")
        btn_vender.setIcon(qta.icon("fa5s.check-circle", color="white"))
        btn_vender.setStyleSheet("background-color: #10b981; padding: 12px; font-weight: bold; margin-top: 10px;")
        btn_vender.clicked.connect(self.vender)

        fl.addWidget(QLabel("Produto:")); fl.addWidget(self.cb)
        fl.addWidget(QLabel("Quantidade:")); fl.addWidget(self.q)
        fl.addWidget(QLabel("Desconto R$:")); fl.addWidget(self.desc)
        fl.addWidget(btn_vender); fl.addStretch()

        # LADO DIREITO: TABELA E EXCLUSÃO
        direita = QVBoxLayout()
        self.tab = QTableWidget(0, 5) # Aumentamos para 5 colunas para mostrar o ID
        self.tab.setHorizontalHeaderLabels(["ID", "Data", "Produto", "Qtd", "Total"])
        self.tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tab.setSelectionBehavior(QAbstractItemView.SelectRows) # Seleciona a linha toda
        
        btn_del = QPushButton(qta.icon("fa5s.trash-alt", color="white"), " EXCLUIR VENDA SELECIONADA")
        btn_del.setStyleSheet("background-color: #ef4444; padding: 10px; font-weight: bold; margin-top: 10px;")
        btn_del.clicked.connect(self.deletar_venda_selecionada)

        direita.addWidget(self.tab)
        direita.addWidget(btn_del, alignment=Qt.AlignRight)

        self.lay.addWidget(form)
        self.lay.addLayout(direita)
        self.atualizar()

    def atualizar(self):
        # Atualiza o combo de produtos
        self.cb.clear()
        for p in listar_produtos_com_calculos():
            self.cb.addItem(p['dados'][1], p['dados'][0])
        
        # Atualiza a tabela (Buscando ID, Data, Nome, Qtd, Total)
        # Nota: Ajuste sua query em obter_vendas_detalhadas para trazer o ID da venda como primeiro campo
        vendas = obter_vendas_detalhadas() 
        self.tab.setRowCount(0)
        # Se sua query atual não traz o ID, você precisará ajustar o vendas_service.py
        for r, v in enumerate(vendas):
            self.tab.insertRow(r)
            for c, val in enumerate(v):
                self.tab.setItem(r, c, QTableWidgetItem(str(val)))

    def vender(self):
        if self.cb.currentData():
            ok, msg = realizar_venda(self.cb.currentData(), self.q.value(), self.desc.value())
            QMessageBox.information(self, "Venda", msg)
            self.atualizar()

    def deletar_venda_selecionada(self):
        row = self.tab.currentRow()
        if row >= 0:
            id_venda = self.tab.item(row, 0).text()
            confirm = QMessageBox.question(self, "Confirmar", f"Deseja excluir a venda #{id_venda}?")
            if confirm == QMessageBox.Yes:
                excluir_venda(int(id_venda))
                self.atualizar()
        else:
            QMessageBox.warning(self, "Aviso", "Selecione uma venda na tabela para excluir.")