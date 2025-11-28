import flet as ft

class APIStatusIndicator(ft.Container):
    """Componente visual global para monitorar uso da API com Tooltip Detalhado."""
    
    def __init__(self, gemini_client):
        super().__init__()
        self.client = gemini_client
        
        # Estilo da Sidebar
        self.padding = 10
        self.border_radius = 8
        self.bgcolor = ft.Colors.GREY_900
        self.margin = ft.margin.only(bottom=10, left=5, right=5)
        
        # Tooltip
        self.tooltip = "Aguardando dados..."
        
        # Componentes
        self.bar_rpm = ft.ProgressBar(value=0, width=None, height=6, color=ft.Colors.GREEN, bgcolor=ft.Colors.GREY_800)
        self.bar_tpm = ft.ProgressBar(value=0, width=None, height=4, color=ft.Colors.BLUE, bgcolor=ft.Colors.GREY_800)
        self.rpm_text = ft.Text("0 RPM", size=10, weight=ft.FontWeight.BOLD)
        self.tpm_text = ft.Text("0 TPM", size=9, color=ft.Colors.GREY_400)
        
        self.content = ft.Column(
            spacing=3,
            controls=[
                ft.Row([ft.Text("API Status", size=11, weight=ft.FontWeight.BOLD), self.rpm_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self.bar_rpm,
                ft.Row([ft.Text("Tokens", size=9, color=ft.Colors.GREY_400), self.tpm_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self.bar_tpm,
                ft.Row([ft.Text("Passe o mouse", size=8, italic=True, color=ft.Colors.GREY_600), ft.Icon(ft.Icons.INFO_OUTLINE, size=10, color=ft.Colors.GREY_500)], alignment=ft.MainAxisAlignment.END, spacing=2)
            ]
        )

    def did_mount(self):
        """Inicia a escuta de eventos quando o componente entra na tela."""
        # Se inscreve no canal "api_update"
        self.page.pubsub.subscribe(self._on_message)
        self.update_stats()

    def will_unmount(self):
        """Limpa a inscrição ao sair."""
        self.page.pubsub.unsubscribe(self._on_message)

    def _on_message(self, topic):
        """Recebe o sinal para atualizar."""
        if topic == "api_update":
            self.update_stats()

    def update_stats(self):
        """Busca dados e atualiza visual."""
        try:
            stats = self.client.get_usage_stats()
            
            rpm_curr, rpm_lim = stats["rpm_current"], stats["rpm_limit"]
            tpm_curr, tpm_lim = stats["tpm_current"], stats["tpm_limit"]
            
            # Atualiza Tooltip
            self.tooltip = (
                f"MODELO: {stats['model']}\n"
                f"-----------------------------------\n"
                f"📊 RPM:  {rpm_curr} / {rpm_lim}\n"
                f"📝 TPM:  {self._format_k(tpm_curr)} / {self._format_k(tpm_lim)}\n"
                f"-----------------------------------\n"
                f"⚠️ Erros: {stats['errors']}"
            )
            
            # Atualiza Barras
            self.bar_rpm.value = min(stats["rpm_percent"], 1.0)
            self.bar_tpm.value = min(stats["tpm_percent"], 1.0)
            
            # Cores
            if stats["rpm_percent"] < 0.5: self.bar_rpm.color = ft.Colors.GREEN
            elif stats["rpm_percent"] < 0.8: self.bar_rpm.color = ft.Colors.AMBER
            else: self.bar_rpm.color = ft.Colors.RED
            
            # Textos
            self.rpm_text.value = f"{rpm_curr}/{rpm_lim}"
            self.tpm_text.value = f"{self._format_k(tpm_curr)}"
            
            self.update()
        except Exception as e:
            print(f"Erro updating stats: {e}")

    def _format_k(self, num):
        if num >= 1_000_000: return f"{num/1_000_000:.1f}M"
        if num >= 1_000: return f"{num/1000:.0f}k"
        return str(num)