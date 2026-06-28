if __name__ == "__main__":
    try:
        import Atualizador
    except ImportError:
        pass
    
import random

import json

import os

import shutil

from datetime import datetime, timedelta

import tkinter as tk

from tkinter import ttk, messagebox, simpledialog, filedialog



# ----------------------

# ATUALIZAÇÃO AUTOMÁTICA INTEGRADA

# ----------------------

import os

import subprocess

import tkinter as tk

from tkinter import messagebox



URL_VERSAO = "https://raw.githubusercontent.com/Edsonlima-sudo/atualizacao-escalas/main/versao.json"

URL_ARQUIVO = "https://raw.githubusercontent.com/Edsonlima-sudo/atualizacao-escalas/main/escalas_igreja.py"

VERSAO_ATUAL = "1.0.2"  # ⚠️ Atualize esse número a cada nova versão



def verificar_atualizacao():

    # Instala o requests se não existir

    try:

        import requests

    except ImportError:

        try:

            subprocess.check_call(["pip", "install", "--user", "requests"])

            import requests

        except Exception as e:

            return f"⚠️ Não foi possível instalar dependência: {str(e)}"



    try:

        # Busca a versão mais recente

        resp = requests.get(URL_VERSAO, timeout=15)

        resp.raise_for_status()

        dados = resp.json()

        nova_versao = dados.get("versao", "0.0.0.3")



        if nova_versao == VERSAO_ATUAL:

            return "✅ Já está na versão mais recente!"



        # Pergunta ao usuário

        janela_temp = tk.Tk()

        janela_temp.withdraw()

        if not messagebox.askyesno("Atualização Disponível",

            f"Versão atual: {VERSAO_ATUAL}\nNova: {nova_versao}\n\nDeseja baixar agora?"):

            return "Atualização adiada."



        # Baixa o arquivo

        resp = requests.get(URL_ARQUIVO, timeout=30)

        resp.raise_for_status()



        # Salva na MESMA pasta do programa (agora em C:\01IGREJAS, sem OneDrive)

        caminho_pasta = os.path.dirname(os.path.abspath(__file__))

        nome_novo = os.path.join(caminho_pasta, f"escalas_igreja_v{nova_versao.replace('.','_')}.py")

        with open(nome_novo, "w", encoding="utf-8") as f:

            f.write(resp.text)



        messagebox.showinfo("Concluído",

            f"Nova versão salva em:\n{nome_novo}\n\nAbra esse arquivo para usar a versão nova.")

        return "✅ Atualização concluída!"



    except Exception as e:

        return f"❌ Erro na verificação: {str(e)}"



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

ARQUIVO_PESSOAS_ORACAO = os.path.join(pasta_dados, "pessoas_oracao.json")

ARQUIVO_PESSOAS_LOUVORES = os.path.join(pasta_dados, "pessoas_louvores.json")



ARQUIVO_ESCALAS_REGULARES = os.path.join(pasta_dados, "escalas_regulares.json")

ARQUIVO_ESCALAS_TREINAMENTO = os.path.join(pasta_dados, "escalas_treinamento.json")

ARQUIVO_ESCALAS_ORACAO = os.path.join(pasta_dados, "escalas_oracao.json")

ARQUIVO_ESCALAS_LOUVORES = os.path.join(pasta_dados, "escalas_louvores.json")



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

                ARQUIVO_PESSOAS_ORACAO, ARQUIVO_PESSOAS_LOUVORES,

                ARQUIVO_ESCALAS_REGULARES, ARQUIVO_ESCALAS_TREINAMENTO,

                ARQUIVO_ESCALAS_ORACAO, ARQUIVO_ESCALAS_LOUVORES, ARQUIVO_CONFIG]:

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

# FUNÇÃO DE EXPORTAR ESCALA

# ----------------------

def gerar_escala_formatada(dados, mes=None, ano=None):

    meses = [

        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",

        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"

    ]

    hoje = datetime.now()

    mes = mes or hoje.month

    ano = ano or hoje.year

    nome_mes = meses[mes - 1]



    texto = f"ESCALA PARA O MÊS DE {nome_mes.upper()} {ano}\n\n"

    for tipo, itens in dados.items():

        if not itens:

            continue

        texto += f"{tipo.upper()}\n"

        itens_ordenados = sorted(itens, key=lambda x: datetime.strptime(x[0], "%d/%m/%Y"))

        for data, nome in itens_ordenados:

            texto += f"{data} {nome}\n"

        texto += "\n"

    return texto.strip()



def exibir_e_salvar_escala(dados, mes=None, ano=None):

    texto = gerar_escala_formatada(dados, mes, ano)

    janela = tk.Toplevel()

    janela.title("Escala do Mês")

    janela.geometry("520x680")

    janela.resizable(False, False)

    area_texto = tk.Text(janela, font=("Arial", 14), padx=25, pady=25, wrap="word")

    area_texto.pack(fill="both", expand=True)

    area_texto.insert("1.0", texto)

    area_texto.config(state="disabled")

    def salvar():

        caminho = filedialog.asksaveasfilename(

            defaultextension=".txt",

            filetypes=[("Arquivo de Texto", "*.txt")],

            initialfile=f"Escala_{mes or datetime.now().month}_{ano or datetime.now().year}",

            title="Salvar escala"

        )

        if caminho:

            try:

                with open(caminho, "w", encoding="utf-8") as f:

                    f.write(texto)

                messagebox.showinfo("Concluído", f"Escala salva em:\n{caminho}")

            except Exception as e:

                messagebox.showerror("Erro", f"Não foi possível salvar:\n{str(e)}")

    ttk.Button(janela, text="💾 Salvar Arquivo", command=salvar).pack(pady=10)



