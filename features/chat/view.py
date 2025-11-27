"""Interface do Chat."""
import flet as ft
from features.chat.service import ChatService
from shared.components import create_message_bubble

class ChatView:
    """View do Chat com IA."""
    
    def __init__(self, page: ft.Page, service: ChatService, get_model_fn):
        self.page = page
        self.service = service
        self.get_model_fn = get_model_fn
        
        # Componentes
        self.chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)
        self.input_field = ft.TextField(
            hint_text="Pergunte algo...", 
            on_submit=self._send_message,
            expand=True
        )
        
        self.container = ft.Container(
            content=ft.Column([
                self.chat_list,
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
        """Envia mensagem do usuário."""
        if not self.input_field.value.strip():
            return
        
        model = self.get_model_fn()
        if not model:
            self._show_error("Selecione um modelo primeiro.")
            return
        
        user_msg = self.input_field.value
        self.input_field.value = ""
        self.input_field.disabled = True
        self.page.update()
        
        # Adiciona mensagem do usuário
        self._add_message("user", user_msg)
        
        # Adiciona resposta da IA
        ai_bubble = self._add_message("assistant", "💭 Pensando...")
        
        full_response = ""
        async for chunk in self.service.send_message(user_msg, model):
            full_response += chunk
            ai_bubble.value = full_response
            self.page.update()
        
        self.input_field.disabled = False
        self.input_field.focus()
        self.page.update()
    
    def _add_message(self, role: str, text: str):
        """Adiciona mensagem visual ao chat."""
        bubble = create_message_bubble(role, text)
        self.chat_list.controls.append(bubble)
        self.page.update()
        return bubble.controls[0].content  # Retorna o Markdown
    
    def _clear_chat(self, e):
        """Limpa o chat."""
        self.chat_list.controls.clear()
        self.service.clear_history()
        self.page.update()
    
    def _show_error(self, msg: str):
        """Exibe mensagem de erro."""
        self.page.snack_bar = ft.SnackBar(
            ft.Text(msg), 
            bgcolor=ft.Colors.RED_400
        )
        self.page.snack_bar.open = True
        self.page.update()