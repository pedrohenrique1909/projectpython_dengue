from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox, QDialog, QFormLayout, QLineEdit, QComboBox, QCheckBox, QPushButton, \
    QVBoxLayout, QTreeWidget, QTreeWidgetItem
import mysql.connector
from mysql.connector import errorcode

db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'dbpython',
    'raise_on_warnings': True
}

def conectar_bd():
    try:
        conexao = mysql.connector.connect(**db_config)
        return conexao
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            QMessageBox.critical(None, "Erro", "Algo está errado com seu nome de usuário ou senha")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            QMessageBox.critical(None, "Erro", "O banco de dados não existe")
        else:
            QMessageBox.critical(None, "Erro", str(err))
    return None

def checar_diagnostico(lista_sintomas):
    sintomas_dengue = [
        "febre", "dor de cabeça", "dores pelo corpo", "náuseas",
        "manchas vermelhas", "sangramentos", "dor abdominal intensa", "vômitos persistentes"
    ]
    contador = 0
    for sintoma in sintomas_dengue:
        if sintoma in lista_sintomas:
            contador += 1

    min_sintomas = 3

    if contador >= min_sintomas:
        return "Positivo"
    else:
        return "Negativo"

class CadastroPacienteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cadastro de Paciente")
        self.setLayout(QFormLayout())

        self.entrada_nome = QLineEdit()
        self.layout().addRow("Nome:", self.entrada_nome)

        self.entrada_nascimento = QLineEdit()
        self.layout().addRow("Data de nascimento (YYYY-MM-DD):", self.entrada_nascimento)

        self.entrada_peso = QLineEdit()
        self.layout().addRow("Peso:", self.entrada_peso)

        self.entrada_cpf = QLineEdit()
        self.layout().addRow("CPF:", self.entrada_cpf)

        self.regioes_brasil = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]
        self.menu_regiao = QComboBox()
        self.menu_regiao.addItems(self.regioes_brasil)
        self.layout().addRow("Região:", self.menu_regiao)

        self.sintomas_dengue = [
            "febre", "dor de cabeça", "dores pelo corpo", "náuseas",
            "manchas vermelhas", "sangramentos", "dor abdominal intensa", "vômitos persistentes"
        ]
        self.variaveis_sintomas = {}
        for sintoma in self.sintomas_dengue:
            checkbox = QCheckBox(sintoma)
            self.variaveis_sintomas[sintoma] = checkbox
            self.layout().addRow(checkbox)

        self.botao_submeter = QPushButton("Cadastrar")
        self.botao_submeter.clicked.connect(self.ao_submeter)
        self.layout().addRow(self.botao_submeter)

    def pegar_sintomas(self):
        sintomas_selecionados = [sintoma for sintoma, var in self.variaveis_sintomas.items() if var.isChecked()]
        return sintomas_selecionados

    def ao_submeter(self):
        nome = self.entrada_nome.text()
        data_nascimento = self.entrada_nascimento.text()
        peso = float(self.entrada_peso.text())
        cpf = self.entrada_cpf.text()
        regiao = self.menu_regiao.currentText()
        sintomas = self.pegar_sintomas()
        diagnostico = checar_diagnostico(sintomas)

        conexao = conectar_bd()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO paciente (nome, data_nascimento, peso, cpf, regiao) VALUES (%s, %s, %s, %s, %s)",
                (nome, data_nascimento, peso, cpf, regiao))
            conexao.commit()

            id_paciente = cursor.lastrowid
            cursor.execute("INSERT INTO diagnostico (paciente_id, sintomas, diagnostico) VALUES (%s, %s, %s)",
                           (id_paciente, ','.join(sintomas), diagnostico))
            conexao.commit()
            cursor.close()
            conexao.close()
            QMessageBox.information(self, "Diagnóstico", f"Diagnóstico: {diagnostico}")
            self.accept()

class PacientesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pacientes")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.arvore = QTreeWidget()
        self.arvore.setColumnCount(7)
        self.arvore.setHeaderLabels(["Nome", "Data de Nascimento", "Peso", "CPF", "Região", "Sintomas", "Diagnóstico"])
        self.layout.addWidget(self.arvore)

    def listar_pacientes(self):
        self.arvore.clear()
        conexao = conectar_bd()
        if conexao:
            try:
                cursor = conexao.cursor()
                cursor.execute("""
                SELECT p.nome, p.data_nascimento, p.peso, p.cpf, p.regiao, d.sintomas, d.diagnostico 
                FROM paciente p 
                JOIN diagnostico d ON p.id = d.paciente_id
                """)
                for row in cursor:
                    item = QTreeWidgetItem(list(map(str, row)))
                    self.arvore.addTopLevelItem(item)
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Erro", f"Erro ao listar pacientes: {err}")
            finally:
                cursor.close()
                conexao.close()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Diagnóstico")

        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.menu_bar = self.menuBar()
        self.menu_paciente = self.menu_bar.addMenu("Pacientes")
        self.menu_diagnostico = self.menu_bar.addMenu("Diagnósticos")

        self.menu_paciente.addAction("Adicionar", self.obter_dados_paciente)
        self.menu_paciente.addAction("Exibir Todos", self.listar_pacientes)
        self.menu_paciente.addAction("Atualizar", self.atualizar_paciente)
        self.menu_paciente.addAction("Deletar", self.excluir_paciente)

        self.menu_diagnostico.addAction("Contagem Geral", self.contar_diagnosticos)
        self.menu_diagnostico.addAction("Contagem por Região", self.contar_diagnosticos_por_regiao)

    def obter_dados_paciente(self):
        dialog = CadastroPacienteDialog()
        dialog.exec_()

    def listar_pacientes(self):
        dialog = PacientesDialog(self)
        dialog.listar_pacientes()
        dialog.exec_()

    def contar_diagnosticos(self):
        conexao = conectar_bd()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute("""
            SELECT diagnostico, COUNT(*) 
            FROM diagnostico 
            GROUP BY diagnostico
            """)
            contagem = cursor.fetchall()
            cursor.close()
            conexao.close()
            resultado = ""
            for (diagnostico, count) in contagem:
                resultado += f"Diagnóstico: {diagnostico}, Quantidade: {count}\n"
            QMessageBox.information(self, "Contagem de Diagnósticos", resultado)

    def contar_diagnosticos_por_regiao(self):
        conexao = conectar_bd()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute("""
            SELECT p.regiao, d.diagnostico, COUNT(*) 
            FROM diagnostico d
            JOIN paciente p ON p.id = d.paciente_id
            GROUP BY p.regiao, d.diagnostico
            """)
            contagem = cursor.fetchall()
            cursor.close()
            conexao.close()
            resultado = ""
            for (regiao, diagnostico, count) in contagem:
                resultado += f"Região: {regiao}, Diagnóstico: {diagnostico}, Quantidade: {count}\n"
            QMessageBox.information(self, "Contagem de Diagnósticos por Região", resultado)

    def atualizar_paciente(self):
        cpf, ok = QtWidgets.QInputDialog.getText(self, "Atualizar Dados do Paciente",
                                                 "Digite o CPF do paciente que deseja atualizar:")
        if ok:
            conexao = conectar_bd()
            if conexao:
                cursor = conexao.cursor()
                cursor.execute("SELECT id FROM paciente WHERE cpf = %s", (cpf,))
                result = cursor.fetchone()
                if result:
                    id_paciente = result[0]
                    novo_nome, ok = QtWidgets.QInputDialog.getText(self, "Atualizar Dados do Paciente", "Novo nome:")
                    if not ok: return
                    nova_data_nascimento, ok = QtWidgets.QInputDialog.getText(self, "Atualizar Dados do Paciente",
                                                                              "Nova data de nascimento (YYYY-MM-DD):")
                    if not ok: return
                    novo_peso, ok = QtWidgets.QInputDialog.getDouble(self, "Atualizar Dados do Paciente", "Novo peso:")
                    if not ok: return
                    cursor.execute("""
                    UPDATE paciente 
                    SET nome = %s, data_nascimento = %s, peso = %s 
                    WHERE id = %s
                    """, (novo_nome, nova_data_nascimento, novo_peso, id_paciente))
                    conexao.commit()
                    QMessageBox.information(self, "Sucesso", "Dados atualizados com sucesso!")
                else:
                    QMessageBox.critical(self, "Erro", "Paciente não encontrado.")
                cursor.close()
                conexao.close()

    def excluir_paciente(self):
        cpf, ok = QtWidgets.QInputDialog.getText(self, "Deletar Paciente",
                                                 "Digite o CPF do paciente que deseja deletar:")
        if ok:
            conexao = conectar_bd()
            if conexao:
                cursor = conexao.cursor()
                cursor.execute("SELECT id, nome FROM paciente WHERE cpf = %s", (cpf,))
                result = cursor.fetchone()
                if result:
                    id_paciente, nome_paciente = result
                    decisao, ok = QtWidgets.QInputDialog.getText(self, "APAGAR PACIENTE",
                                                                 f"Confirma apagar o paciente {nome_paciente}?\nSIM OU NÃO:")
                    if ok and decisao.strip().lower() == 'sim':
                        cursor.execute('DELETE FROM paciente WHERE id = %s', (id_paciente,))
                        conexao.commit()
                        QMessageBox.information(self, "Sucesso", "Paciente apagado com sucesso!")
                    else:
                        QMessageBox.information(self, "Operação cancelada", "O paciente não foi apagado.")
                else:
                    QMessageBox.critical(self, "Erro", "Paciente não encontrado.")
                cursor.close()
                conexao.close()

def main():
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
