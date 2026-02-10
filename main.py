import sys
from PySide6.QtWidgets import QApplication
from database.db import init_db  # Importa a função de criação
from ui.main_window import MainWindow
from database.db import init_db

if __name__ == "__main__":
    # 1. Tenta criar o banco e as tabelas
    try:
        init_db() 
        print("Banco de dados verificado/criado com sucesso!")
    except Exception as e:
        print(f"Erro ao iniciar banco: {e}")

    app = QApplication(sys.argv)
    app.setStyle("Fusion") 
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())