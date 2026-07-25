import json
import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import datetime, timedelta
import urllib.request

# ----------------------
# CONFIGURAÇÕES DE VERSÃO E ATUALIZAÇÃO
# ----------------------
VERSAO_ATUAL = "1.0.2"
URL_VERSAO = "https://raw.githubusercontent.com/Edsonlima-sudo/atualizacao-escalas/main/versao.json"
URL_ARQUIVO = "https://raw.githubusercontent.com/Edsonlima-sudo/atualizacao-escalas/main/escalas_igreja.py"

# ----------------------
# PASTAS E ARQUIVOS DE DADOS
# ----------------------
pasta_dados = os.path.join(os.path.expanduser("~"), "Documentos", "SistemaEscalas")
os.makedirs(pasta_dados, exist_ok=True)

ARQUIVO_CONFIG = os.path.join(pasta_dados, "config.json")
ARQUIVO_PESSOAS_REGULARES = os.path.join(pasta_dados, "pessoas_regulares.json")
ARQUIVO_PESSOAS_ORACAO = os.path.join(pasta_dados, "pessoas_oracao.json")
ARQUIVO_PESSOAS_LOUVORES = os.path.join(pasta_dados, "pessoas_louvores.json")
ARQUIVO_PESSOAS_TREINAMENTO = os.path.join(pasta_dados, "pessoas_treinamento.json")

ARQUIVO_ESCALAS_REGULARES = os.path.join(pasta_dados, "escalas_regulares.json")
ARQUIVO_ESCALAS_ORACAO = os.path.join(pasta_dados, "escalas_oracao.json")
ARQUIVO_ESCALAS_LOUVORES = os.path.join(pasta_dados, "escalas_louvores.json")
ARQUIVO_ESCALAS_TREINAMENTO = os.path.join(pasta_dados, "escalas_treinamento.json")

CONFIG_PADRAO = {"senha": "igreja123"}

# ----------------------
# FUNÇÕES DE ATUALIZAÇÃO
# ----------------------
def verificar_atualizacao():
    try:
        resposta = urllib.request.urlopen(URL_VERSAO, timeout=5)
        dados = json.loads(resposta.read().decode("utf-8"))
        versao_nova = dados.get("versao", "0.0.0")
        if versao_nova > VERSAO_ATUAL:
            if messagebox.askyesno("Atualização Disponível",
                f"Versão {versao_nova} disponível!\nDeseja atualizar agora?"):
                baixar_e_atualizar()
    except Exception as e:
        pass  # Sem erro se sem internet

def baixar_e_atualizar():
    try:
        caminho_atual = os.path.abspath(sys.argv[0])
        caminho_backup = caminho_atual + ".bak"
        shutil.copy2(caminho_atual, caminho_backup)  # Backup de segurança
        urllib.request.urlretrieve(URL_ARQUIVO, caminho_atual)
        messagebox.showinfo("Sucesso", "Atualizado! Reiniciando...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        messagebox.showerror("Erro", f"Falha na atualização: {str(e)}")

# ----------------------
# FUNÇÕES DE DADOS
# ----------------------
def carregar_dados(arquivo):
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)
            return dados if isinstance(dados, list) else []
    except:
        return []

def salvar_dados(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def carregar_escalas(arquivo):
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)
            return dados if isinstance(dados, dict) else {}
    except:
        return {}

