"""Interface do Chat."""
import flet as ft
from features.chat.service import ChatService
from shared.components import create_message_bubble

# NÃO precisa mais importar APIStatusIndicator aqui

class ChatView:
    def __init__(self, page: ft.Page, service: ChatService, get_model_fn):
        self.page = page
        self.service = service
        self.get_model_fn = get_model_fn
        
        # REMOVIDO: self.api_monitor = APIStatusIndicator(...)
        
        self.chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)
        self.input_field = ft.TextField(
            hint_text="Pergunte algo...", 
            on_submit=self._send_message,
            expand=True
        )
        
        self.container = ft.Container(
            content=ft.Column([
                self.chat_list,
                # REMOVIDO: O container do monitor que ficava aqui
                ft.Row([
                    self.input_field,
                    ft.IconButton(ft.Icons.SEND, on_click=self._send_message),
                    ft.IconButton(
                        ft.Icons.DELETE_OUTLINE, 
                        on_click=self._clear_chat,
                        tooltip="Limpar conversa"
                    )
                ])
            ]),
            padding=20,
            expand=True
        )
    
    async def _send_message(self, e):
        # ... (código de validação igual) ...
        if not self.input_field.value.strip(): return
        
        model = self.get_model_fn()
        if not model:
            self._show_error("Selecione um modelo.")
            return

        user_msg = self.input_field.value
        self.input_field.value = ""
        self.input_field.disabled = True
        self.page.update()
        
        self._add_message("user", user_msg)
        ai_bubble = self._add_message("assistant", "💭 Pensando...")
        
        full_response = ""
        
        # --- AQUI ESTÁ A MÁGICA DO PubSub ---
        async for chunk in self.service.send_message(user_msg, model):
            full_response += chunk
            ai_bubble.value = full_response
            
            # Envia sinal global: "Ei, atualize o gráfico!"
            self.page.pubsub.send_all("api_update")
            
            self.page.update()
        # ------------------------------------
        
        self.page.pubsub.send_all("api_update") # Atualização final
        
        self.input_field.disabled = False
        self.input_field.focus()
        self.page.update()

    # ... (restante dos métodos iguais) ...
    def _add_message(self, role, text):
        bubble = create_message_bubble(role, text)
        self.chat_list.controls.append(bubble)
        self.page.update()
        return bubble.controls[0].content

    def _clear_chat(self, e):
        self.chat_list.controls.clear()
        self.service.clear_history()
        self.page.update()

    def _show_error(self, msg):
        self.page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=ft.Colors.RED_400)
        self.page.snack_bar.open = True
        self.page.update()