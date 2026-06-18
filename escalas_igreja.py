if __name__ == "__main__":
    try:
        import Atualizador
    except ImportError:
        pass
    # ... resto do código que já tem ...
import random
import json
import os
import shutil
import subprocess
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# Bibliotecas para relatórios e exportação
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    import openpyxl
    from openpyxl import Workbook
except ImportError:
    pass

# ----------------------
# CONFIGURAÇÕES
# ----------------------
pasta_dados = os.path.join(os.path.expanduser("~"), "Documentos", "SistemaEscalas")
pasta_export = os.path.join(pasta_dados, "Exportacoes")
if not os.path.exists(pasta_dados):
    os.makedirs(pasta_dados)
if not os.path.exists(pasta_export):
    os.makedirs(pasta_export)

ARQUIVO_PESSOAS_REGULARES = os.path.join(pasta_dados, "pessoas_regulares.json")
ARQUIVO_PESSOAS_TREINAMENTO = os.path.join(pasta_dados, "pessoas_treinamento.json")
ARQUIVO_ESCALAS_REGULARES = os.path.join(pasta_dados, "escalas_regulares.json")
ARQUIVO_ESCALAS_TREINAMENTO = os.path.join(pasta_dados, "escalas_treinamento.json")
ARQUIVO_CONFIG = os.path.join(pasta_dados, "config.json")
PASTA_BACKUP = os.path.join(pasta_dados, "backups")

CONFIG_PADRAO = {
    "senha": "igreja123",
    "limite_escalas_mes": 3,
    "dias_bloquear_edicao": 7,
    "nome_igreja": "Igreja Evangélica",
    "endereco_igreja": "Alvorada d'Oeste - RO"
}

# ----------------------
# FUNÇÕES AUXILIARES
# ----------------------
def carregar_dados(arquivo, padrao=None):
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return padrao.copy() if isinstance(padrao, dict) else padrao if padrao is not None else {}

