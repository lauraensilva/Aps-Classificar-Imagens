import customtkinter as ctk
from tkinter import filedialog
from PIL import Image

# Configurações iniciais da aparência
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class ChatVisionApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Configuração da Janela Principal ---
        self.title("Analisador de Imagens")
        self.geometry("700x550")
        self.minsize(500, 400)

        # --- Layout Principal (Grid) ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Widgets ---
        # 1. Frame rolável para exibir o chat
        self.chat_frame = ctk.CTkScrollableFrame(self, label_text="Histórico da Conversa")
        self.chat_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # 2. Frame para os controles de entrada na parte inferior
        self.input_frame = ctk.CTkFrame(self, height=50)
        self.input_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_columnconfigure(1, weight=0)

        # 3. Label para mostrar o arquivo selecionado
        self.selected_file_label = ctk.CTkLabel(self.input_frame, text="Nenhum arquivo selecionado.", text_color="gray")
        self.selected_file_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # 4. Botão para selecionar imagem
        self.select_image_button = ctk.CTkButton(self.input_frame, text="Enviar Imagem", command=self.selecionar_e_enviar_imagem)
        self.select_image_button.grid(row=0, column=1, padx=10, pady=10)

        # Adiciona uma mensagem inicial
        self.adicionar_mensagem_ao_chat("Assistente", "Olá! Por favor, envie uma imagem para análise.")

    def adicionar_mensagem_ao_chat(self, remetente, texto):
        """Adiciona um balão de mensagem de texto ao chat."""
        # Cria um label para a mensagem
        message_label = ctk.CTkLabel(self.chat_frame, text=f"{remetente}:\n{texto}", justify="left", wraplength=400)
        
        # Alinha a mensagem à esquerda para o Assistente, e à direita para o Usuário
        if remetente == "Assistente":
            message_label.pack(side="top", anchor="w", padx=10, pady=5)
        else:
            message_label.pack(side="top", anchor="e", padx=10, pady=5)
        
        # Rola para a mensagem mais recente
        self.after(10, lambda: self.chat_frame._parent_canvas.yview_moveto(1.0))


    def adicionar_imagem_ao_chat(self, remetente, image_path):
        """Adiciona um balão com uma imagem ao chat."""
        try:
            # Carrega a imagem e a redimensiona
            img = Image.open(image_path)
            img.thumbnail((200, 200))
            ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)

            # Cria um label para o remetente
            sender_label = ctk.CTkLabel(self.chat_frame, text=f"{remetente}:")
            
            # Cria um label para a imagem
            image_label = ctk.CTkLabel(self.chat_frame, image=ctk_image, text="")
            
            # Alinha à direita para o usuário
            sender_label.pack(side="top", anchor="e", padx=10, pady=(5,0))
            image_label.pack(side="top", anchor="e", padx=10, pady=(0,5))
            
            # Rola para a mensagem mais recente
            self.after(10, lambda: self.chat_frame._parent_canvas.yview_moveto(1.0))

        except Exception as e:
            print(f"Erro ao carregar a imagem: {e}")
            self.adicionar_mensagem_ao_chat("Sistema", "Erro ao exibir a imagem.")

    def selecionar_e_enviar_imagem(self):
        """Abre o seletor de arquivos e processa a imagem selecionada."""
        filepath = filedialog.askopenfilename(
            title="Selecione uma Imagem",
            filetypes=[("Arquivos de Imagem", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if not filepath:
            return

        filename = filepath.split("/")[-1]
        self.selected_file_label.configure(text=f"Enviando: {filename}")

        # 1. Exibe a imagem enviada pelo usuário na tela
        self.adicionar_imagem_ao_chat("Você", filepath)

        # 2. Simula o processamento e a resposta do assistente
        self.after(1000, lambda: self.processar_resposta(filepath))
        
    def processar_resposta(self, image_path):
        """Função placeholder para a lógica da API do Google Cloud."""
        resposta_placeholder = "Analisando imagem...\n\n" \
                               "Futuramente, a resposta com os labels detectados pela API aparecerá aqui."

        self.adicionar_mensagem_ao_chat("Assistente", resposta_placeholder)
        self.selected_file_label.configure(text="Nenhum arquivo selecionado.")

if __name__ == "__main__":
    app = ChatVisionApp()
    app.mainloop()