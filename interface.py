import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import requests
from bs4 import BeautifulSoup
import spacy

try:
    nlp = spacy.load("pt_core_news_sm")
except OSError:
    raise OSError("Por favor, instale o modelo do spaCy: python -m spacy download pt_core_news_sm")


class NLPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analisador de Texto com NLP")
        self.root.geometry("1000x600")

        tk.Label(root, text="1. Escolha a origem do texto:", font=("Arial", 11, "bold")).pack(anchor="w", padx=10,
                                                                                              pady=5)

        tk.Label(root, text="Digite/Cole o texto ou insira uma URL da Web:").pack(anchor="w", padx=20)
        self.input_text = scrolledtext.ScrolledText(root, height=6, width=80)
        self.input_text.pack(padx=20, pady=5)

        btn_frame = tk.Frame(root)
        btn_frame.pack(anchor="w", padx=20, pady=5)

        tk.Button(btn_frame, text="Carregar Arquivo (.txt)", command=self.carregar_arquivo).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Limpar Campo", command=self.limpar_campo).pack(side="left", padx=5)

        tk.Label(root, text="2. Processamento:", font=("Arial", 11, "bold")).pack(anchor="w", padx=10, pady=10)
        tk.Button(root, text="Processar Texto com NLP", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
                  command=self.processar_texto).pack(fill="x", padx=20, pady=5)

        tk.Label(root, text="3. Resultados da Análise (Entidades Encontradas):", font=("Arial", 11, "bold")).pack(
            anchor="w", padx=10, pady=5)
        self.output_text = scrolledtext.ScrolledText(root, height=12, width=80, bg="#f0f0f0")
        self.output_text.pack(padx=20, pady=5)

    def carregar_arquivo(self):
        caminho_arquivo = filedialog.askopenfilename(filetypes=[("Arquivos de Texto", "*.txt")])
        if caminho_arquivo:
            try:
                with open(caminho_arquivo, "r", encoding="utf-8") as f:
                    conteudo = f.read()
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert(tk.END, conteudo)
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível ler o arquivo:\n{e}")

    def obter_texto_url(self, url):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            resposta = requests.get(url, headers=headers, timeout=5)
            resposta.raise_for_status()


            soup = BeautifulSoup(resposta.text, 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()

            return soup.get_text(separator="\n", strip=True)
        except Exception as e:
            messagebox.showerror("Erro na Web", f"Falha ao buscar a URL:\n{e}")
            return None

    def limpar_campo(self):
        self.input_text.delete("1.0", tk.END)

    def processar_texto(self):
        entrada = self.input_text.get("1.0", tk.END).strip()

        if not entrada:
            messagebox.showwarning("Aviso", "Por favor, digite algo, carregue um arquivo ou insira uma URL válida.")
            return

        if entrada.startswith("http://") or entrada.startswith("https://"):
            texto_para_processar = self.obter_texto_url(entrada)
            if not texto_para_processar:
                return
        else:
            texto_para_processar = entrada

        doc = nlp(texto_para_processar)


        self.output_text.delete("1.0", tk.END)


        self.output_text.insert(tk.END, f"Total de caracteres analisados: {len(texto_para_processar)}\n")
        self.output_text.insert(tk.END, "=" * 50 + "\n\n")

        if not doc.ents:
            self.output_text.insert(tk.END, "Nenhuma entidade nomeada (Pessoas, Locais, Organizações) foi encontrada.")
            return

        self.output_text.insert(tk.END, "ENTIDADES ENCONTRADAS:\n")
        for ent in doc.ents:

            self.output_text.insert(tk.END, f"- [{ent.label_}] {ent.text}\n")



if __name__ == "__main__":
    root = tk.Tk()
    app = NLPApp(root)
    root.mainloop()