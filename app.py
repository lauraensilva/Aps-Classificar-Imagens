import customtkinter as ctk
import json
from tkinter import filedialog
from PIL import Image
import os
import io
import cv2 
from dotenv import load_dotenv
from google.cloud import vision
from google.api_core import exceptions as google_exceptions

# ==============================================================================
# 1. CONFIGURAÇÃO E AUTENTICAÇÃO
# ==============================================================================

load_dotenv()
json_cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not json_cred_path:
    print("ERRO DE CONFIGURAÇÃO:")
    print("A variável de ambiente 'GOOGLE_APPLICATION_CREDENTIALS' não está definida no seu arquivo .env.")
    print("O script não poderá se autenticar. Por favor, corrija o .env e tente novamente.")

# Define a variável de ambiente para a biblioteca do Google encontrar
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_cred_path


# ==============================================================================
# 1.5. CONFIGURAÇÃO DO FILTRO E TRADUÇÃO
# ==============================================================================

# Dicionário para traduzir os rótulos da API (Inglês) para Português
# E TAMBÉM serve como lista de filtros para TODOS OS EPIs que queremos encontrar.
TRADUCOES_E_FILTROS = {
    
    # --- Capacetes ---
    "Helmet": "Capacete",
    "Hat": "Capacete",
    "Hard hat": "Capacete",
    "Safety helmet": "Capacete de Segurança",
    
    # --- Luvas ---
    "Glove": "Luva",
    "Protective glove": "Luva de Proteção",
    "Safety glove": "Luva de Segurança",

    # --- Botas ---
    "Boot": "Bota",
    "Safety boot": "Bota de Segurança",
    "Work boot": "Bota de Trabalho",

    # --- Óculos ---
    "Goggles": "Óculos de Proteção",
    "Safety goggles": "Óculos de Proteção",
    "Glasses": "Óculos",
    "Eyewear": "Óculos",
    "Safety glasses": "Óculos de Segurança",

    # --- Coletes ---
    "Vest": "Colete",
    "High-visibility clothing": "Colete de Alta Visibilidade",
    "Safety vest": "Colete de Segurança",

    # --- Máscaras ---
    "Mask": "Máscara",
    "Respirator": "Respirador / Máscara",
    "Dust mask": "Máscara de Poeira"
}

# set (conjunto) com todas as chaves em INGLÊS para uma filtragem rápida.
OBJETOS_FILTRADOS = set(TRADUCOES_E_FILTROS.keys())


# ==============================================================================
# 2. FUNÇÃO PARA COMUNICAÇÃO COM A VISION API (MODIFICADA)
# ==============================================================================

