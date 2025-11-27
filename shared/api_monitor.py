import flet as ft

class APIStatusIndicator(ft.Container):
    """Componente visual global para monitorar uso da API."""
    
    def __init__(self, gemini_client):
        super().__init__()
        self.client = gemini_client
        
        # Estilo compacto para caber na sidebar
        self.padding = 10
        self.border_radius = 8
        self.bgcolor = ft.Colors.GREY_900
        self.margin = ft.margin.only(bottom=10, left=5, right=5)
        
        # Componentes
        self.bar = ft.ProgressBar(
            value=0, 
            width=None, # Largura automática
            height=6, 
            color=ft.Colors.GREEN,
            bgcolor=ft.Colors.GREY_800
        )
        
        self.percentage_text = ft.Text("0%", size=10, weight=ft.FontWeight.BOLD)
        self.rpm_text = ft.Text("0/15 RPM", size=10, color=ft.Colors.GREY_400)
        
        self.content = ft.Column(
            spacing=3,
            controls=[
                ft.Row([
                    ft.Text("API Status", size=11, weight=ft.FontWeight.BOLD),
                    self.percentage_text
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self.bar,
                ft.Row([
                    self.rpm_text,
                    ft.Icon(ft.Icons.CIRCLE, size=8, color=ft.Colors.GREEN, ref=self.status_icon_ref())
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ]
        )

    def status_icon_ref(self):
        """Referência para atualizar ícone sem recriar objeto."""
        self.status_icon = ft.Icon(ft.Icons.CIRCLE, size=8, color=ft.Colors.GREEN)
        return self.status_icon

    def did_mount(self):
        """Chamado quando o componente entra na tela. Inscreve no canal."""
        self.page.pubsub.subscribe(self._on_message)
        self.update_stats() # Primeira atualização

    def will_unmount(self):
        """Chamado quando sai. Remove inscrição."""
        self.page.pubsub.unsubscribe(self._on_message)

    def _on_message(self, topic):
        """Recebe o sinal global para atualizar."""
        if topic == "api_update":
            self.update_stats()

    def update_stats(self):
        """Lógica de atualização visual."""
        stats = self.client.get_usage_stats()
        
        current_rpm = stats['requests_last_min']
        max_rpm = 15
        
        ratio = min(current_rpm / max_rpm, 1.0) if max_rpm > 0 else 0
        
        # Atualiza valores
        self.bar.value = ratio
        self.percentage_text.value = f"{int(ratio * 100)}%"
        self.rpm_text.value = f"{current_rpm}/15 RPM"
        
        # Cores dinâmicas
        if ratio < 0.5:
            color = ft.Colors.GREEN
        elif ratio < 0.8:
            color = ft.Colors.AMBER
        else:
            color = ft.Colors.RED
            
        self.bar.color = color
        self.status_icon.color = color
        
        # IMPORTANTE: Atualiza APENAS este container, não a página toda
        self.update()