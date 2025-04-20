import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
from datetime import datetime

# Bibliotecas para gráficos
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ARQUIVO_DADOS = 'data.json'

# ---------------- Funções de dados ----------------

def carregar_dados():
    if not os.path.exists(ARQUIVO_DADOS):
        return {"disciplinas": {}}
    try:
        with open(ARQUIVO_DADOS, 'r') as f:
            conteudo = f.read().strip()
            if not conteudo:
                return {"disciplinas": {}}
            return json.loads(conteudo)
    except json.JSONDecodeError:
        return {"disciplinas": {}}

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, 'w') as f:
        json.dump(dados, f, indent=4)

dados = carregar_dados()

# ---------------- Interface Gráfica ----------------

class OrganizadorEstudosApp:
    def __init__(self, master):
        self.master = master
        master.title("Organizador de Estudos")

        self.frame = tk.Frame(master, padx=20, pady=20)
        self.frame.pack()

        tk.Label(self.frame, text="Organizador de Estudos", font=("Arial", 16, "bold")).pack(pady=10)

        # Estado do modo (Dark ou Light)
        self.dark_mode = True  # Iniciar com Dark Mode

        # Cores para Dark e Light Mode
        self.cores = {
            "dark": {
                "bg": "#2b2b2b",
                "fg": "#f2f2f2",
                "button_bg": "#444444",
                "button_active": "#666666"
            },
            "light": {
                "bg": "#ffffff",
                "fg": "#000000",
                "button_bg": "#e0e0e0",
                "button_active": "#d0d0d0"
            }
        }

        # Botão de alternância de tema
        self.toggle_btn = tk.Button(self.frame, text="🌙 Dark Mode", command=self.toggle_tema)
        self.toggle_btn.pack(anchor="ne")

        botoes = [
            ("Adicionar Disciplina", self.adicionar_disciplina),
            ("Adicionar Meta", self.adicionar_meta),
            ("Registrar Sessão", self.registrar_sessao),
            ("Visualizar Progresso", self.visualizar_progresso),
            ("Marcar Meta como Concluída", self.marcar_meta_concluida),
            ("📈 Ver Gráficos de Progresso", self.mostrar_graficos),
        ]

        for texto, comando in botoes:
            tk.Button(self.frame, text=texto, width=30, command=comando).pack(pady=5)

        self.aplicar_tema()  # Aplica o tema inicial

    # Função para aplicar o tema (Dark ou Light)
    def aplicar_tema(self, widget=None):
        if widget is None:
            widget = self.master

        tema = "dark" if self.dark_mode else "light"
        cores = self.cores[tema]

        widget.configure(bg=cores["bg"])

        for child in widget.winfo_children():
            if isinstance(child, tk.Button):
                child.configure(bg=cores["button_bg"], fg=cores["fg"],
                                activebackground=cores["button_active"],
                                activeforeground=cores["fg"])
            elif isinstance(child, (tk.Label, tk.LabelFrame)):
                child.configure(bg=cores["bg"], fg=cores["fg"])
            elif isinstance(child, tk.Frame):
                child.configure(bg=cores["bg"])
            self.aplicar_tema(child)

    # Função para alternar entre Dark Mode e Light Mode
    def toggle_tema(self):
        self.dark_mode = not self.dark_mode
        self.toggle_btn.config(text="☀️ Light Mode" if not self.dark_mode else "🌙 Dark Mode")
        self.aplicar_tema()

    # Função para escolher disciplina
    def escolher_disciplina(self, prompt="Escolha uma disciplina:"):
        if not dados["disciplinas"]:
            messagebox.showinfo("Info", "Nenhuma disciplina cadastrada.")
            return None
        return simpledialog.askstring("Disciplina", prompt + "\n" + "\n".join(dados["disciplinas"].keys()))

    # Adicionar nova disciplina
    def adicionar_disciplina(self):
        nome = simpledialog.askstring("Adicionar Disciplina", "Nome da nova disciplina:")
        if nome:
            if nome in dados["disciplinas"]:
                messagebox.showerror("Erro", "Essa disciplina já existe.")
            else:
                dados["disciplinas"][nome] = {"metas": [], "sessoes": []}
                salvar_dados(dados)
                messagebox.showinfo("Sucesso", f"Disciplina '{nome}' adicionada.")

    # Adicionar uma meta a uma disciplina
    def adicionar_meta(self):
        nome = self.escolher_disciplina("Para qual disciplina deseja adicionar uma meta?")
        if not nome or nome not in dados["disciplinas"]:
            return
        meta = simpledialog.askstring("Nova Meta", "Descreva a meta:")
        if meta:
            dados["disciplinas"][nome]["metas"].append({"descricao": meta, "concluida": False})
            salvar_dados(dados)
            messagebox.showinfo("Sucesso", "Meta adicionada!")

    # Registrar uma sessão de estudo
    def registrar_sessao(self):
        nome = self.escolher_disciplina("Para qual disciplina deseja registrar uma sessão?")
        if not nome or nome not in dados["disciplinas"]:
            return
        duracao = simpledialog.askinteger("Sessão de Estudo", "Duração em minutos:")
        if duracao and duracao > 0:
            dados["disciplinas"][nome]["sessoes"].append({
                "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "duracao": duracao
            })
            salvar_dados(dados)
            messagebox.showinfo("Sucesso", "Sessão registrada!")

    # Visualizar progresso de todas as disciplinas
    def visualizar_progresso(self):
        janela = tk.Toplevel(self.master)
        janela.title("Progresso de Estudos")

        for nome, info in dados["disciplinas"].items():
            frame = tk.LabelFrame(janela, text=nome, padx=10, pady=10)
            frame.pack(fill="both", expand="yes", padx=10, pady=5)

            metas = info["metas"]
            if not metas:
                tk.Label(frame, text="Nenhuma meta cadastrada.").pack(anchor="w")
            else:
                for m in metas:
                    status = "✅" if m["concluida"] else "❌"
                    tk.Label(frame, text=f"{status} {m['descricao']}").pack(anchor="w")

            total = sum(sessao["duracao"] for sessao in info["sessoes"])
            tk.Label(frame, text=f"Tempo total de estudo: {total} minutos").pack(anchor="w")

    # Marcar meta como concluída
    def marcar_meta_concluida(self):
        nome = self.escolher_disciplina("Escolha uma disciplina:")
        if not nome or nome not in dados["disciplinas"]:
            return

        metas = dados["disciplinas"][nome]["metas"]
        if not metas:
            messagebox.showinfo("Info", "Nenhuma meta para marcar.")
            return

        opcoes = [f"{i+1}. {m['descricao']} {'✅' if m['concluida'] else '❌'}" for i, m in enumerate(metas)]
        escolha = simpledialog.askinteger("Marcar Concluída", "Escolha a meta:\n" + "\n".join(opcoes))

        if escolha and 1 <= escolha <= len(metas):
            metas[escolha - 1]["concluida"] = True
            salvar_dados(dados)
            messagebox.showinfo("Sucesso", "Meta marcada como concluída!")
        else:
            messagebox.showerror("Erro", "Escolha inválida.")

    # Mostrar gráficos de progresso
    def mostrar_graficos(self):
        janela = tk.Toplevel(self.master)
        janela.title("Gráficos de Progresso")
        janela.geometry("900x500")

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        fig.tight_layout(pad=4)

        # ---------- Gráfico 1: Tempo de estudo por disciplina ----------
        nomes = []
        tempos = []
        for nome, info in dados["disciplinas"].items():
            nomes.append(nome)
            tempos.append(sum(sessao["duracao"] for sessao in info["sessoes"]))

        ax1.bar(nomes, tempos, color='skyblue')
        ax1.set_title("Tempo total de estudo")
        ax1.set_ylabel("Minutos")
        ax1.set_xlabel("Disciplinas")
        ax1.tick_params(axis='x', rotation=45)

        # ---------- Gráfico 2: Metas concluídas x pendentes ----------
        concluidas = 0
        pendentes = 0
        for info in dados["disciplinas"].values():
            for meta in info["metas"]:
                if meta["concluida"]:
                    concluidas += 1
                else:
                    pendentes += 1

        if concluidas + pendentes > 0:
            ax2.pie([concluidas, pendentes], labels=["Concluídas", "Pendentes"],
                    autopct='%1.1f%%', startangle=90, colors=["green", "red"])
        else:
            ax2.text(0.5, 0.5, 'Sem metas cadastradas', ha='center', va='center')
        ax2.set_title("Metas de Estudo")

        canvas = FigureCanvasTkAgg(fig, master=janela)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# ---------------- Executar app ----------------

if __name__ == "__main__":
    root = tk.Tk()
    app = OrganizadorEstudosApp(root)
    root.mainloop()
    