# Importando bibliotecas necessárias
import tkinter as tk
from tkinter import messagebox

# Criando a classe para o frontend
class Frontend:
    def __init__(self):
        # Criando a janela principal
        self.janela = tk.Tk()
        self.janela.title("Frontend")

        # Criando o menu
        self.menu = tk.Menu(self.janela)
        self.janela.config(menu=self.menu)

        # Criando as opções do menu
        self.arquivo = tk.Menu(self.menu)
        self.menu.add_cascade(label="Arquivo", menu=self.arquivo)
        self.arquivo.add_command(label="Novo", command=self.novo)
        self.arquivo.add_command(label="Abrir", command=self.abrir)
        self.arquivo.add_separator()
        self.arquivo.add_command(label="Sair", command=self.janela.quit)

        # Criando o frame para o conteúdo
        self.conteudo = tk.Frame(self.janela)
        self.conteudo.pack(padx=10, pady=10)

        # Criando o campo de texto
        self.texto = tk.Text(self.conteudo)
        self.texto.pack(fill=tk.BOTH, expand=True)

    # Método para criar um novo arquivo
    def novo(self):
        # Limpa o campo de texto
        self.texto.delete(1.0, tk.END)

    # Método para abrir um arquivo
    def abrir(self):
        # Abre um arquivo e insere o conteúdo no campo de texto
        from tkinter import filedialog
        arquivo = filedialog.askopenfilename()
        if arquivo:
            with open(arquivo, 'r') as f:
                self.texto.delete(1.0, tk.END)
                self.texto.insert(tk.END, f.read())

    # Método para iniciar o frontend
    def iniciar(self):
        self.janela.mainloop()

# Criando uma instância do frontend e iniciando
if __name__ == "__main__":
    frontend = Frontend()
    frontend.iniciar()