def salvar_escalas(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def data_para_dia_semana(data_str):
    dias = ["domingo", "segunda", "terça", "quarta", "quinta", "sexta", "sábado"]
    try: return dias[datetime.strptime(data_str, "%d/%m/%Y").weekday()]
    except: return ""

# ----------------------
# CALENDÁRIO
# ----------------------
class CalendarioPopup(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Escolher Data")
        self.geometry("300x300")
        self.data_atual = datetime.now()
        self.transient(parent)
        self.grab_set()

        cab = ttk.Frame(self)
        cab.pack(pady=5)
        ttk.Button(cab, text="<", command=self.ant).grid(row=0, column=0)
        self.lbl = ttk.Label(cab, text="", font=("Arial", 11, "bold"))
        self.lbl.grid(row=0, column=1, padx=10)
        ttk.Button(cab, text=">", command=self.prox).grid(row=0, column=2)

        cab_dias = ttk.Frame(self)
        cab_dias.pack()
        for c, d in enumerate(["Dom","Seg","Ter","Qua","Qui","Sex","Sáb"]):
            ttk.Label(cab_dias, text=d, width=4).grid(row=0, column=c)

        self.grade = ttk.Frame(self)
        self.grade.pack()
        self.atualizar()

    def ant(self): self.data_atual = (self.data_atual.replace(day=1)-timedelta(days=1)); self.atualizar()
    def prox(self): self.data_atual = (self.data_atual.replace(day=28)+timedelta(days=4)).replace(day=1); self.atualizar()
    def atualizar(self):
        for w in self.grade.winfo_children(): w.destroy()
        meses = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
        self.lbl.config(text=f"{meses[self.data_atual.month-1]} {self.data_atual.year}")
        pri = self.data_atual.replace(day=1)
        ult = (pri.replace(month=pri.month%12+1,day=1)-timedelta(days=1))
        inicio = (pri.weekday()+1)%7
        dia=1
        for l in range(6):
            for c in range(7):
                if l==0 and c<inicio: ttk.Label(self.grade,text="",width=4).grid(row=l,column=c)
                elif dia<=ult.day:
                    dte = self.data_atual.replace(day=dia)
                    ttk.Button(self.grade,text=str(dia),width=4,command=lambda d=dte: self.escolher(d)).grid(row=l,column=c)
                    dia+=1
                else: ttk.Label(self.grade,text="",width=4).grid(row=l,column=c)
    def escolher(self, dt):
        self.callback(dt.strftime("%d/%m/%Y"), data_para_dia_semana(dt.strftime("%d/%m/%Y")))
        self.destroy()

# ----------------------
# RELATÓRIO
# ----------------------
def gerar_escala():
    reg = carregar_escalas(ARQUIVO_ESCALAS_REGULARES)
    ora = carregar_escalas(ARQUIVO_ESCALAS_ORACAO)
    lou = carregar_escalas(ARQUIVO_ESCALAS_LOUVORES)
    tre = carregar_escalas(ARQUIVO_ESCALAS_TREINAMENTO)
    hoje = datetime.now()
    texto = f"ESCALA — {hoje.month}/{hoje.year}\n\n"

    def add(dados, tit):
        nonlocal texto
        for dt, inf in dados.items():
            serv = inf.get("servicos", {})
            linhas = [f"{f}: {n}" for f,n in serv.items() if n]
            texto += f"{tit} — {dt} ({inf.get('dia','')})\n"
            texto += "\n".join(linhas) + "\n\n" if linhas else "Sem pessoas\n\n"

    add(ora, "🙏 SEMANA DE ORAÇÃO")
    add(reg, "📅 ESCALA REGULAR")
    add(lou, "🎵 LOUVORES")
    add(tre, "🎓 TREINAMENTO")

    jan = tk.Toplevel(); jan.title("Escala Completa"); jan.geometry("500x600")
    txt = tk.Text(jan, font=("Arial",11)); txt.insert("1.0", texto); txt.config(state="disabled")
    txt.pack(fill="both", expand=True)

# ----------------------
# SISTEMA PRINCIPAL
# ----------------------
class App:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Sistema de Escalas - v{VERSAO_ATUAL}")
        self.root.geometry("900x650")
        self.config = carregar_dados(ARQUIVO_CONFIG)
        if not self.config:
            self.config = CONFIG_PADRAO
            salvar_dados(ARQUIVO_CONFIG, self.config)

        if not self.verificar_senha():
            root.quit()
            return

        # Verifica atualização ao abrir
        verificar_atualizacao()

        # Menu com atualização
        menu = tk.Menu(root)
        menu_ajuda = tk.Menu(menu, tearoff=0)
        menu_ajuda.add_command(label="Verificar Atualizações", command=verificar_atualizacao)
        menu.add_cascade(label="Ajuda", menu=menu_ajuda)
        root.config(menu=menu)

        self.abas = ttk.Notebook(root)
        self.abas.pack(fill="both", expand=True, padx=10, pady=10)

        # ✅ Todas as 4 áreas
        self.criar_aba("oracao", "🙏 Semana de Oração", ARQUIVO_PESSOAS_ORACAO, ARQUIVO_ESCALAS_ORACAO)
        self.criar_aba("regulares", "👥 Escalas Regulares", ARQUIVO_PESSOAS_REGULARES, ARQUIVO_ESCALAS_REGULARES)
        self.criar_aba("louvores", "🎵 Louvores", ARQUIVO_PESSOAS_LOUVORES, ARQUIVO_ESCALAS_LOUVORES)
        self.criar_aba("treinamento", "🎓 Treinamento", ARQUIVO_PESSOAS_TREINAMENTO, ARQUIVO_ESCALAS_TREINAMENTO)

        ttk.Button(root, text="📄 Gerar Escala Completa", command=gerar_escala).pack(pady=10)

    def verificar_senha(self):
        senha = simpledialog.askstring("Acesso", "Digite a Senha:", show="*")
        return senha == self.config.get("senha", "igreja123")

    def criar_aba(self, cod, titulo, arq_pessoas, arq_escalas):
        frame = ttk.Frame(self.abas)
        self.abas.add(frame, text=titulo)

        ttk.Label(frame, text="Pessoas Cadastradas:", font=("Arial",11,"bold")).pack(pady=5)
        lista_p = ttk.Treeview(frame, columns=("Função","Nome","Dias"), show="headings", height=5)
        lista_p.heading("Função", text="Função")
        lista_p.heading("Nome", text="Nome")
        lista_p.heading("Dias", text="Dias")
        lista_p.pack(fill="x", padx=5)

        ttk.Label(frame, text="Escalas:", font=("Arial",11,"bold")).pack(pady=10)
        lista_e = ttk.Treeview(frame, columns=("Data","Dia"), show="headings")
        lista_e.heading("Data", text="Data")
        lista_e.heading("Dia", text="Dia da Semana")
        lista_e.pack(fill="both", expand=True, padx=5, pady=5)

        def carregar():
            lista_p.delete(*lista_p.get_children())
            pessoas = carregar_dados(arq_pessoas)
            for p in pessoas:
                if isinstance(p, dict) and all(k in p for k in ["funcao","nome","dias"]):
                    lista_p.insert("", "end", values=(p["funcao"], p["nome"], p["dias"]))
            lista_e.delete(*lista_e.get_children())
            esc = carregar_escalas(arq_escalas)
            for dt, inf in esc.items():
                lista_e.insert("", "end", values=(dt, inf.get("dia","")))

        def cadastrar():
            jan = tk.Toplevel(self.root)
            jan.title("Cadastrar Pessoa")
            jan.geometry("300x200")
            n = ttk.Entry(jan); f = ttk.Entry(jan); d = ttk.Entry(jan)
            ttk.Label(jan, text="Nome:").pack(); n.pack(padx=10)
            ttk.Label(jan, text="Função:").pack(); f.pack(padx=10)
            ttk.Label(jan, text="Dias:").pack(); d.pack(padx=10)
            n.focus()

            def salvar(event=None):
                if not n.get().strip() or not f.get().strip() or not d.get().strip():
                    messagebox.showwarning("Aviso", "Preencha todos os campos!")
                    return
                pessoas = carregar_dados(arq_pessoas)
                pessoas.append({"nome":n.get().strip(),"funcao":f.get().strip(),"dias":d.get().strip()})
                salvar_dados(arq_pessoas, pessoas)
                jan.destroy(); carregar(); messagebox.showinfo("OK", "Cadastrado!")

            n.bind("<Return>", salvar); f.bind("<Return>", salvar); d.bind("<Return>", salvar); jan.bind("<Return>", salvar)
            ttk.Button(jan, text="Salvar", command=salvar).pack(pady=10)

        def nova_escala():
            def criar(data, dia):
                esc = carregar_escalas(arq_escalas)
                if data not in esc:
                    esc[data] = {"dia": dia, "servicos": {}}
                    salvar_escalas(arq_escalas, esc)
                    carregar()
                else:
                    messagebox.showinfo("Aviso", "Já existe!")
            CalendarioPopup(self.root, criar)

        def editar_escala():
            sel = lista_e.selection()
            if not sel: return
            data = lista_e.item(sel[0])["values"][0]
            esc = carregar_escalas(arq_escalas)
            info = esc.get(data, {})
            pessoas = carregar_dados(arq_pessoas)
            funcoes = sorted({p["funcao"] for p in pessoas if isinstance(p, dict) and "funcao" in p})

            jan = tk.Toplevel(self.root)
            jan.title("Editar Escala")
            campos = {}
            for i, fun in enumerate(funcoes):
                ttk.Label(jan, text=fun+":").grid(row=i, column=0, padx=5, pady=3, sticky="e")
                e = ttk.Entry(jan)
                e.insert(0, info.get("servicos", {}).get(fun, ""))
                e.grid(row=i, column=1, padx=5, pady=3)
                campos[fun] = e

            def salvar(event=None):
                info.setdefault("servicos", {})
                for fun, ent in campos.items():
                    val = ent.get().strip()
                    if val: info["servicos"][fun] = val
                    elif fun in info["servicos"]: del info["servicos"][fun]
                esc[data] = info
                salvar_escalas(arq_escalas, esc)
                jan.destroy(); carregar(); messagebox.showinfo("OK", "Atualizado!")

            jan.bind("<Return>", salvar)
            ttk.Button(jan, text="Salvar", command=salvar).grid(row=len(funcoes)+1, column=0, columnspan=2, pady=10)

        botoes = ttk.Frame(frame)
        botoes.pack(fill="x", pady=5)
        ttk.Button(botoes, text="Cadastrar Pessoa", command=cadastrar).pack(side="left", padx=2)
        ttk.Button(botoes, text="Nova Escala", command=nova_escala).pack(side="left", padx=2)
        ttk.Button(botoes, text="Editar Escala", command=editar_escala).pack(side="left", padx=2)

        carregar()

if __name__ == "__main__":
    import shutil
    root = tk.Tk()
    app = App(root)
    root.mainloop()