def analisar_com_conta_servico(caminho_imagem):
    """
    Envia uma imagem para a Vision API usando a autenticação da Conta de Serviço.
    """
    if not json_cred_path:
        return {"error": "Autenticação não configurada. Verifique o .env."}

    try:
        client = vision.ImageAnnotatorClient()

        with io.open(caminho_imagem, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        
        response = client.object_localization(image=image)
  
        return response

    except google_exceptions.PermissionDenied as e:
        return {"error": f"Permissão negada (403). Verifique se a API Cloud Vision está ativa, se o faturamento está configurado e se a Conta de Serviço possui a permissão 'Cloud Vision API User'."}
    except FileNotFoundError:
        return {"error": f"O arquivo de imagem {caminho_imagem} não foi encontrado."}
    except google_exceptions.GoogleAPICallError as e:
        return {"error": f"Erro na chamada à API: {e.message}"}
    except Exception as e:
        return {"error": f"Ocorreu um erro inesperado: {e}"}


# ==============================================================================
# 3. CLASSE DA APLICAÇÃO DE INTERFACE GRÁFICA
# ==============================================================================

class ChatVisionApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Analisador de Objetos (Google Vision API)")
        self.geometry("700x600") 
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
        
        self.adicionar_mensagem_ao_chat("Assistente", "Olá! Por favor, envie uma imagem para análise de objetos.")

    def adicionar_mensagem_ao_chat(self, remetente, texto):
        # Cria e empacota a mensagem no chat_frame
        message_label = ctk.CTkLabel(self.chat_frame, text=f"{remetente}:\n{texto}", justify="left", wraplength=400)
        anchor = "w" if remetente == "Assistente" else "e"
        message_label.pack(side="top", anchor=anchor, padx=10, pady=5)
        # Scroll para o final
        self.after(10, lambda: self.chat_frame._parent_canvas.yview_moveto(1.0))

    
    def adicionar_imagem_ao_chat(self, remetente, image_data, is_path=True):
        """
        Adiciona uma imagem ao chat.
        Se is_path=True, image_data é um caminho de arquivo.
        Se is_path=False, image_data é um objeto de Imagem PIL.
        """
        try:
            if is_path:
                # Se for um caminho, abre o arquivo
                img = Image.open(image_data)
            else:
                # Se for um objeto PIL, apenas o utiliza
                img = image_data
            
            # Redimensiona para exibição no chat
            img.thumbnail((200, 200))
            ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            
            sender_label = ctk.CTkLabel(self.chat_frame, text=f"{remetente}:")
            image_label = ctk.CTkLabel(self.chat_frame, image=ctk_image, text="")
            
            anchor = "w" if remetente == "Assistente" else "e"
            sender_label.pack(side="top", anchor=anchor, padx=10, pady=(5,0))
            image_label.pack(side="top", anchor=anchor, padx=10, pady=(0,5))
            
            self.after(10, lambda: self.chat_frame._parent_canvas.yview_moveto(1.0))
        except Exception as e:
            print(f"Erro ao carregar a imagem para GUI: {e}")
            self.adicionar_mensagem_ao_chat("Sistema", "Erro ao exibir a imagem.")

  
    def selecionar_e_enviar_imagem(self):
        filepath = filedialog.askopenfilename(title="Selecione uma Imagem", filetypes=[("Arquivos de Imagem", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if not filepath: 
            return
            
        filename = os.path.basename(filepath)
        self.selected_file_label.configure(text=f"Enviando: {filename}")
        
      
        self.adicionar_imagem_ao_chat("Você", filepath, is_path=True)
        
        self.after(100, lambda: self.processar_resposta(filepath))

 
   # --- FUNÇÃO PARA O CORTE ---
    def processar_resposta(self, image_path):
        """
        Chama a API, filtra, traduz e CORTA os objetos usando OpenCV.
        """
        
        # 1. Chama a função de análise (object_localization)
        dados_resposta = analisar_com_conta_servico(image_path)
        
        # 2. Trata erros
        if isinstance(dados_resposta, dict) and "error" in dados_resposta:
            resposta_final = f"ERRO:\n{dados_resposta['error']}"
            self.adicionar_mensagem_ao_chat("Assistente", resposta_final)
            self.selected_file_label.configure(text="Nenhum arquivo selecionado.")
            return

        if dados_resposta.error.message:
            resposta_final = f"Erro da API ao processar imagem:\n{dados_resposta.error.message}"
            self.adicionar_mensagem_ao_chat("Assistente", resposta_final)
            self.selected_file_label.configure(text="Nenhum arquivo selecionado.")
            return
        
        # 3. Processa a resposta de SUCESSO
        objects = dados_resposta.localized_object_annotations
        objetos_filtrados = [obj for obj in objects if obj.name in OBJETOS_FILTRADOS]

        if objetos_filtrados:
            self.adicionar_mensagem_ao_chat("Assistente", f"✅ Análise concluída. {len(objetos_filtrados)} EPI(s) encontrado(s):")
            
            try:
                # Carrega a imagem usando OpenCV
                original_img_cv2 = cv2.imread(image_path)
                # Obtém altura e largura (OpenCV inverte a ordem comparado ao PIL)
                height, width = original_img_cv2.shape[:2] 
            except Exception as e:
                self.adicionar_mensagem_ao_chat("Assistente", f"Erro ao abrir a imagem original para cortar: {e}")
                return
           

            for i, obj in enumerate(objetos_filtrados):
                
                nome_en = obj.name
                nome_pt = TRADUCOES_E_FILTROS.get(nome_en, nome_en)
                score = obj.score * 100
                
                texto_obj = f"Item {i+1}: {nome_pt}\n(Confiança: {score:.2f}%)"
                self.adicionar_mensagem_ao_chat("Assistente", texto_obj)

                # --- Lógica de Corte da Imagem 
                vertices = obj.bounding_poly.normalized_vertices
                
                # Converte coordenadas normalizadas (0.0 a 1.0) em pixels
                # Arredonda para garantir que são pixels inteiros
                x1 = int(vertices[0].x * width)
                y1 = int(vertices[0].y * height)
                x2 = int(vertices[2].x * width)
                y2 = int(vertices[2].y * height)

                # Garante que as coordenadas estão dentro dos limites da imagem
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(width, x2), min(height, y2)
                
                # Corta a imagem usando o fatiamento (slicing) do NumPy/OpenCV
                cropped_img_cv2 = original_img_cv2[y1:y2, x1:x2]
                
                # --- Conversão de volta para PIL ---
                # 1. Converte de BGR (padrão OpenCV) para RGB (padrão PIL)
                rgb_img = cv2.cvtColor(cropped_img_cv2, cv2.COLOR_BGR2RGB)
                # 2. Converte do array NumPy (OpenCV) para um objeto Imagem PIL
                cropped_img_pil = Image.fromarray(rgb_img)
                
                # Adiciona a imagem CORTADA ao chat (passando o objeto PIL)
                self.adicionar_imagem_ao_chat("Assistente", cropped_img_pil, is_path=False)

        else:
            resposta_final = "Análise concluída, mas nenhum EPI foi encontrado na imagem."
            self.adicionar_mensagem_ao_chat("Assistente", resposta_final)
        
        self.selected_file_label.configure(text="Nenhum arquivo selecionado.")

# ==============================================================================
# 4. PONTO DE ENTRADA DA APLICAÇÃO
# ==============================================================================
if __name__ == "__main__":
    if json_cred_path:
        app = ChatVisionApp()
        app.mainloop()
    else:
        print("\nAplicação encerrada devido à falha na configuração de autenticação.")