def gerar_escala_do_sistema(mes=None, ano=None):

    esc_reg = carregar_dados(ARQUIVO_ESCALAS_REGULARES, {})

    esc_treino = carregar_dados(ARQUIVO_ESCALAS_TREINAMENTO, {})

    esc_oracao = carregar_dados(ARQUIVO_ESCALAS_ORACAO, {})

    esc_louvores = carregar_dados(ARQUIVO_ESCALAS_LOUVORES, {})

    dados_formatados = {}



    for data, info in esc_reg.items():

        try:

            d = datetime.strptime(data, "%d/%m/%Y")

            if mes and ano:

                if d.month != mes or d.year != ano:

                    continue

            dia = info["dia"].lower()

            if dia == "domingo":

                secao = "ESCOLA DOMINICAL" if "dominical" in info.get("tipo", "") else "ESCALA PARA DOMINGO A NOITE"

            elif dia == "quarta":

                secao = "ESCALAS PARA QUARTA FEIRA"

            else:

                secao = f"ESCALA PARA {dia.upper()}"

            nomes = " e ".join(info["servicos"].values())

            dados_formatados.setdefault(secao, []).append((data, nomes))

        except:

            continue



    for data, info in esc_treino.items():

        try:

            d = datetime.strptime(data, "%d/%m/%Y")

            if mes and ano:

                if d.month != mes or d.year != ano:

                    continue

            dia = info["dia"].lower()

            secao = f"TREINAMENTO - {dia.upper()}"

            nomes = " e ".join(info["servicos"].values())

            dados_formatados.setdefault(secao, []).append((data, nomes))

        except:

            continue



    for data, info in esc_oracao.items():

        try:

            d = datetime.strptime(data, "%d/%m/%Y")

            if mes and ano:

                if d.month != mes or d.year != ano:

                    continue

            dia = info["dia"].lower()

            secao = f"SEMANA DE ORAÇÃO - {dia.upper()}"

            nomes = " e ".join(info["servicos"].values())

            dados_formatados.setdefault(secao, []).append((data, nomes))

        except:

            continue



    for data, info in esc_louvores.items():

        try:

            d = datetime.strptime(data, "%d/%m/%Y")

            if mes and ano:

                if d.month != mes or d.year != ano:

                    continue

            dia = info["dia"].lower()

            secao = f"LOUVORES E ADORAÇÃO - {dia.upper()}"

            nomes = " e ".join(info["servicos"].values())

            dados_formatados.setdefault(secao, []).append((data, nomes))

        except:

            continue



    exibir_e_salvar_escala(dados_formatados, mes, ano)



# ----------------------

