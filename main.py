import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
import requests
import base64
import json
import os # Importe a biblioteca OS
from dotenv import load_dotenv # Importe a função load_dotenv

# Carrega as variáveis do arquivo .env para o ambiente
load_dotenv()

# Lê a chave de API do ambiente. Retorna None se não encontrar.
MINHA_CHAVE_API = os.getenv("GOOGLE_API_KEY")

# --- Função de chamada da API (sem alterações) ---
def analisar_com_api_key(caminho_imagem, chave_api):
    """
    Envia uma imagem para a Vision API usando uma Chave de API e retorna a resposta.
    """
    # Verifica se a chave foi carregada
    if not chave_api:
        return {"error": "A chave da API do Google não foi encontrada. Verifique seu arquivo .env."}

    url_endpoint = f"https://vision.googleapis.com/v1/images:annotate?key={chave_api}"
    try:
        with open(caminho_imagem, "rb") as image_file:
            conteudo_imagem = base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        return {"error": f"Não foi possível ler a imagem: {e}"}

    corpo_requisicao = {
        "requests": [
            {
                "image": {
                    "content": conteudo_imagem
                },
                "features": [
                    {
                        "type": "LABEL_DETECTION",
                        "maxResults": 5
                    }
                ]
            }
        ]
    }
    try:
        response = requests.post(url_endpoint, json=corpo_requisicao)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Erro na requisição para a API: {e}"}


# --- Classe da Aplicação (com a chamada atualizada) ---
class ChatVisionApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        # ... (resto do seu __init__ sem alterações) ...
        self.title("Analisador de Imagens")
        self.geometry("700x550")
        self.minsize(500, 400)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.chat_frame = ctk.CTkScrollableFrame(self, label_text="Histórico da Conversa")
        self.chat_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.input_frame = ctk.CTkFrame(self, height=50)
        self.input_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_columnconfigure(1, weight=0)
        self.selected_file_label = ctk.CTkLabel(self.input_frame, text="Nenhum arquivo selecionado.", text_color="gray")
        self.selected_file_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.select_image_button = ctk.CTkButton(self.input_frame, text="Enviar Imagem", command=self.selecionar_e_enviar_imagem)
        self.select_image_button.grid(row=0, column=1, padx=10, pady=10)
        self.adicionar_mensagem_ao_chat("Assistente", "Olá! Por favor, envie uma imagem para análise.")

    # ... (funções adicionar_mensagem_ao_chat e adicionar_imagem_ao_chat sem alterações) ...
    def adicionar_mensagem_ao_chat(self, remetente, texto):
        message_label = ctk.CTkLabel(self.chat_frame, text=f"{remetente}:\n{texto}", justify="left", wraplength=400)
        if remetente == "Assistente":
            message_label.pack(side="top", anchor="w", padx=10, pady=5)
        else:
            message_label.pack(side="top", anchor="e", padx=10, pady=5)
        self.after(10, lambda: self.chat_frame._parent_canvas.yview_moveto(1.0))

    def adicionar_imagem_ao_chat(self, remetente, image_path):
        try:
            img = Image.open(image_path)
            img.thumbnail((200, 200))
            ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            sender_label = ctk.CTkLabel(self.chat_frame, text=f"{remetente}:")
            image_label = ctk.CTkLabel(self.chat_frame, image=ctk_image, text="")
            sender_label.pack(side="top", anchor="e", padx=10, pady=(5,0))
            image_label.pack(side="top", anchor="e", padx=10, pady=(0,5))
            self.after(10, lambda: self.chat_frame._parent_canvas.yview_moveto(1.0))
        except Exception as e:
            print(f"Erro ao carregar a imagem: {e}")
            self.adicionar_mensagem_ao_chat("Sistema", "Erro ao exibir a imagem.")

    def selecionar_e_enviar_imagem(self):
        filepath = filedialog.askopenfilename(title="Selecione uma Imagem", filetypes=[("Arquivos de Imagem", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if not filepath: return
        filename = filepath.split("/")[-1]
        self.selected_file_label.configure(text=f"Enviando: {filename}")
        self.adicionar_imagem_ao_chat("Você", filepath)
        self.after(1000, lambda: self.processar_resposta(filepath))

    def processar_resposta(self, image_path):
        """Função que chama a API do Google Cloud e exibe a resposta."""
        # A chave agora é lida da variável global carregada do .env
        dados_resposta = analisar_com_api_key(image_path, MINHA_CHAVE_API)
        
        # ... (resto da função processar_resposta sem alterações) ...
        if "error" in dados_resposta:
            resposta_final = f"Ocorreu um erro: {dados_resposta['error']}"
        elif "responses" in dados_resposta and dados_resposta["responses"]:
            primeira_resposta = dados_resposta["responses"][0]
            if "labelAnnotations" in primeira_resposta:
                resposta_final = "Rótulos detectados:\n"
                labels = primeira_resposta["labelAnnotations"]
                for label in labels:
                    descricao = label.get('description', 'N/A')
                    score = label.get('score', 0) * 100
                    resposta_final += f"- {descricao} (Confiança: {score:.2f}%)\n"
            else:
                resposta_final = "Análise concluída, mas nenhum rótulo foi encontrado."
        else:
            resposta_final = "A API retornou uma resposta vazia ou em formato inesperado."
        self.adicionar_mensagem_ao_chat("Assistente", resposta_final)
        self.selected_file_label.configure(text="Nenhum arquivo selecionado.")

if __name__ == "__main__":
    # Adicionamos uma verificação para garantir que a chave foi carregada
    if not MINHA_CHAVE_API:
        print("ERRO: A variável de ambiente GOOGLE_API_KEY não foi definida.")
        print("Por favor, crie um arquivo .env e adicione GOOGLE_API_KEY=sua_chave")
    else:
        app = ChatVisionApp()
        app.mainloop()