def salvar_dados(arquivo, dados):
    try:
        with open(arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
    except Exception as e:
        raise Exception(f"Erro ao salvar: {e}")

def criar_backup():
    if not os.path.exists(PASTA_BACKUP):
        os.makedirs(PASTA_BACKUP)
    data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
    for arq in [ARQUIVO_PESSOAS_REGULARES, ARQUIVO_PESSOAS_TREINAMENTO,
                ARQUIVO_ESCALAS_REGULARES, ARQUIVO_ESCALAS_TREINAMENTO, ARQUIVO_CONFIG]:
        if os.path.exists(arq):
            shutil.copy2(arq, f"{PASTA_BACKUP}/{os.path.basename(arq).replace('.json', '')}_{data_hora}.json")
    messagebox.showinfo("Backup", "Criado com sucesso!")

def data_para_dia_semana(data_str):
    try:
        dias = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
        data = datetime.strptime(data_str, "%d/%m/%Y")
        return dias[data.weekday()]
    except:
        return ""

def pode_editar_escala(data_escala_str, dias_bloquear):
    try:
        data_escala = datetime.strptime(data_escala_str, "%d/%m/%Y")
        diferenca = (datetime.now() - data_escala).days
        return diferenca <= dias_bloquear
    except:
        return False

# ----------------------
# CALENDÁRIO
# ----------------------
class CalendarioPopup(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Escolher Data")
        self.geometry("320x320")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.data_atual = datetime.now()
        self.dias_semana = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]

        self.frame_cabecalho = ttk.Frame(self)
        self.frame_cabecalho.pack(pady=10)
        ttk.Button(self.frame_cabecalho, text="<", command=self.mes_anterior).grid(row=0, column=0, padx=5)
        self.label_mes_ano = ttk.Label(self.frame_cabecalho, text="", font=("Arial", 12, "bold"))
        self.label_mes_ano.grid(row=0, column=1, padx=15)
        ttk.Button(self.frame_cabecalho, text=">", command=self.mes_proximo).grid(row=0, column=2, padx=5)

        self.frame_dias_semana = ttk.Frame(self)
        self.frame_dias_semana.pack()
        for col, dia in enumerate(self.dias_semana):
            ttk.Label(self.frame_dias_semana, text=dia, width=5, anchor="center", font=("Arial", 9, "bold")).grid(row=0, column=col, padx=2, pady=2)

        self.frame_grade = ttk.Frame(self)
        self.frame_grade.pack(pady=5)
        self.atualizar_calendario()

    def mes_anterior(self):
        primeiro_dia = self.data_atual.replace(day=1)
        self.data_atual = primeiro_dia - timedelta(days=1)
        self.atualizar_calendario()

    def mes_proximo(self):
        proximo_mes = self.data_atual.replace(day=28) + timedelta(days=4)
        self.data_atual = proximo_mes.replace(day=1)
        self.atualizar_calendario()

    def atualizar_calendario(self):
        for widget in self.frame_grade.winfo_children():
            widget.destroy()
        meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                 "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.label_mes_ano.config(text=f"{meses[self.data_atual.month - 1]} de {self.data_atual.year}")
        primeiro_dia = self.data_atual.replace(day=1)
        ultimo_dia = (primeiro_dia.replace(month=primeiro_dia.month % 12 + 1, day=1) - timedelta(days=1))
        dia_inicio = primeiro_dia.weekday()
        dia_atual = 1
        for linha in range(6):
            for coluna in range(7):
                if linha == 0 and coluna < dia_inicio:
                    ttk.Label(self.frame_grade, text="", width=5).grid(row=linha, column=coluna, padx=2, pady=2)
                elif dia_atual <= ultimo_dia.day:
                    data_selecionada = self.data_atual.replace(day=dia_atual)
                    btn = ttk.Button(self.frame_grade, text=str(dia_atual), width=5,
                                     command=lambda d=data_selecionada: self.selecionar_dia(d))
                    btn.grid(row=linha, column=coluna, padx=2, pady=2)
                    dia_atual += 1
                else:
                    ttk.Label(self.frame_grade, text="", width=5).grid(row=linha, column=coluna, padx=2, pady=2)

    def selecionar_dia(self, data):
        data_str = data.strftime("%d/%m/%Y")
        dia_semana = data_para_dia_semana(data_str)
        self.callback(data_str, dia_semana)
        self.destroy()

# ----------------------
# SISTEMA PRINCIPAL
# ----------------------
class SistemaEscalas:
    def __init__(self, root):
        self.root = root
        self.root.title("📋 Sistema de Escalas - Igreja")
        self.root.geometry("980x720")
        self.root.minsize(880, 620)
        self.root.configure(bg="#f0f4f8")

        self.fonte = ("Arial", 11)
        self.fonte_destaque = ("Arial", 12, "bold")
        self.cor_botao = "#2c5c97"
        self.cor_texto_botao = "#ffffff"

        self.config = carregar_dados(ARQUIVO_CONFIG, CONFIG_PADRAO)
        salvar_dados(ARQUIVO_CONFIG, self.config)

        if not self.verificar_senha():
            self.root.quit()
            return

        self.criar_menu()
        self.criar_abas()
        self.carregar_tudo()

    def verificar_senha(self):
        senha = simpledialog.askstring("Acesso", "Digite a senha do sistema:", show="*")
        return senha == self.config["senha"]

    def criar_menu(self):
        menu_bar = tk.Menu(self.root)
        menu_config = tk.Menu(menu_bar, tearoff=0)
        menu_config.add_command(label="Alterar Senha", command=self.janela_alterar_senha)
        menu_config.add_command(label="Ajustar Limite de Escalas", command=self.janela_ajustar_limite)
        menu_config.add_command(label="Dias para Bloquear Edição", command=self.janela_ajustar_bloqueio)
        menu_config.add_separator()
        menu_config.add_command(label="Alterar Dados da Igreja", command=self.janela_editar_dados_igreja)
        menu_bar.add_cascade(label="⚙️ Configurações", menu=menu_config)

        menu_relatorios = tk.Menu(menu_bar, tearoff=0)
        menu_relatorios.add_command(label="Escalas por Pessoa", command=self.janela_relatorio_pessoas)
        menu_relatorios.add_command(label="Escalas por Função", command=self.janela_relatorio_funcoes)
        menu_relatorios.add_command(label="Escalas por Período", command=self.janela_relatorio_periodo)
        menu_bar.add_cascade(label="📊 Relatórios", menu=menu_relatorios)

        menu_ferramentas = tk.Menu(menu_bar, tearoff=0)
        menu_ferramentas.add_command(label="Criar Backup", command=criar_backup)
        menu_bar.add_cascade(label="🛠️ Ferramentas", menu=menu_ferramentas)
        self.root.config(menu=menu_bar)

    def criar_abas(self):
        self.abas = ttk.Notebook(self.root)
        self.abas.pack(fill="both", expand=True, padx=8, pady=8)

        # Aba Pessoas Regulares
        self.aba_pessoas_reg = ttk.Frame(self.abas)
        self.abas.add(self.aba_pessoas_reg, text="👥 Pessoas Regulares")
        frame_botoes_reg = ttk.Frame(self.aba_pessoas_reg)
        frame_botoes_reg.pack(fill="x", padx=5, pady=5)
        ttk.Button(frame_botoes_reg, text="Cadastrar", command=lambda: self.janela_cadastrar("regular"), style="Botao.TButton").pack(side="left", padx=3)
        ttk.Button(frame_botoes_reg, text="Editar", command=lambda: self.janela_editar_pessoa("regular"), style="Botao.TButton").pack(side="left", padx=3)
        ttk.Button(frame_botoes_reg, text="Excluir", command=lambda: self.excluir_pessoa("regular"), style="Botao.TButton").pack(side="left", padx=3)
        ttk.Label(frame_botoes_reg, text="🔍 Pesquisar:", font=self.fonte).pack(side="left", padx=10)
        self.busca_reg = ttk.Entry(frame_botoes_reg, width=30)
        self.busca_reg.pack(side="left")
        self.busca_reg.bind("<KeyRelease>", lambda e: self.filtrar_pessoas("regular"))
        self.lista_pessoas_reg = ttk.Treeview(self.aba_pessoas_reg, columns=("Função", "Nome", "Disponibilidade", "Escalas Mês"), show="headings")
        self.lista_pessoas_reg.heading("Função", text="Função")
        self.lista_pessoas_reg.heading("Nome", text="Nome")
        self.lista_pessoas_reg.heading("Disponibilidade", text="Dias Disponíveis")
        self.lista_pessoas_reg.heading("Escalas Mês", text="Escalas / Mês")
        self.lista_pessoas_reg.column("Função", width=140)
        self.lista_pessoas_reg.column("Nome", width=260)
        self.lista_pessoas_reg.column("Disponibilidade", width=240)
        self.lista_pessoas_reg.column("Escalas Mês", width=120, anchor="center")
        self.lista_pessoas_reg.pack(fill="both", expand=True, padx=5, pady=5)

        # Aba Pessoas Treinamento
        self.aba_pessoas_treino = ttk.Frame(self.abas)
        self.abas.add(self.aba_pessoas_treino, text="🎓 Pessoas Treinamento")
        frame_botoes_treino = ttk.Frame(self.aba_pessoas_treino)
        frame_botoes_treino.pack(fill="x", padx=5, pady=5)
        ttk.Button(frame_botoes_treino, text="Cadastrar", command=lambda: self.janela_cadastrar("treinamento"), style="Botao.TButton").pack(side="left", padx=3)
        ttk.Button(frame_botoes_treino, text="Editar", command=lambda: self.janela_editar_pessoa("treinamento"), style="Botao.TButton").pack(side="left", padx=3)
        ttk.Button(frame_botoes_treino, text="Excluir", command=lambda: self.excluir_pessoa("treinamento"), style="Botao.TButton").pack(side="left", padx=3)
        ttk.Label(frame_botoes_treino, text="🔍 Pesquisar:", font=self.fonte).pack(side="left", padx=10)
        self.busca_treino = ttk.Entry(frame_botoes_treino, width=30)
        self.busca_treino.pack(side="left")
        self.busca_treino.bind("<KeyRelease>", lambda e: self.filtrar_pessoas("treinamento"))
        self.lista_pessoas_treino = ttk.Treeview(self.aba_pessoas_treino, columns=("Função", "Nome", "Disponibilidade", "Escalas Mês"), show="headings")
        self.lista_pessoas_treino.heading("Função", text="Função")
        self.lista_pessoas_treino.heading("Nome", text="Nome")
        self.lista_pessoas_treino.heading("Disponibilidade", text="Dias Disponíveis")
        self.lista_pessoas_treino.heading("Escalas Mês", text="Escalas / Mês")
        self.lista_pessoas_treino.column("Função", width=140)
        self.lista_pessoas_treino.column("Nome", width=260)
        self.lista_pessoas_treino.column("Disponibilidade", width=240)
        self.lista_pessoas_treino.column("Escalas Mês", width=120, anchor="center")
        self.lista_pessoas_treino.pack(fill="both", expand=True, padx=5, pady=5)

        # Aba Escalas Regulares
        self.aba_esc_reg = ttk.Frame(self.abas)
        self.abas.add(self.aba_esc_reg, text="🗓️ Escalas Regulares")
        frame_esc_reg = ttk.Frame(self.aba_esc_reg)
        frame_esc_reg.pack(fill="x", padx=5, pady=5)
        ttk.Button(frame_esc_reg, text="Gerar Escala", command=lambda: self.janela_gerar("regular"), style="Botao.TButton").pack(side="left", padx=3)
        ttk.Button(frame_esc_reg, text="Ver/Editar", command=lambda: self.janela_ver_editar("regular"), style="Botao.TButton").pack(side="left", padx=3)
        ttk.Button(frame_esc_reg, text="Excluir", command=lambda: self.excluir_escala("regular"), style="Botao.TButton").pack(side="left", padx=3)
        ttk.Label(frame_esc_reg, text="🔍 Pesquisar:", font=self.fonte).pack(side="left", padx=10)
        self.busca_esc_reg = ttk.Entry(frame_esc_reg, width=30)
        self.busca_esc_reg.pack(side="left")
        self.busca_esc_reg.bind("<KeyRelease>", lambda e: self.filtrar_escalas("regular"))
        self.lista_esc_reg = ttk.Treeview(self.aba_esc_reg, columns=("Data", "Dia", "Status"), show="headings")
        self.lista_esc_reg.heading("Data", text="Data")
        self.lista_esc_reg.heading("Dia", text="Dia da Semana")
        self.lista_esc_reg.heading("Status", text="Edição")
        self.lista_esc_reg.column("Data", width=120)
        self.lista_esc_reg.column("Dia", width=250)
        self.lista_esc_reg.column("Status", width=120, anchor="center")
        self.lista_esc_reg.pack(fill="both", expand=True, padx=5, pady=5)

        # Aba Escalas Treinamento
        self.aba_esc_treino = ttk.Frame(self.abas)
        self.abas.add(self.aba_esc_treino, text="🎓 Escalas de Treinamento")
        frame_esc_treino = ttk.Frame(self.aba_esc_treino)
        frame_esc_treino.pack(fill="x", padx=5, pady=5)
        ttk.Button(frame_esc_treino, text="Gerar Escala", command=lambda: self.janela_gerar("treinamento"), style="Botao.TButton").pack(side="left", padx=3)
        ttk.Button(frame_esc_treino, text="Ver/Editar", command=lambda: self.janela_ver_editar("treinamento"), style="Botao.TButton").pack(side="left", padx=3)
        ttk.Button(frame_esc_treino, text="Excluir", command=lambda: self.excluir_escala("treinamento"), style="Botao.TButton").pack(side="left", padx=3)
        ttk.Label(frame_esc_treino, text="🔍 Pesquisar:", font=self.fonte).pack(side="left", padx=10)
        self.busca_esc_treino = ttk.Entry(frame_esc_treino, width=30)
        self.busca_esc_treino.pack(side="left")
        self.busca_esc_treino.bind("<KeyRelease>", lambda e: self.filtrar_escalas("treinamento"))
        self.lista_esc_treino = ttk.Treeview(self.aba_esc_treino, columns=("Data", "Dia", "Status"), show="headings")
        self.lista_esc_treino.heading("Data", text="Data")
        self.lista_esc_treino.heading("Dia", text="Dia da Semana")
        self.lista_esc_treino.heading("Status", text="Edição")
        self.lista_esc_treino.column("Data", width=120)
        self.lista_esc_treino.column("Dia", width=250)
        self.lista_esc_treino.column("Status", width=120, anchor="center")
        self.lista_esc_treino.pack(fill="both", expand=True, padx=5, pady=5)

        estilo = ttk.Style()
        estilo.configure("Botao.TButton", font=self.fonte, padding=5)

    # ----------------------
    # CONFIGURAÇÕES
    # ----------------------
    def janela_alterar_senha(self):
        janela = tk.Toplevel(self.root)
        janela.title("Alterar Senha")
        janela.geometry("350x220")
        janela.resizable(False, False)
        janela.configure(bg="#f0f4f8")
        ttk.Label(janela, text="Senha Atual:", font=self.fonte_destaque).pack(pady=8)
        senha_atual = ttk.Entry(janela, show="*", width=30)
        senha_atual.pack()
        ttk.Label(janela, text="Nova Senha:", font=self.fonte_destaque).pack(pady=8)
        nova_senha = ttk.Entry(janela, show="*", width=30)
        nova_senha.pack()
        ttk.Label(janela, text="Confirmar Nova Senha:", font=self.fonte_destaque).pack(pady=8)
        confirma_senha = ttk.Entry(janela, show="*", width=30)
        confirma_senha.pack()
        def salvar():
            if senha_atual.get() != self.config["senha"]:
                messagebox.showerror("Erro", "Senha atual incorreta!")
                return
            if nova_senha.get() != confirma_senha.get():
                messagebox.showerror("Erro", "As senhas não coincidem!")
                return
            if len(nova_senha.get()) < 4:
                messagebox.showwarning("Aviso", "Use pelo menos 4 caracteres!")
                return
            self.config["senha"] = nova_senha.get()
            salvar_dados(ARQUIVO_CONFIG, self.config)
            messagebox.showinfo("Sucesso", "Senha alterada!")
            janela.destroy()
        ttk.Button(janela, text="Salvar", command=salvar, style="Botao.TButton").pack(pady=15)

    def janela_ajustar_limite(self):
        janela = tk.Toplevel(self.root)
        janela.title("Limite de Escalas por Mês")
        janela.geometry("320x180")
        janela.resizable(False, False)
        janela.configure(bg="#f0f4f8")
        ttk.Label(janela, text="Máximo de escalas por pessoa/mês:", font=self.fonte_destaque).pack(pady=15)
        valor = ttk.Entry(janela, width=10, justify="center", font=self.fonte_destaque)
        valor.insert(0, str(self.config["limite_escalas_mes"]))
        valor.pack(pady=5)
        def salvar():
            try:
                novo_limite = int(valor.get())
                if novo_limite < 1:
                    raise ValueError
                self.config["limite_escalas_mes"] = novo_limite
                salvar_dados(ARQUIVO_CONFIG, self.config)
                messagebox.showinfo("Sucesso", "Limite atualizado!")
                self.carregar_pessoas("regular")
                self.carregar_pessoas("treinamento")
                janela.destroy()
            except:
                messagebox.showerror("Erro", "Digite um número válido maior que zero!")
        ttk.Button(janela, text="Salvar", command=salvar, style="Botao.TButton").pack(pady=10)

    def janela_ajustar_bloqueio(self):
        janela = tk.Toplevel(self.root)
        janela.title("Bloquear Edição de Escalas")
        janela.geometry("350x180")
        janela.resizable(False, False)
        janela.configure(bg="#f0f4f8")
        ttk.Label(janela, text="Dias após a data para bloquear edição:", font=self.fonte_destaque).pack(pady=15)
        valor = ttk.Entry(janela, width=10, justify="center", font=self.fonte_destaque)
        valor.insert(0, str(self.config["dias_bloquear_edicao"]))
        valor.pack(pady=5)
        def salvar():
            try:
                dias = int(valor.get())
                if dias < 0:
                    raise ValueError
                self.config["dias_bloquear_edicao"] = dias
                salvar_dados(ARQUIVO_CONFIG, self.config)
                messagebox.showinfo("Sucesso", "Configuração salva!")
                self.carregar_escalas("regular")
                self.carregar_escalas("treinamento")
                janela.destroy()
            except:
                messagebox.showerror("Erro", "Digite um número válido!")
        ttk.Button(janela, text="Salvar", command=salvar, style="Botao.TButton").pack(pady=10)

    def janela_editar_dados_igreja(self):
        janela = tk.Toplevel(self.root)
        janela.title("Dados da Igreja")
        janela.geometry("400x220")
        janela.resizable(False, False)
        janela.configure(bg="#f0f4f8")
        ttk.Label(janela, text="Nome da Igreja:", font=self.fonte_destaque).pack(pady=8)
        nome = ttk.Entry(janela, width=45)
        nome.insert(0, self.config["nome_igreja"])
        nome.pack()
        ttk.Label(janela, text="Endereço / Cidade:", font=self.fonte_destaque).pack(pady=8)
        endereco = ttk.Entry(janela, width=45)
        endereco.insert(0, self.config["endereco_igreja"])
        endereco.pack()
        def salvar():
            self.config["nome_igreja"] = nome.get().strip()
            self.config["endereco_igreja"] = endereco.get().strip()
            salvar_dados(ARQUIVO_CONFIG, self.config)
            messagebox.showinfo("Sucesso", "Dados atualizados!")
            janela.destroy()
        ttk.Button(janela, text="Salvar", command=salvar, style="Botao.TButton").pack(pady=15)

    # ----------------------
    # RELATÓRIOS
    # ----------------------
    def janela_relatorio_pessoas(self):
        janela = tk.Toplevel(self.root)
        janela.title("Relatório de Escalas por Pessoa")
        janela.geometry("750x550")
        janela.configure(bg="#f0f4f8")
        frame_top = ttk.Frame(janela)
        frame_top.pack(fill="x", padx=10, pady=10)
        ttk.Label(frame_top, text="Mês/Ano (ex: 06/2026):", font=self.fonte_destaque).pack(side="left", padx=5)
        mes_ano = ttk.Entry(frame_top, width=12)
        mes_ano.insert(0, datetime.now().strftime("%m/%Y"))
        mes_ano.pack(side="left", padx=5)
        ttk.Button(frame_top, text="Gerar Relatório", command=lambda: self.mostrar_relatorio_pessoas(mes_ano.get(), tree), style="Botao.TButton").pack(side="left", padx=10)
        tree = ttk.Treeview(janela, columns=("Nome", "Função", "Escalas", "Status"), show="headings")
        tree.heading("Nome", text="Nome")
        tree.heading("Função", text="Função")
        tree.heading("Escalas", text="Número de Escalas")
        tree.heading("Status", text="Status")
        tree.column("Nome", width=250)
        tree.column("Função", width=200)
        tree.column("Escalas", width=150, anchor="center")
        tree.column("Status", width=150, anchor="center")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

    def mostrar_relatorio_pessoas(self, mes_ano, tree):
        tree.delete(*tree.get_children())
        try:
            mes, ano = mes_ano.split("/")
            mes = int(mes)
            ano = int(ano)
        except:
            messagebox.showerror("Erro", "Formato inválido! Use: MM/AAAA")
            return
        limite = self.config["limite_escalas_mes"]
        pessoas_reg = carregar_dados(ARQUIVO_PESSOAS_REGULARES, {})
        pessoas_treino = carregar_dados(ARQUIVO_PESSOAS_TREINAMENTO, {})
        for funcao, lista in pessoas_reg.items():
            for p in lista:
                qtd = p.get("escalas_mes", 0)
                if qtd >= limite:
                    status = "⚠️ Atingiu Limite"
                elif qtd >= limite - 1:
                    status = "🔔 Próximo do Limite"
                else:
                    status = "✅ Normal"
                tree.insert("", "end", values=(p["nome"], funcao.upper(), qtd, status))
        for funcao, lista in pessoas_treino.items():
            for p in lista:
                qtd = p.get("escalas_mes", 0)
                if qtd >= limite:
                    status = "⚠️ Atingiu Limite"
                elif qtd >= limite - 1:
                    status = "🔔 Próximo do Limite"
                else:
                    status = "✅ Normal"
                tree.insert("", "end", values=(p["nome"], f"{funcao.upper()} (Treinamento)", qtd, status))

    def janela_relatorio_funcoes(self):
        janela = tk.Toplevel(self.root)
        janela.title("Relatório por Função")
        janela.geometry("600x450")
        tree = ttk.Treeview(janela, columns=("Função", "Total"), show="headings")
        tree.heading("Função", text="Função")
        tree.heading("Total", text="Quantidade de Escalas")
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        escalas_reg = carregar_dados(ARQUIVO_ESCALAS_REGULARES, {})
        escalas_treino = carregar_dados(ARQUIVO_ESCALAS_TREINAMENTO, {})
        contagem = {}
        for e in list(escalas_reg.values()) + list(escalas_treino.values()):
            for funcao in e["servicos"]:
                contagem[funcao] = contagem.get(funcao, 0) + 1
        for funcao, qtd in contagem.items():
            tree.insert("", "end", values=(funcao.upper(), qtd))

    def janela_relatorio_periodo(self):
        janela = tk.Toplevel(self.root)
        janela.title("Relatório por Período")
        janela.geometry("750x550")
        frame = ttk.Frame(janela)
        frame.pack(fill="x", padx=10, pady=10)
        ttk.Label(frame, text="Data Início (DD/MM/AAAA):").grid(row=0, column=0, padx=5)
        data_ini = ttk.Entry(frame, width=12)
        data_ini.grid(row=0, column=1, padx=5)
        ttk.Label(frame, text="Data Fim (DD/MM/AAAA):").grid(row=0, column=2, padx=5)
        data_fim = ttk.Entry(frame, width=12)
        data_fim.grid(row=0, column=3, padx=5)
        tree = ttk.Treeview(janela, columns=("Data", "Dia", "Tipo"), show="headings")
        tree.heading("Data", text="Data")
        tree.heading("Dia", text="Dia")
        tree.heading("Tipo", text="Tipo de Escala")
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        def gerar():
            tree.delete(*tree.get_children())
            try:
                di = datetime.strptime(data_ini.get(), "%d/%m/%Y")
                df = datetime.strptime(data_fim.get(), "%d/%m/%Y")
            except:
                messagebox.showerror("Erro", "Datas inválidas!")
                return
            esc_reg = carregar_dados(ARQUIVO_ESCALAS_REGULARES, {})
            esc_treino = carregar_dados(ARQUIVO_ESCALAS_TREINAMENTO, {})
            for d, info in esc_reg.items():
                if di <= datetime.strptime(d, "%d/%m/%Y") <= df:
                    tree.insert("", "end", values=(d, info["dia"].capitalize(), "Regular"))
            for d, info in esc_treino.items():
                if di <= datetime.strptime(d, "%d/%m/%Y") <= df:
                    tree.insert("", "end", values=(d, info["dia"].capitalize(), "Treinamento"))
        ttk.Button(frame, text="Gerar", command=gerar, style="Botao.TButton").grid(row=0, column=4, padx=10)

    # ----------------------
    # CARREGAR E FILTRAR DADOS
    # ----------------------
    def carregar_tudo(self):
        self.carregar_pessoas("regular")
        self.carregar_pessoas("treinamento")
        self.carregar_escalas("regular")
        self.carregar_escalas("treinamento")

    def carregar_pessoas(self, tipo):
        lista = self.lista_pessoas_reg if tipo == "regular" else self.lista_pessoas_treino
        arquivo = ARQUIVO_PESSOAS_REGULARES if tipo == "regular" else ARQUIVO_PESSOAS_TREINAMENTO
        lista.delete(*lista.get_children())
        pessoas = carregar_dados(arquivo, {})
        limite = self.config["limite_escalas_mes"]
        for funcao, itens in pessoas.items():
            for p in itens:
                qtd = p.get("escalas_mes", 0)
                lista.insert("", "end", values=(funcao.upper(), p["nome"], p["disponibilidade"].capitalize(), f"{qtd} / {limite}"))

    def filtrar_pessoas(self, tipo, evento=None):
        termo = (self.busca_reg if tipo == "regular" else self.busca_treino).get().strip().lower()
        lista = self.lista_pessoas_reg if tipo == "regular" else self.lista_pessoas_treino
        arquivo = ARQUIVO_PESSOAS_REGULARES if tipo == "regular" else ARQUIVO_PESSOAS_TREINAMENTO
        lista.delete(*lista.get_children())
        pessoas = carregar_dados(arquivo, {})
        limite = self.config["limite_escalas_mes"]
        for funcao, itens in pessoas.items():
            for p in itens:
                if termo in p["nome"].lower() or termo in funcao.lower():
                    qtd = p.get("escalas_mes", 0)
                    lista.insert("", "end", values=(funcao.upper(), p["nome"], p["disponibilidade"].capitalize(), f"{qtd} / {limite}"))

    def carregar_escalas(self, tipo):
        lista = self.lista_esc_reg if tipo == "regular" else self.lista_esc_treino
        arquivo = ARQUIVO_ESCALAS_REGULARES if tipo == "regular" else ARQUIVO_ESCALAS_TREINAMENTO
        lista.delete(*lista.get_children())
        escalas = carregar_dados(arquivo, {})
        dias_bloquear = self.config["dias_bloquear_edicao"]
        for data, info in sorted(escalas.items(), reverse=True):
            status = "🔒 Bloqueada" if not pode_editar_escala(data, dias_bloquear) else "✏️ Editar"
            lista.insert("", "end", values=(data, info["dia"].capitalize(), status))

    def filtrar_escalas(self, tipo, evento=None):
        termo = (self.busca_esc_reg if tipo == "regular" else self.busca_esc_treino).get().strip().lower()
        lista = self.lista_esc_reg if tipo == "regular" else self.lista_esc_treino
        arquivo = ARQUIVO_ESCALAS_REGULARES if tipo == "regular" else ARQUIVO_ESCALAS_TREINAMENTO
        lista.delete(*lista.get_children())
        escalas = carregar_dados(arquivo, {})
        dias_bloquear = self.config["dias_bloquear_edicao"]
        for data, info in escalas.items():
            if termo in data or termo in info["dia"]:
                status = "🔒 Bloqueada" if not pode_editar_escala(data, dias_bloquear) else "✏️ Editar"
                lista.insert("", "end", values=(data, info["dia"].capitalize(), status))

    # ----------------------
    # CADASTRO, EDIÇÃO E EXCLUSÃO
    # ----------------------
    def janela_cadastrar(self, tipo):
        janela = tk.Toplevel(self.root)
        titulo = "Cadastrar Pessoa Regular" if tipo == "regular" else "Cadastrar Pessoa Treinamento"
        janela.title(titulo)
        janela.geometry("420x300")
        janela.configure(bg="#f0f4f8")
        janela.resizable(False, False)
        tk.Label(janela, text="Nome Completo:", font=self.fonte_destaque, bg="#f0f4f8").pack(pady=6)
        nome = tk.Entry(janela, font=self.fonte, width=45)
        nome.pack()
        tk.Label(janela, text="Função:", font=self.fonte_destaque, bg="#f0f4f8").pack(pady=6)
        funcao = tk.Entry(janela, font=self.fonte, width=45)
        funcao.pack()
        tk.Label(janela, text="Dias disponíveis (ex: domingo, quarta):", font=self.fonte_destaque, bg="#f0f4f8").pack(pady=6)
        dias = tk.Entry(janela, font=self.fonte, width=45)
        dias.pack()
        def salvar():
            if not nome.get().strip() or not funcao.get().strip() or not dias.get().strip():
                messagebox.showwarning("Aviso", "Preencha todos os campos!")
                return
            arquivo = ARQUIVO_PESSOAS_REGULARES if tipo == "regular" else ARQUIVO_PESSOAS_TREINAMENTO
            pessoas = carregar_dados(arquivo, {})
            f = funcao.get().strip().lower()
            pessoas.setdefault(f, []).append({
                "nome": nome.get().strip().title(),
                "disponibilidade": dias.get().strip().lower(),
                "escalas_mes": 0
            })
            salvar_dados(arquivo, pessoas)
            self.carregar_pessoas(tipo)
            janela.destroy()
            messagebox.showinfo("Sucesso", "Cadastrado!")
        tk.Button(janela, text="Salvar", command=salvar, font=self.fonte_destaque, bg=self.cor_botao, fg=self.cor_texto_botao, width=15).pack(pady=15)

    def janela_editar_pessoa(self, tipo):
        lista = self.lista_pessoas_reg if tipo == "regular" else self.lista_pessoas_treino
        sel = lista.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione uma pessoa!")
            return
        valores = lista.item(sel[0], "values")
        funcao_atual, nome_atual, disp_atual = valores[0], valores[1], valores[2]
        janela = tk.Toplevel(self.root)
        janela.title("Editar Pessoa")
        janela.geometry("420x300")
        janela.configure(bg="#f0f4f8")
        janela.resizable(False, False)
        tk.Label(janela, text="Nome:", font=self.fonte_destaque, bg="#f0f4f8").pack(pady=6)
        nome = tk.Entry(janela, font=self.fonte, width=45)
        nome.insert(0, nome_atual)
        nome.pack()
        tk.Label(janela, text="Função:", font=self.fonte_destaque, bg="#f0f4f8").pack(pady=6)
        funcao = tk.Entry(janela, font=self.fonte, width=45)
        funcao.insert(0, funcao_atual)
        funcao.pack()
        tk.Label(janela, text="Dias Disponíveis:", font=self.fonte_destaque, bg="#f0f4f8").pack(pady=6)
        dias = tk.Entry(janela, font=self.fonte, width=45)
        dias.insert(0, disp_atual)
        dias.pack()
        def salvar():
            arquivo = ARQUIVO_PESSOAS_REGULARES if tipo == "regular" else ARQUIVO_PESSOAS_TREINAMENTO
            pessoas = carregar_dados(arquivo, {})
            f_ant = funcao_atual.lower()
            f_novo = funcao.get().strip().lower()
            if f_ant in pessoas:
                for i, p in enumerate(pessoas[f_ant]):
                    if p["nome"] == nome_atual:
                        if f_novo != f_ant:
                            pessoas.setdefault(f_novo, []).append({
                                "nome": nome.get().strip().title(),
                                "disponibilidade": dias.get().strip().lower(),
                                "escalas_mes": p.get("escalas_mes", 0)
                            })
                            pessoas[f_ant].pop(i)
                            if not pessoas[f_ant]:
                                del pessoas[f_ant]
                        else:
                            p["nome"] = nome.get().strip().title()
                            p["disponibilidade"] = dias.get().strip().lower()
                        break
            salvar_dados(arquivo, pessoas)
            self.carregar_pessoas(tipo)
            janela.destroy()
            messagebox.showinfo("Sucesso", "Atualizado!")
        tk.Button(janela, text="Salvar Alterações", command=salvar, font=self.fonte_destaque, bg=self.cor_botao, fg=self.cor_texto_botao, width=18).pack(pady=15)

    def excluir_pessoa(self, tipo):
        lista = self.lista_pessoas_reg if tipo == "regular" else self.lista_pessoas_treino
        sel = lista.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione uma pessoa!")
            return
        valores = lista.item(sel[0], "values")
        funcao, nome = valores[0].lower(), valores[1]
        if messagebox.askyesno("Confirmar", f"Excluir {nome} da função {valores[0]}?"):
            arquivo = ARQUIVO_PESSOAS_REGULARES if tipo == "regular" else ARQUIVO_PESSOAS_TREINAMENTO
            pessoas = carregar_dados(arquivo, {})
            if funcao in pessoas:
                pessoas[funcao] = [p for p in pessoas[funcao] if p["nome"] != nome]
                if not pessoas[funcao]:
                    del pessoas[funcao]
                salvar_dados(arquivo, pessoas)
                self.carregar_pessoas(tipo)
                messagebox.showinfo("Excluído", "Pessoa removida!")

    def janela_gerar(self, tipo):
        janela = tk.Toplevel(self.root)
        janela.title(f"Gerar Escala - {'Regular' if tipo == 'regular' else 'Treinamento'}")
        janela.geometry("450x220")
        janela.configure(bg="#f0f4f8")
        janela.resizable(False, False)
        data_var = tk.StringVar()
        dia_var = tk.StringVar()
        def escolher_data(data_str, dia_str):
            data_var.set(data_str)
            dia_var.set(dia_str)
        ttk.Label(janela, text="Data do Culto:", font=self.fonte_destaque).pack(pady=8)
        frame_data = ttk.Frame(janela)
        frame_data.pack()
        ttk.Entry(frame_data, textvariable=data_var, width=15, font=self.fonte).pack(side="left", padx=5)
        ttk.Button(frame_data, text="📅 Escolher", command=lambda: CalendarioPopup(janela, escolher_data), style="Botao.TButton").pack(side="left")
        ttk.Label(janela, text="Dia da Semana:", font=self.fonte_destaque).pack(pady=8)
        ttk.Entry(janela, textvariable=dia_var, width=25, font=self.fonte, state="readonly").pack()
        def confirmar():
            if not data_var.get() or not dia_var.get():
                messagebox.showwarning("Aviso", "Escolha uma data!")
                return
            self.criar_escala(tipo, data_var.get(), dia_var.get())
            janela.destroy()
        ttk.Button(janela, text="Continuar", command=confirmar, style="Botao.TButton").pack(pady=15)

    def criar_escala(self, tipo, data, dia):
        arquivo = ARQUIVO_ESCALAS_REGULARES if tipo == "regular" else ARQUIVO_ESCALAS_TREINAMENTO
        escalas = carregar_dados(arquivo, {})
        if data in escalas:
            messagebox.showwarning("Aviso", "Já existe uma escala para essa data!")
            return
        janela = tk.Toplevel(self.root)
        janela.title(f"Preencher Escala - {data}")
        janela.geometry("500x550")
        janela.configure(bg="#f0f4f8")
        pessoas = carregar_dados(ARQUIVO_PESSOAS_REGULARES if tipo == "regular" else ARQUIVO_PESSOAS_TREINAMENTO, {})
        entradas = {}
        canvas_esc = tk.Canvas(janela, bg="#f0f4f8")
        scroll = ttk.Scrollbar(janela, orient="vertical", command=canvas_esc.yview)
        frame_esc = ttk.Frame(canvas_esc)
        frame_esc.bind("<Configure>", lambda e: canvas_esc.configure(scrollregion=canvas_esc.bbox("all")))
        canvas_esc.create_window((0,0), window=frame_esc, anchor="nw")
        canvas_esc.configure(yscrollcommand=scroll.set)
        canvas_esc.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        ttk.Label(frame_esc, text=f"Escala: {dia.upper()} - {data}", font=self.fonte_destaque).pack(pady=10)
        for funcao, lista_pessoas in pessoas.items():
            frame_linha = ttk.Frame(frame_esc)
            frame_linha.pack(fill="x", padx=15, pady=5)
            ttk.Label(frame_linha, text=f"{funcao.upper()}:", width=18, font=self.fonte).pack(side="left")
            nomes = [p["nome"] for p in lista_pessoas]
            cb = ttk.Combobox(frame_linha, values=nomes, width=35, font=self.fonte, state="readonly")
            cb.pack(side="left")
            entradas[funcao] = cb
        def salvar():
            servicos = {}
            for funcao, campo in entradas.items():
                if campo.get():
                    servicos[funcao] = campo.get()
            if not servicos:
                messagebox.showwarning("Aviso", "Preencha pelo menos uma função!")
                return
               # Atualiza contagem de escalas das pessoas
            arquivo_pessoas = ARQUIVO_PESSOAS_REGULARES if tipo == "regular" else ARQUIVO_PESSOAS_TREINAMENTO
            dados_pessoas = carregar_dados(arquivo_pessoas, {})
            for funcao, nome in servicos.items():
                if funcao in dados_pessoas:
                    for pessoa in dados_pessoas[funcao]:
                        if pessoa["nome"] == nome:
                            pessoa["escalas_mes"] = pessoa.get("escalas_mes", 0) + 1
                            break
            salvar_dados(arquivo_pessoas, dados_pessoas)

            # Salva a escala
            escalas[data] = {
                "dia": dia,
                "servicos": servicos
            }
            salvar_dados(arquivo, escalas)

            self.carregar_escalas(tipo)
            self.carregar_pessoas(tipo)
            janela.destroy()
            messagebox.showinfo("Sucesso", "Escala criada com sucesso!")

        ttk.Button(frame_esc, text="💾 Salvar Escala", command=salvar, style="Botao.TButton").pack(pady=20)

    def janela_ver_editar(self, tipo):
        lista = self.lista_esc_reg if tipo == "regular" else self.lista_esc_treino
        sel = lista.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione uma escala!")
            return
        valores = lista.item(sel[0], "values")
        data_esc = valores[0]
        status = valores[2]
        if status == "🔒 Bloqueada":
            messagebox.showinfo("Acesso Negado", "Essa escala já passou do prazo de edição!")
            return

        arquivo = ARQUIVO_ESCALAS_REGULARES if tipo == "regular" else ARQUIVO_ESCALAS_TREINAMENTO
        escalas = carregar_dados(arquivo, {})
        if data_esc not in escalas:
            messagebox.showerror("Erro", "Escala não encontrada!")
            return

        dados_escala = escalas[data_esc]
        janela = tk.Toplevel(self.root)
        janela.title(f"Editar Escala - {data_esc}")
        janela.geometry("520x580")
        janela.configure(bg="#f0f4f8")

        pessoas = carregar_dados(ARQUIVO_PESSOAS_REGULARES if tipo == "regular" else ARQUIVO_PESSOAS_TREINAMENTO, {})
        entradas = {}

        canvas_esc = tk.Canvas(janela, bg="#f0f4f8")
        scroll = ttk.Scrollbar(janela, orient="vertical", command=canvas_esc.yview)
        frame_esc = ttk.Frame(canvas_esc)
        frame_esc.bind("<Configure>", lambda e: canvas_esc.configure(scrollregion=canvas_esc.bbox("all")))
        canvas_esc.create_window((0, 0), window=frame_esc, anchor="nw")
        canvas_esc.configure(yscrollcommand=scroll.set)
        canvas_esc.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        ttk.Label(frame_esc, text=f"Editar: {dados_escala['dia'].upper()} - {data_esc}",
                  font=self.fonte_destaque).pack(pady=12)

        for funcao, lista_pessoas in pessoas.items():
            frame_linha = ttk.Frame(frame_esc)
            frame_linha.pack(fill="x", padx=15, pady=6)
            ttk.Label(frame_linha, text=f"{funcao.upper()}:", width=20, font=self.fonte).pack(side="left")
            nomes = [p["nome"] for p in lista_pessoas]
            cb = ttk.Combobox(frame_linha, values=nomes, width=38, font=self.fonte, state="readonly")
            cb.set(dados_escala["servicos"].get(funcao, ""))
            cb.pack(side="left")
            entradas[funcao] = cb

        def salvar_alteracoes():
            novos_servicos = {}
            for funcao, campo in entradas.items():
                if campo.get():
                    novos_servicos[funcao] = campo.get()

            if not novos_servicos:
                messagebox.showwarning("Aviso", "Mantenha pelo menos uma função preenchida!")
                return

            # Zera contagem antiga e recalcula
            arquivo_pessoas = ARQUIVO_PESSOAS_REGULARES if tipo == "regular" else ARQUIVO_PESSOAS_TREINAMENTO
            dados_pessoas = carregar_dados(arquivo_pessoas, {})

            # Remove a contagem anterior
            for funcao, nome_antigo in dados_escala["servicos"].items():
                if funcao in dados_pessoas:
                    for p in dados_pessoas[funcao]:
                        if p["nome"] == nome_antigo:
                            p["escalas_mes"] = max(0, p.get("escalas_mes", 1) - 1)
                            break

            # Adiciona nova contagem
            for funcao, nome_novo in novos_servicos.items():
                if funcao in dados_pessoas:
                    for p in dados_pessoas[funcao]:
                        if p["nome"] == nome_novo:
                            p["escalas_mes"] = p.get("escalas_mes", 0) + 1
                            break

            salvar_dados(arquivo_pessoas, dados_pessoas)

            # Atualiza a escala
            escalas[data_esc]["servicos"] = novos_servicos
            salvar_dados(arquivo, escalas)

            self.carregar_escalas(tipo)
            self.carregar_pessoas(tipo)
            janela.destroy()
            messagebox.showinfo("Sucesso", "Escala atualizada!")

        def exportar_pdf():
            try:
                caminho = os.path.join(pasta_export, f"Escala_{data_esc.replace('/', '-')}.pdf")
                c = canvas.Canvas(caminho, pagesize=A4)
                largura, altura = A4

                c.setFont("Helvetica-Bold", 14)
                c.drawCenteredString(largura/2, altura - 2*cm, self.config["nome_igreja"])
                c.setFont("Helvetica", 11)
                c.drawCenteredString(largura/2, altura - 3*cm, self.config["endereco_igreja"])
                c.setFont("Helvetica-Bold", 12)
                c.drawCenteredString(largura/2, altura - 4.5*cm, f"ESCALA - {dados_escala['dia'].upper()} - {data_esc}")

                y = altura - 7*cm
                c.setFont("Helvetica", 11)
                for funcao, nome in novos_servicos.items():
                    c.drawString(3*cm, y, f"{funcao.upper()}:")
                    c.drawString(7*cm, y, nome)
                    y -= 0.8*cm

                c.setFont("Helvetica-Oblique", 9)
                c.drawString(3*cm, 2*cm, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
                c.save()
                messagebox.showinfo("Exportado", f"PDF salvo em:\n{caminho}")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível gerar PDF: {e}")

        def exportar_excel():
            try:
                caminho = os.path.join(pasta_export, f"Escala_{data_esc.replace('/', '-')}.xlsx")
                wb = Workbook()
                ws = wb.active
                ws.title = "Escala"
                ws.append(["Função", "Responsável"])
                for funcao, nome in dados_escala["servicos"].items():
                    ws.append([funcao.upper(), nome])
                wb.save(caminho)
                messagebox.showinfo("Exportado", f"Planilha salva em:\n{caminho}")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível gerar Excel: {e}")

        frame_botoes = ttk.Frame(frame_esc)
        frame_botoes.pack(pady=20)
        ttk.Button(frame_botoes, text="💾 Salvar Alterações", command=salvar_alteracoes, style="Botao.TButton").grid(row=0, column=0, padx=8)
        ttk.Button(frame_botoes, text="📄 Exportar PDF", command=exportar_pdf, style="Botao.TButton").grid(row=0, column=1, padx=8)
        ttk.Button(frame_botoes, text="📊 Exportar Excel", command=exportar_excel, style="Botao.TButton").grid(row=0, column=2, padx=8)

    def excluir_escala(self, tipo):
        lista = self.lista_esc_reg if tipo == "regular" else self.lista_esc_treino
        sel = lista.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione uma escala!")
            return
        valores = lista.item(sel[0], "values")
        data_esc = valores[0]

        if not messagebox.askyesno("Confirmar Exclusão", f"Deseja excluir a escala do dia {data_esc}?\nEssa ação não pode ser desfeita!"):
            return

        arquivo = ARQUIVO_ESCALAS_REGULARES if tipo == "regular" else ARQUIVO_ESCALAS_TREINAMENTO
        escalas = carregar_dados(arquivo, {})
        if data_esc not in escalas:
            messagebox.showerror("Erro", "Escala não encontrada!")
            return

        # Devolve a contagem de escalas
        arquivo_pessoas = ARQUIVO_PESSOAS_REGULARES if tipo == "regular" else ARQUIVO_PESSOAS_TREINAMENTO
        dados_pessoas = carregar_dados(arquivo_pessoas, {})
        for funcao, nome in escalas[data_esc]["servicos"].items():
            if funcao in dados_pessoas:
                for p in dados_pessoas[funcao]:
                    if p["nome"] == nome:
                        p["escalas_mes"] = max(0, p.get("escalas_mes", 1) - 1)
                        break
        salvar_dados(arquivo_pessoas, dados_pessoas)

        # Remove a escala
        del escalas[data_esc]
        salvar_dados(arquivo, escalas)

        self.carregar_escalas(tipo)
        self.carregar_pessoas(tipo)
        messagebox.showinfo("Excluído", "Escala removida com sucesso!")

# ----------------------
# INICIALIZAÇÃO DO SISTEMA
# ----------------------
if __name__ == "__main__":
    # Verifica se as bibliotecas de exportação estão instaladas
    try:
        import reportlab
        import openpyxl
    except ImportError:
        print("Instalando bibliotecas necessárias...")
        import subprocess
        subprocess.check_call(["pip", "install", "reportlab", "openpyxl"])
        print("Instalação concluída! Reinicie o programa.")
        exit()

    root = tk.Tk()
    app = SistemaEscalas(root)
    root.mainloop()