# CLASSE PRINCIPAL

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



        self.config = carregar_dados(ARQUIVO_CONFIG, CONFIG_PADRAO)

        salvar_dados(ARQUIVO_CONFIG, self.config)



        if not self.verificar_senha():

            self.root.quit()

            return



        self.frame_menu = ttk.Frame(self.root)

        self.frame_menu.pack(fill="x", padx=10, pady=5)



        self.criar_menu()



        ttk.Button(

            self.frame_menu,

            text="📋 Gerar Escala do Mês",

            command=gerar_escala_do_sistema

        ).pack(side="left", padx=5)



        self.criar_abas()

        self.carregar_tudo()



    def verificar_senha(self):

        senha = simpledialog.askstring("Acesso ao Sistema", "Digite a senha de acesso:", show="*")

        return senha == self.config["senha"]



    def criar_menu(self):

        menu_bar = tk.Menu(self.root)

        menu_config = tk.Menu(menu_bar, tearoff=0)

        menu_config.add_command(label="Alterar Senha", command=self.janela_alterar_senha)

        menu_config.add_command(label="Definir Limite de Escalas/Mês", command=self.janela_ajustar_limite)

        menu_config.add_command(label="Definir Dias para Bloquear Edição", command=self.janela_ajustar_bloqueio)

        menu_config.add_separator()

        menu_config.add_command(label="Dados da Igreja", command=self.janela_editar_dados_igreja)

        menu_bar.add_cascade(label="⚙️ Configurações", menu=menu_config)



        menu_relatorios = tk.Menu(menu_bar, tearoff=0)

        menu_relatorios.add_command(label="Escalas por Pessoa", command=self.janela_relatorio_pessoas)

        menu_relatorios.add_command(label="Escalas por Função", command=self.janela_relatorio_funcoes)

        menu_relatorios.add_command(label="Escalas por Período", command=self.janela_relatorio_periodo)

        menu_bar.add_cascade(label="📊 Relatórios", menu=menu_relatorios)



        menu_ferramentas = tk.Menu(menu_bar, tearoff=0)

        menu_ferramentas.add_command(label="Criar Backup dos Dados", command=criar_backup)

        menu_bar.add_cascade(label="🛠️ Ferramentas", menu=menu_ferramentas)



        self.root.config(menu=menu_bar)



    def criar_abas(self):

        self.abas = ttk.Notebook(self.root)

        self.abas.pack(fill="both", expand=True, padx=8, pady=8)



        # ===== ABA 1: PESSOAS REGULARES =====

        self.aba_pessoas_reg = ttk.Frame(self.abas)

        self.abas.add(self.aba_pessoas_reg, text="👥 Pessoas Regulares")

        frame_botoes_reg = ttk.Frame(self.aba_pessoas_reg)

        frame_botoes_reg.pack(fill="x", padx=5, pady=5)

        ttk.Button(frame_botoes_reg, text="Cadastrar", command=lambda: self.janela_cadastrar("regular")).pack(side="left", padx=3)

        ttk.Button(frame_botoes_reg, text="Editar", command=lambda: self.janela_editar_pessoa("regular")).pack(side="left", padx=3)

        ttk.Button(frame_botoes_reg, text="Excluir", command=lambda: self.excluir_pessoa("regular")).pack(side="left", padx=3)

        ttk.Label(frame_botoes_reg, text="🔍 Pesquisar:").pack(side="left", padx=10)

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



        # ===== ABA 2: PESSOAS TREINAMENTO =====

        self.aba_pessoas_treino = ttk.Frame(self.abas)

        self.abas.add(self.aba_pessoas_treino, text="🎓 Pessoas Treinamento")

        frame_botoes_treino = ttk.Frame(self.aba_pessoas_treino)

        frame_botoes_treino.pack(fill="x", padx=5, pady=5)

        ttk.Button(frame_botoes_treino, text="Cadastrar", command=lambda: self.janela_cadastrar("treinamento")).pack(side="left", padx=3)

        ttk.Button(frame_botoes_treino, text="Editar", command=lambda: self.janela_editar_pessoa("treinamento")).pack(side="left", padx=3)

        ttk.Button(frame_botoes_treino, text="Excluir", command=lambda: self.excluir_pessoa("treinamento")).pack(side="left", padx=3)

        ttk.Label(frame_botoes_treino, text="🔍 Pesquisar:").pack(side="left", padx=10)

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



        # ===== ABA 3: PESSOAS SEMANA DE ORAÇÃO =====

        self.aba_pessoas_oracao = ttk.Frame(self.abas)

        self.abas.add(self.aba_pessoas_oracao, text="🙏 Semana de Oração")

        frame_botoes_oracao = ttk.Frame(self.aba_pessoas_oracao)

        frame_botoes_oracao.pack(fill="x", padx=5, pady=5)

        ttk.Button(frame_botoes_oracao, text="Cadastrar", command=lambda: self.janela_cadastrar("oracao")).pack(side="left", padx=3)

        ttk.Button(frame_botoes_oracao, text="Editar", command=lambda: self.janela_editar_pessoa("oracao")).pack(side="left", padx=3)

        ttk.Button(frame_botoes_oracao, text="Excluir", command=lambda: self.excluir_pessoa("oracao")).pack(side="left", padx=3)

        ttk.Label(frame_botoes_oracao, text="🔍 Pesquisar:").pack(side="left", padx=10)

        self.busca_oracao = ttk.Entry(frame_botoes_oracao, width=30)

        self.busca_oracao.pack(side="left")

        self.busca_oracao.bind("<KeyRelease>", lambda e: self.filtrar_pessoas("oracao"))

        self.lista_pessoas_oracao = ttk.Treeview(self.aba_pessoas_oracao, columns=("Função", "Nome", "Disponibilidade", "Escalas Mês"), show="headings")

        self.lista_pessoas_oracao.heading("Função", text="Função")

        self.lista_pessoas_oracao.heading("Nome", text="Nome")

        self.lista_pessoas_oracao.heading("Disponibilidade", text="Dias Disponíveis")

        self.lista_pessoas_oracao.heading("Escalas Mês", text="Escalas / Mês")

        self.lista_pessoas_oracao.column("Função", width=140)

        self.lista_pessoas_oracao.column("Nome", width=260)

        self.lista_pessoas_oracao.column("Disponibilidade", width=240)

        self.lista_pessoas_oracao.column("Escalas Mês", width=120, anchor="center")

        self.lista_pessoas_oracao.pack(fill="both", expand=True, padx=5, pady=5)



        # ===== ABA 4: PESSOAS LOUVORES =====

        self.aba_pessoas_louvores = ttk.Frame(self.abas)

        self.abas.add(self.aba_pessoas_louvores, text="🎵 Louvores e Adoração")

        frame_botoes_louvores = ttk.Frame(self.aba_pessoas_louvores)

        frame_botoes_louvores.pack(fill="x", padx=5, pady=5)

        ttk.Button(frame_botoes_louvores, text="Cadastrar", command=lambda: self.janela_cadastrar("louvores")).pack(side="left", padx=3)

        ttk.Button(frame_botoes_louvores, text="Editar", command=lambda: self.janela_editar_pessoa("louvores")).pack(side="left", padx=3)

        ttk.Button(frame_botoes_louvores, text="Excluir", command=lambda: self.excluir_pessoa("louvores")).pack(side="left", padx=3)

        ttk.Label(frame_botoes_louvores, text="🔍 Pesquisar:").pack(side="left", padx=10)

        self.busca_louvores = ttk.Entry(frame_botoes_louvores, width=30)

        self.busca_louvores.pack(side="left")

        self.busca_louvores.bind("<KeyRelease>", lambda e: self.filtrar_pessoas("louvores"))

        self.lista_pessoas_louvores = ttk.Treeview(self.aba_pessoas_louvores, columns=("Função", "Nome", "Disponibilidade", "Escalas Mês"), show="headings")

        self.lista_pessoas_louvores.heading("Função", text="Função")

        self.lista_pessoas_louvores.heading("Nome", text="Nome")

        self.lista_pessoas_louvores.heading("Disponibilidade", text="Dias Disponíveis")

        self.lista_pessoas_louvores.heading("Escalas Mês", text="Escalas / Mês")

        self.lista_pessoas_louvores.column("Função", width=140)

        self.lista_pessoas_louvores.column("Nome", width=260)

        self.lista_pessoas_louvores.column("Disponibilidade", width=240)

        self.lista_pessoas_louvores.column("Escalas Mês", width=120, anchor="center")

        self.lista_pessoas_louvores.pack(fill="both", expand=True, padx=5, pady=5)



        # ===== ABA 5: ESCALAS REGULARES =====

        self.aba_esc_reg = ttk.Frame(self.abas)

        self.abas.add(self.aba_esc_reg, text="🗓️ Escalas Regulares")

        frame_esc_reg = ttk.Frame(self.aba_esc_reg)

        frame_esc_reg.pack(fill="x", padx=5, pady=5)

        ttk.Button(frame_esc_reg, text="Gerar Escala", command=lambda: self.janela_gerar("regular")).pack(side="left", padx=3)

        ttk.Button(frame_esc_reg, text="Ver / Editar", command=lambda: self.janela_ver_editar("regular")).pack(side="left", padx=3)

        ttk.Button(frame_esc_reg, text="Excluir", command=lambda: self.excluir_escala("regular")).pack(side="left", padx=3)

        ttk.Label(frame_esc_reg, text="🔍 Pesquisar:").pack(side="left", padx=10)

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



        # ===== ABA 6: ESCALAS TREINAMENTO =====

        self.aba_esc_treino = ttk.Frame(self.abas)

        self.abas.add(self.aba_esc_treino, text="🎓 Escalas de Treinamento")

        frame_esc_treino = ttk.Frame(self.aba_esc_treino)

        frame_esc_treino.pack(fill="x", padx=5, pady=5)

        ttk.Button(frame_esc_treino, text="Gerar Escala", command=lambda: self.janela_gerar("treinamento")).pack(side="left", padx=3)

        ttk.Button(frame_esc_treino, text="Ver / Editar", command=lambda: self.janela_ver_editar("treinamento")).pack(side="left", padx=3)

        ttk.Button(frame_esc_treino, text="Excluir", command=lambda: self.excluir_escala("treinamento")).pack(side="left", padx=3)

        ttk.Label(frame_esc_treino, text="🔍 Pesquisar:").pack(side="left", padx=10)

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



        # ===== ABA 7: ESCALAS SEMANA DE ORAÇÃO =====

        self.aba_esc_oracao = ttk.Frame(self.abas)

        self.abas.add(self.aba_esc_oracao, text="🙏 Escalas Oração")

        frame_esc_oracao = ttk.Frame(self.aba_esc_oracao)

        frame_esc_oracao.pack(fill="x", padx=5, pady=5)

        ttk.Button(frame_esc_oracao, text="Gerar Escala", command=lambda: self.janela_gerar("oracao")).pack(side="left", padx=3)

        ttk.Button(frame_esc_oracao, text="Ver / Editar", command=lambda: self.janela_ver_editar("oracao")).pack(side="left", padx=3)

        ttk.Button(frame_esc_oracao, text="Excluir", command=lambda: self.excluir_escala("oracao")).pack(side="left", padx=3)

        ttk.Label(frame_esc_oracao, text="🔍 Pesquisar:").pack(side="left", padx=10)

        self.busca_esc_oracao = ttk.Entry(frame_esc_oracao, width=30)

        self.busca_esc_oracao.pack(side="left")

        self.busca_esc_oracao.bind("<KeyRelease>", lambda e: self.filtrar_escalas("oracao"))

        self.lista_esc_oracao = ttk.Treeview(self.aba_esc_oracao, columns=("Data", "Dia", "Status"), show="headings")

        self.lista_esc_oracao.heading("Data", text="Data")

        self.lista_esc_oracao.heading("Dia", text="Dia da Semana")

        self.lista_esc_oracao.heading("Status", text="Edição")

        self.lista_esc_oracao.column("Data", width=120)

        self.lista_esc_oracao.column("Dia", width=250)

        self.lista_esc_oracao.column("Status", width=120, anchor="center")

        self.lista_esc_oracao.pack(fill="both", expand=True, padx=5, pady=5)



        # ===== ABA 8: ESCALAS LOUVORES =====

        self.aba_esc_louvores = ttk.Frame(self.abas)

        self.abas.add(self.aba_esc_louvores, text="🎵 Escalas Louvores")

        frame_esc_louvores = ttk.Frame(self.aba_esc_louvores)

        frame_esc_louvores.pack(fill="x", padx=5, pady=5)

        ttk.Button(frame_esc_louvores, text="Gerar Escala", command=lambda: self.janela_gerar("louvores")).pack(side="left", padx=3)

        ttk.Button(frame_esc_louvores, text="Ver / Editar", command=lambda: self.janela_ver_editar("louvores")).pack(side="left", padx=3)

        ttk.Button(frame_esc_louvores, text="Excluir", command=lambda: self.excluir_escala("louvores")).pack(side="left", padx=3)

        ttk.Label(frame_esc_louvores, text="🔍 Pesquisar:").pack(side="left", padx=10)

        self.busca_esc_louvores = ttk.Entry(frame_esc_louvores, width=30)

        self.busca_esc_louvores.pack(side="left")

        self.busca_esc_louvores.bind("<KeyRelease>", lambda e: self.filtrar_escalas("louvores"))

        self.lista_esc_louvores = ttk.Treeview(self.aba_esc_louvores, columns=("Data", "Dia", "Status"), show="headings")

        self.lista_esc_louvores.heading("Data", text="Data")

        self.lista_esc_louvores.heading("Dia", text="Dia da Semana")

        self.lista_esc_louvores.heading("Status", text="Edição")

        self.lista_esc_louvores.column("Data", width=120)

        self.lista_esc_louvores.column("Dia", width=250)

        self.lista_esc_louvores.column("Status", width=120, anchor="center")

        self.lista_esc_louvores.pack(fill="both", expand=True, padx=5, pady=5)



    # --- DEMAIS FUNÇÕES (MANTIDAS E ADAPTADAS) ---

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

        ttk.Button(janela, text="Salvar", command=salvar).pack(pady=15)



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

                for tipo in ["regular", "treinamento", "oracao", "louvores"]:

                    self.carregar_pessoas(tipo)

                janela.destroy()

            except:

                messagebox.showerror("Erro", "Digite um número válido maior que zero!")

        ttk.Button(janela, text="Salvar", command=salvar).pack(pady=10)



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

                for tipo in ["regular", "treinamento", "oracao", "louvores"]:

                    self.carregar_escalas(tipo)

                janela.destroy()

            except:

                messagebox.showerror("Erro", "Digite um número válido!")

        ttk.Button(janela, text="Salvar", command=salvar).pack(pady=10)



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

        ttk.Button(janela, text="Salvar", command=salvar).pack(pady=15)



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

        tree = ttk.Treeview(janela, columns=("Nome", "Função", "Categoria", "Escalas", "Status"), show="headings")

        tree.heading("Nome", text="Nome")

        tree.heading("Função", text="Função")

        tree.heading("Categoria", text="Categoria")

        tree.heading("Escalas", text="Número de Escalas")

        tree.heading("Status", text="Status")

        tree.column("Nome", width=220)

        tree.column("Função", width=180)

        tree.column("Categoria", width=160)

        tree.column("Escalas", width=120, anchor="center")

        tree.column("Status", width=150, anchor="center")

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        def gerar():

            tree.delete(*tree.get_children())

            try:

                m, a = mes_ano.get().split("/")

                mes = int(m)

                ano = int(a)

            except:

                messagebox.showerror("Erro", "Formato inválido! Use: MM/AAAA")

                return

            limite = self.config["limite_escalas_mes"]

            dados = [

                ("Regular", ARQUIVO_PESSOAS_REGULARES),

                ("Treinamento", ARQUIVO_PESSOAS_TREINAMENTO),

                ("Semana Oração", ARQUIVO_PESSOAS_ORACAO),

                ("Louvores", ARQUIVO_PESSOAS_LOUVORES)

            ]

            for cat, arq in dados:

                pessoas = carregar_dados(arq, {})

                for funcao, lista in pessoas.items():

                    for p in lista:

                        qtd = p.get("escalas_mes", 0)

                        status = "✅ Normal" if qtd < limite else "⚠️ Limite atingido"

                        tree.insert("", "end", values=(p["nome"], funcao.upper(), cat, qtd, status))

        ttk.Button(frame_top, text="Gerar Relatório", command=gerar).pack(side="left", padx=10)



    def janela_relatorio_funcoes(self):

        janela = tk.Toplevel(self.root)

        janela.title("Relatório por Função")

        janela.geometry("600x450")

        tree = ttk.Treeview(janela, columns=("Função", "Total de Escalas"), show="headings")

        tree.heading("Função", text="Função")

        tree.heading("Total de Escalas", text="Quantidade")

        tree.column("Função", width=350)

        tree.column("Total de Escalas", width=150, anchor="center")

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        arquivos_esc = [ARQUIVO_ESCALAS_REGULARES, ARQUIVO_ESCALAS_TREINAMENTO,

                        ARQUIVO_ESCALAS_ORACAO, ARQUIVO_ESCALAS_LOUVORES]

        contagem = {}

        for arq in arquivos_esc:

            esc = carregar_dados(arq, {})

            for e in esc.values():

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

        tree = ttk.Treeview(janela, columns=("Data", "Dia", "Tipo de Escala"), show="headings")

        tree.heading("Data", text="Data")

        tree.heading("Dia", text="Dia da Semana")

        tree.heading("Tipo de Escala", text="Tipo")

        tree.column("Data", width=120)

        tree.column("Dia", width=250)

        tree.column("Tipo de Escala", width=300)

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        def gerar():

            tree.delete(*tree.get_children())

            try:

                di = datetime.strptime(data_ini.get(), "%d/%m/%Y")

                df = datetime.strptime(data_fim.get(), "%d/%m/%Y")

            except:

                messagebox.showerror("Erro", "Datas inválidas! Use DD/MM/AAAA")

                return

            lista_esc = [

                (ARQUIVO_ESCALAS_REGULARES, "Escala Regular"),

                (ARQUIVO_ESCALAS_TREINAMENTO, "Escala Treinamento"),

                (ARQUIVO_ESCALAS_ORACAO, "Semana de Oração"),

                (ARQUIVO_ESCALAS_LOUVORES, "Louvores e Adoração")

            ]

            for arq, nome_tipo in lista_esc:

                esc = carregar_dados(arq, {})

                for d, info in esc.items():

                    try:

                        data_esc = datetime.strptime(d, "%d/%m/%Y")

                        if di <= data_esc <= df:

                            tree.insert("", "end", values=(d, info["dia"].capitalize(), nome_tipo))

                    except:

                        continue

        ttk.Button(frame, text="Gerar", command=gerar).grid(row=0, column=4, padx=10)



    def carregar_tudo(self):

        for tipo in ["regular", "treinamento", "oracao", "louvores"]:

            self.carregar_pessoas(tipo)

            self.carregar_escalas(tipo)



    def carregar_pessoas(self, tipo):

        mapa = {

            "regular": (self.lista_pessoas_reg, ARQUIVO_PESSOAS_REGULARES),

            "treinamento": (self.lista_pessoas_treino, ARQUIVO_PESSOAS_TREINAMENTO),

            "oracao": (self.lista_pessoas_oracao, ARQUIVO_PESSOAS_ORACAO),

            "louvores": (self.lista_pessoas_louvores, ARQUIVO_PESSOAS_LOUVORES)

        }

        lista, arq = mapa[tipo]

        lista.delete(*lista.get_children())

        pessoas = carregar_dados(arq, {})

        limite = self.config["limite_escalas_mes"]

        for funcao, itens in pessoas.items():

            for p in itens:

                qtd = p.get("escalas_mes", 0)

                lista.insert("", "end", values=(funcao.upper(), p["nome"], p["disponibilidade"].capitalize(), f"{qtd} / {limite}"))



    def filtrar_pessoas(self, tipo, evento=None):

        mapa = {

            "regular": (self.busca_reg, self.lista_pessoas_reg, ARQUIVO_PESSOAS_REGULARES),

            "treinamento": (self.busca_treino, self.lista_pessoas_treino, ARQUIVO_PESSOAS_TREINAMENTO),

            "oracao": (self.busca_oracao, self.lista_pessoas_oracao, ARQUIVO_PESSOAS_ORACAO),

            "louvores": (self.busca_louvores, self.lista_pessoas_louvores, ARQUIVO_PESSOAS_LOUVORES)

        }

        entrada, lista, arq = mapa[tipo]

        termo = entrada.get().strip().lower()

        lista.delete(*lista.get_children())

        pessoas = carregar_dados(arq, {})

        limite = self.config["limite_escalas_mes"]

        for funcao, itens in pessoas.items():

            for p in itens:

                if termo in p["nome"].lower() or termo in funcao.lower():

                    qtd = p.get("escalas_mes", 0)

                    lista.insert("", "end", values=(funcao.upper(), p["nome"], p["disponibilidade"].capitalize(), f"{qtd} / {limite}"))



    def carregar_escalas(self, tipo):

        mapa = {

            "regular": (self.lista_esc_reg, ARQUIVO_ESCALAS_REGULARES),

            "treinamento": (self.lista_esc_treino, ARQUIVO_ESCALAS_TREINAMENTO),

            "oracao": (self.lista_esc_oracao, ARQUIVO_ESCALAS_ORACAO),

            "louvores": (self.lista_esc_louvores, ARQUIVO_ESCALAS_LOUVORES)

        }

        lista, arq = mapa[tipo]

        lista.delete(*lista.get_children())

        escalas = carregar_dados(arq, {})

        dias_bloquear = self.config["dias_bloquear_edicao"]

        for data, info in sorted(escalas.items(), reverse=True):

            status = "🔒 Bloqueada" if not pode_editar_escala(data, dias_bloquear) else "✏️ Editar"

            lista.insert("", "end", values=(data, info["dia"].capitalize(), status))



    def filtrar_escalas(self, tipo, evento=None):

        mapa = {

            "regular": (self.busca_esc_reg, self.lista_esc_reg, ARQUIVO_ESCALAS_REGULARES),

            "treinamento": (self.busca_esc_treino, self.lista_esc_treino, ARQUIVO_ESCALAS_TREINAMENTO),

            "oracao": (self.busca_esc_oracao, self.lista_esc_oracao, ARQUIVO_ESCALAS_ORACAO),

            "louvores": (self.busca_esc_louvores, self.lista_esc_louvores, ARQUIVO_ESCALAS_LOUVORES)

        }

        entrada, lista, arq = mapa[tipo]

        termo = entrada.get().strip().lower()

        lista.delete(*lista.get_children())

        escalas = carregar_dados(arq, {})

        dias_bloquear = self.config["dias_bloquear_edicao"]

        for data, info in escalas.items():

            if termo in data or termo in info["dia"].lower():

                status = "🔒 Bloqueada" if not pode_editar_escala(data, dias_bloquear) else "✏️ Editar"

                lista.insert("", "end", values=(data, info["dia"].capitalize(), status))



    def janela_cadastrar(self, tipo):

        mapa_arq = {

            "regular": ARQUIVO_PESSOAS_REGULARES,

            "treinamento": ARQUIVO_PESSOAS_TREINAMENTO,

            "oracao": ARQUIVO_PESSOAS_ORACAO,

            "louvores": ARQUIVO_PESSOAS_LOUVORES

        }

        titulos = {

            "regular": "Cadastrar Pessoa Regular",

            "treinamento": "Cadastrar Pessoa Treinamento",

            "oracao": "Cadastrar - Semana de Oração",

            "louvores": "Cadastrar - Louvores e Adoração"

        }

        janela = tk.Toplevel(self.root)

        janela.title(titulos[tipo])

        janela.geometry("420x300")

        janela.resizable(False, False)

        janela.configure(bg="#f0f4f8")

        ttk.Label(janela, text="Nome Completo:", font=self.fonte_destaque).pack(pady=6)

        nome = ttk.Entry(janela, width=45)

        nome.pack()

        ttk.Label(janela, text="Função / Cargo:", font=self.fonte_destaque).pack(pady=6)

        funcao = ttk.Entry(janela, width=45)

        funcao.pack()

        ttk.Label(janela, text="Dias disponíveis (ex: domingo, quarta):", font=self.fonte_destaque).pack(pady=6)

        dias = ttk.Entry(janela, width=45)

        dias.pack()

        def salvar():

            if not nome.get().strip() or not funcao.get().strip() or not dias.get().strip():

                messagebox.showwarning("Aviso", "Preencha todos os campos!")

                return

            arq = mapa_arq[tipo]

            pessoas = carregar_dados(arq, {})

            f = funcao.get().strip().lower()

            pessoas.setdefault(f, []).append({

                "nome": nome.get().strip().title(),

                "disponibilidade": dias.get().strip().lower(),

                "escalas_mes": 0

            })

            salvar_dados(arq, pessoas)

            self.carregar_pessoas(tipo)

            janela.destroy()

            messagebox.showinfo("Sucesso", "Cadastro realizado!")

        ttk.Button(janela, text="Salvar Cadastro", command=salvar).pack(pady=15)



    def janela_editar_pessoa(self, tipo):

        mapa_lista = {

            "regular": self.lista_pessoas_reg,

            "treinamento": self.lista_pessoas_treino,

            "oracao": self.lista_pessoas_oracao,

            "louvores": self.lista_pessoas_louvores

        }

        mapa_arq = {

            "regular": ARQUIVO_PESSOAS_REGULARES,

            "treinamento": ARQUIVO_PESSOAS_TREINAMENTO,

            "oracao": ARQUIVO_PESSOAS_ORACAO,

            "louvores": ARQUIVO_PESSOAS_LOUVORES

        }

        lista = mapa_lista[tipo]

        sel = lista.selection()

        if not sel:

            messagebox.showwarning("Aviso", "Selecione uma pessoa na lista!")

            return

        valores = lista.item(sel[0], "values")

        funcao_atual, nome_atual, disp_atual = valores[0], valores[1], valores[2]

        janela = tk.Toplevel(self.root)

        janela.title("Editar Dados da Pessoa")

        janela.geometry("420x300")

        janela.resizable(False, False)

        janela.configure(bg="#f0f4f8")

        ttk.Label(janela, text="Nome Completo:", font=self.fonte_destaque).pack(pady=6)

        nome = ttk.Entry(janela, width=45)

        nome.insert(0, nome_atual)

        nome.pack()

        ttk.Label(janela, text="Função / Cargo:", font=self.fonte_destaque).pack(pady=6)

        funcao = ttk.Entry(janela, width=45)

        funcao.insert(0, funcao_atual)

        funcao.pack()

        ttk.Label(janela, text="Dias disponíveis:", font=self.fonte_destaque).pack(pady=6)

        dias = ttk.Entry(janela, width=45)

        dias.insert(0, disp_atual)

        dias.pack()

        def salvar():

            arq = mapa_arq[tipo]

            pessoas = carregar_dados(arq, {})

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

            salvar_dados(arq, pessoas)

            self.carregar_pessoas(tipo)

            janela.destroy()

            messagebox.showinfo("Sucesso", "Dados atualizados!")

        ttk.Button(janela, text="Salvar Alterações", command=salvar).pack(pady=15)



    def excluir_pessoa(self, tipo):

        mapa_lista = {

            "regular": self.lista_pessoas_reg,

            "treinamento": self.lista_pessoas_treino,

            "oracao": self.lista_pessoas_oracao,

            "louvores": self.lista_pessoas_louvores

        }

        mapa_arq = {

            "regular": ARQUIVO_PESSOAS_REGULARES,

            "treinamento": ARQUIVO_PESSOAS_TREINAMENTO,

            "oracao": ARQUIVO_PESSOAS_ORACAO,

            "louvores": ARQUIVO_PESSOAS_LOUVORES

        }

        lista = mapa_lista[tipo]

        sel = lista.selection()

        if not sel:

            messagebox.showwarning("Aviso", "Selecione uma pessoa para excluir!")

            return

        valores = lista.item(sel[0], "values")

        funcao_atual, nome_atual = valores[0], valores[1]

        if not messagebox.askyesno("Confirmação", f"Deseja realmente excluir:\n{nome_atual} ({funcao_atual})?"):

            return

        arq = mapa_arq[tipo]

        pessoas = carregar_dados(arq, {})

        f_ant = funcao_atual.lower()

        if f_ant in pessoas:

            for i, p in enumerate(pessoas[f_ant]):

                if p["nome"] == nome_atual:

                    pessoas[f_ant].pop(i)

                    if not pessoas[f_ant]:

                        del pessoas[f_ant]

                    break

            salvar_dados(arq, pessoas)

            self.carregar_pessoas(tipo)

            messagebox.showinfo("Sucesso", "Pessoa excluída!")



    def definir_data(self, data_str, dia_str):

        self.entry_data.delete(0, tk.END)

        self.entry_data.insert(0, data_str)

        self.combo_dia.set(dia_str.title())



    def janela_gerar(self, tipo):

        mapa_arq = {

            "regular": ARQUIVO_ESCALAS_REGULARES,

            "treinamento": ARQUIVO_ESCALAS_TREINAMENTO,

            "oracao": ARQUIVO_ESCALAS_ORACAO,

            "louvores": ARQUIVO_ESCALAS_LOUVORES

        }

        titulos = {

            "regular": "Gerar Escala Regular",

            "treinamento": "Gerar Escala Treinamento",

            "oracao": "Gerar Escala - Semana de Oração",

            "louvores": "Gerar Escala - Louvores"

        }

        janela = tk.Toplevel(self.root)

        janela.title(titulos[tipo])

        janela.geometry("450x300")

        janela.resizable(False, False)

        janela.configure(bg="#f0f4f8")



        ttk.Label(janela, text="Data da Escala:", font=self.fonte_destaque).pack(pady=10)

        frame_data = ttk.Frame(janela)

        frame_data.pack()

        self.entry_data = ttk.Entry(frame_data, width=15, font=self.fonte)

        self.entry_data.pack(side="left", padx=5)

        ttk.Button(frame_data, text="📅", command=lambda: CalendarioPopup(janela, self.definir_data)).pack(side="left")



        ttk.Label(janela, text="Dia da Semana:", font=self.fonte_destaque).pack(pady=10)

        self.combo_dia = ttk.Combobox(janela, values=["Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"], state="readonly", font=self.fonte)

        self.combo_dia.pack(pady=5)



        if tipo == "regular":

            ttk.Label(janela, text="Tipo de Escala:", font=self.fonte_destaque).pack(pady=10)

            self.combo_tipo = ttk.Combobox(janela, values=["Escola Dominical", "Culto Noite", "Reunião Quarta", "Outro"], state="readonly", font=self.fonte)

            self.combo_tipo.pack(pady=5)

        else:

            self.combo_tipo = None



        def confirmar():

            data = self.entry_data.get().strip()

            dia = self.combo_dia.get().strip()

            if not data or not dia:

                messagebox.showwarning("Aviso", "Preencha data e dia da semana!")

                return

            try:

                datetime.strptime(data, "%d/%m/%Y")

            except:

                messagebox.showerror("Erro", "Data inválida! Use DD/MM/AAAA")

                return

            arq = mapa_arq[tipo]

            escalas = carregar_dados(arq, {})

            if data in escalas:

                if not messagebox.askyesno("Já existe", "Já há escala para essa data. Deseja substituir?"):

                    return

            escalas[data] = {

                "dia": dia.lower(),

                "tipo": self.combo_tipo.get().strip().lower() if self.combo_tipo else tipo,

                "servicos": {}

            }

            salvar_dados(arq, escalas)

            self.carregar_escalas(tipo)

            janela.destroy()

            messagebox.showinfo("Sucesso", "Escala criada! Agora use 'Ver / Editar' para preencher os nomes.")



        ttk.Button(janela, text="✅ Criar Escala", command=confirmar).pack(pady=15)



    def janela_ver_editar(self, tipo):

        mapa_lista = {

            "regular": self.lista_esc_reg,

            "treinamento": self.lista_esc_treino,

            "oracao": self.lista_esc_oracao,

            "louvores": self.lista_esc_louvores

        }

        mapa_arq = {

            "regular": ARQUIVO_ESCALAS_REGULARES,

            "treinamento": ARQUIVO_ESCALAS_TREINAMENTO,

            "oracao": ARQUIVO_ESCALAS_ORACAO,

            "louvores": ARQUIVO_ESCALAS_LOUVORES

        }

        mapa_funcoes = {

            "regular": ["Dirigente", "Pregador", "Leitor", "Oração", "Músico", "Diácono"],

            "treinamento": ["Estagiário 1", "Estagiário 2", "Auxiliar"],

            "oracao": ["Coordenador", "Líder Oração", "Leitor Bíblico", "Intercessor"],

            "louvores": ["Cantor", "Instrumentista", "Regente", "Técnico Som"]

        }

        lista = mapa_lista[tipo]

        arq = mapa_arq[tipo]

        sel = lista.selection()

        if not sel:

            messagebox.showwarning("Aviso", "Selecione uma escala na lista!")

            return

        valores = lista.item(sel[0], "values")

        data_esc = valores[0]

        if not pode_editar_escala(data_esc, self.config["dias_bloquear_edicao"]):

            messagebox.showerror("Bloqueado", "Essa escala já passou do limite de edição!")

            return

        escalas = carregar_dados(arq, {})

        info = escalas.get(data_esc, {})

        janela = tk.Toplevel(self.root)

        janela.title(f"Editar Escala - {data_esc}")

        janela.geometry("500x400")

        janela.resizable(False, False)

        janela.configure(bg="#f0f4f8")

        ttk.Label(janela, text=f"Data: {data_esc} | Dia: {info.get('dia','').capitalize()}", font=self.fonte_destaque).pack(pady=10)

        frame_campos = ttk.Frame(janela)

        frame_campos.pack(pady=10, padx=15, fill="x")

        campos = []

        funcoes_padrao = mapa_funcoes[tipo]

        for i, funcao in enumerate(funcoes_padrao):

            ttk.Label(frame_campos, text=f"{funcao}:", font=self.fonte).grid(row=i, column=0, sticky="w", pady=5)

            entrada = ttk.Entry(frame_campos, width=35, font=self.fonte)

            entrada.insert(0, info.get("servicos", {}).get(funcao.lower(), ""))

            entrada.grid(row=i, column=1, padx=10, pady=5)

            campos.append( (funcao.lower(), entrada) )

        def salvar():

            for funcao, entrada in campos:

                valor = entrada.get().strip()

                if valor:

                    escalas[data_esc]["servicos"][funcao] = valor

                elif funcao in escalas[data_esc]["servicos"]:

                    del escalas[data_esc]["servicos"][funcao]

            salvar_dados(arq, escalas)

            self.carregar_escalas(tipo)

            janela.destroy()

            messagebox.showinfo("Sucesso", "Escala atualizada!")

        ttk.Button(janela, text="💾 Salvar Alterações", command=salvar).pack(pady=15)



    def excluir_escala(self, tipo):

        mapa_lista = {

            "regular": self.lista_esc_reg,

            "treinamento": self.lista_esc_treino,

            "oracao": self.lista_esc_oracao,

            "louvores": self.lista_esc_louvores

        }

        mapa_arq = {

            "regular": ARQUIVO_ESCALAS_REGULARES,

            "treinamento": ARQUIVO_ESCALAS_TREINAMENTO,

            "oracao": ARQUIVO_ESCALAS_ORACAO,

            "louvores": ARQUIVO_ESCALAS_LOUVORES

        }

        lista = mapa_lista[tipo]

        arq = mapa_arq[tipo]

        sel = lista.selection()

        if not sel:

            messagebox.showwarning("Aviso", "Selecione uma escala para excluir!")

            return

        valores = lista.item(sel[0], "values")

        data_esc = valores[0]

        if not messagebox.askyesno("Confirmação", f"Deseja excluir a escala do dia {data_esc}?"):

            return

        escalas = carregar_dados(arq, {})

        if data_esc in escalas:

            del escalas[data_esc]

            salvar_dados(arq, escalas)

            self.carregar_escalas(tipo)

            messagebox.showinfo("Sucesso", "Escala excluída!")



# ----------------------

# INICIALIZAÇÃO FINAL

# ----------------------

if __name__ == "__main__":
    resultado = verificar_atualizacao()
    print(resultado)

    root = tk.Tk()
    app = SistemaEscalas(root)
    root.mainloop()


