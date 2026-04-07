"""
main.py - AI Studio Desktop
"""

import flet as ft
import traceback
from google import genai

from config.settings import settings
from core.gemini_client import GeminiClient
from core.knowledge_manager import KnowledgeManager

# Services
try:
    from features.chat.service import ChatService
    from features.project_analyzer.service import ProjectAnalyzerService
    from features.log_fixer.service import LogFixerService
    from features.automations.service import AutomationsService
except ImportError as e:
    print(f"Erro de importação nos serviços: {e}")


# Views
try:
    from features.chat.view import ChatView
    from features.project_analyzer.view import ProjectAnalyzerView
    from features.log_fixer.view import LogFixerView
    from features.automations.view import AutomationsView
    from features.data_randomizer.view import DataRandomizerView
except ImportError as e:
    print(f"Erro de importação nas views: {e}")

# Shared Components
from shared.api_monitor import APIStatusIndicator


class App:
    """Aplicação principal - inicializa serviços e views."""

    def __init__(self, page: ft.Page):
        self.page = page
        self._setup_page()

        # --- Knowledge Manager ---
        self.knowledge_mgr = KnowledgeManager()

        # --- Core client (Gemini) ---
        try:
            api_key = getattr(settings, "GEMINI_API_KEY", "")
            self.gemini = GeminiClient(api_key=api_key) if api_key else GeminiClient()
        except Exception:
            self.gemini = GeminiClient()

        # --- Monitor de API ---
        self.api_monitor = APIStatusIndicator(self.gemini)
        # --- Services ---
        self._init_services()
        # --- UI: Config section ---
        self._build_config_bar()

        # --- NavigationRail ---
        # Definimos expand=True para que o Rail ocupe todo o espaço vertical disponível
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=120,
            group_alignment=-0.9, # Mantém os ícones no topo
            destinations=[
                ft.NavigationRailDestination(icon=ft.Icons.CHAT, label="Chat"),
                ft.NavigationRailDestination(icon=ft.Icons.FOLDER, label="Projeto"),
                ft.NavigationRailDestination(icon=ft.Icons.TERMINAL, label="Logs"),
                ft.NavigationRailDestination(icon=ft.Icons.AUTO_MODE, label="Automações"),
                ft.NavigationRailDestination(icon=ft.Icons.SHUFFLE, label="Randomizar"),
            ],
            on_change=self._change_view,
            expand=True # <--- IMPORTANTE: Permite que funcione dentro da Column sem erro de altura
        )

        # --- Views ---
        self._init_views()

        # --- Layout ---
        self._build_layout()

        # Auto-load se tiver chave
        if getattr(settings, "GEMINI_API_KEY", ""):
            try:
                self._load_models()
            except Exception as e:
                print("Falha ao carregar modelos automaticamente:", e)

    def _setup_page(self):
        """Configura página inicial."""
        self.page.title = getattr(settings, "APP_TITLE", "AI Studio Desktop")
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.window_width = getattr(settings, "WINDOW_WIDTH", 1366)
        self.page.window_height = getattr(settings, "WINDOW_HEIGHT", 768)
        self.page.padding = 0

    def _init_services(self):
        try:
            self.chat_service = ChatService(self.gemini)
        except Exception as e:
            self.chat_service = None
            print("Falha ao criar ChatService:", e)

        try:
            self.project_service = ProjectAnalyzerService(self.gemini)
        except Exception as e:
            self.project_service = None
            print("Falha ao criar ProjectAnalyzerService:", e)

        try:
            self.log_fixer_service = LogFixerService(self.gemini)
        except Exception as e:
            self.log_fixer_service = None
            print("Falha ao criar LogFixerService:", e)

        try:
            self.automations_service = AutomationsService(self.gemini)
        except Exception as e:
            self.automations_service = None
            print("Falha ao criar AutomationsService:", e)

    def _build_config_bar(self):
        self.api_key_field = ft.TextField(
            label="Gemini API Key",
            password=True,
            width=300,
            value=getattr(settings, "GEMINI_API_KEY", ""),
            hint_text="Cole sua chave aqui"
        )

        self.model_dropdown = ft.Dropdown(
            label="Modelo",
            width=250,
            hint_text="Carregue a chave primeiro",
            on_select=self._on_model_change
        )

        self.status_text = ft.Text("", size=12)

        # Barra de configuração superior com botões
        self.config_bar = ft.Container(
            content=ft.Column([
                # Linha 1: API Key, Modelo, Status com botões
                ft.Row([
                    self.api_key_field,
                    ft.IconButton(ft.Icons.REFRESH, on_click=lambda _: self._load_models(), tooltip="Recarregar Modelos"),
                    self.model_dropdown,
                    ft.VerticalDivider(),
                    self.status_text,
                    ft.Container(expand=True),  # Spacer dinâmico
                    # Novos botões
                    ft.IconButton(
                        ft.Icons.SETTINGS,
                        on_click=self._show_settings_dialog,
                        tooltip="Configurações e Conhecimentos"
                    ),
                    ft.IconButton(
                        ft.Icons.RESTART_ALT,
                        on_click=self._reset_app,
                        tooltip="Resetar App (Limpa instâncias e cache)"
                    ),
                ], alignment=ft.MainAxisAlignment.START, spacing=12),
            ], spacing=10),
            padding=10,
            bgcolor=ft.Colors.BLACK12
        )

    def _init_views(self):
        try:
            self.chat_view = ChatView(self.page, self.chat_service, self._get_selected_model)
        except Exception as e:
            print("Erro iniciando ChatView:", e)
            self.chat_view = None

        try:
            self.project_view = ProjectAnalyzerView(self.page, self.project_service, self._get_selected_model)
        except Exception as e:
            print("Erro iniciando ProjectAnalyzerView:", e)
            self.project_view = None

        try:
            self.log_fixer_view = LogFixerView(self.page, self.log_fixer_service, self._get_selected_model)
        except Exception as e:
            print("Erro iniciando LogFixerView:", e)
            self.log_fixer_view = None

        try:
            self.automations_view = AutomationsView(self.page, self.automations_service, self._get_selected_model)
        except Exception as e:
            print("Erro iniciando AutomationsView:", e)
            self.automations_view = None

        try:
            self.data_randomizer_view = DataRandomizerView(self.page)
        except Exception as e:
            print("Erro iniciando DataRandomizerView:", e)
            self.data_randomizer_view = None

    def _build_layout(self):
        """Monta layout principal com correções de altura."""
        
        # Sidebar
        # NavigationRail tem expand=True, então empurra o monitor para o fundo
        sidebar = ft.Container(
            content=ft.Column(
                controls=[
                    self.nav_rail,
                    self.api_monitor
                ],
                spacing=0,
                expand=True # Garante que a coluna ocupe todo o Container
            ),
            width=120,
            bgcolor=ft.Colors.GREY_900
        )

        # Stack de Views
        stack_children = []

        def add_to_stack(view_obj, visible=False, name="Indisponível"):
            if view_obj and getattr(view_obj, "container", None):
                view_obj.container.visible = visible
                stack_children.append(view_obj.container)
            else:
                stack_children.append(self._placeholder_container(f"{name} indisponível"))

        add_to_stack(self.chat_view, visible=True, name="Chat")
        add_to_stack(self.project_view, visible=False, name="Projeto")
        add_to_stack(self.log_fixer_view, visible=False, name="Logs")
        add_to_stack(self.automations_view, visible=False, name="Auto")
        add_to_stack(self.data_randomizer_view, visible=False, name="Data")

        # Conteúdo Principal
        main_content_area = ft.Column([
            self.config_bar,
            ft.Stack(stack_children, expand=True)
        ], expand=True, spacing=0)

        # Adiciona à página
        self.page.add(
            ft.Row(
                controls=[
                    sidebar,
                    ft.VerticalDivider(width=1, color=ft.Colors.GREY_800),
                    main_content_area
                ],
                expand=True,
                spacing=0,
                # IMPORTANTE: Garante que a sidebar tenha altura total para calcular o 'expand' interno
                vertical_alignment=ft.CrossAxisAlignment.STRETCH
            )
        )

        self.page.update()

    def _placeholder_container(self, text: str):
        return ft.Container(
            content=ft.Text(text, italic=True),
            alignment=ft.Alignment.CENTER,
            padding=20,
            visible=False,
            expand=True
        )

    # --- Utilities ---

    def _on_model_change(self, e):
        """Atualiza modelo selecionado."""
        self.current_model = e.control.value
        
        # AVISA AO CLIENTE QUAL MODELO ESTÁ ATIVO PARA AJUSTAR LIMITES
        self.gemini.set_current_model(self.current_model)
        
        # Força atualização visual do monitor imediatamente
        self.api_monitor.update_stats()

    def _get_selected_model(self) -> str:
        return getattr(self, "current_model", None)

    def _change_view(self, e):
        idx = e.control.selected_index
        try:
            # Acessa a Stack: Row -> MainCol(2) -> Stack(1)
            main_col = self.page.controls[0].controls[2]
            stack = main_col.controls[1]
            
            for i, control in enumerate(stack.controls):
                control.visible = (i == idx)
                control.update()
        except Exception as ex:
            print(f"Erro ao trocar aba: {ex}")

        self.page.update()

    def _update_status(self, text: str, color):
        self.status_text.value = text
        self.status_text.color = color
        self.status_text.update()

    def _load_models(self):
        key = self.api_key_field.value.strip()
        if not key:
            self._update_status("Insira uma chave API.", ft.Colors.RED)
            return

        try:
            self.gemini.api_key = key
            self.gemini.client = genai.Client(api_key=key)
        except Exception as e:
            print(f"Erro config key: {e}")

        try:
            options, msg = self.gemini.get_available_models()
            if options:
                self.model_dropdown.options = [ft.dropdown.Option(key=o["key"], text=o["text"]) for o in options]
                first_key = options[0]["key"]
                self.model_dropdown.value = first_key
                self.current_model = first_key
                self._update_status(f"{len(options)} modelos", ft.Colors.GREEN)
            else:
                self._update_status(f"{msg}", ft.Colors.RED)
        except Exception as e:
            self._update_status(f"Erro: {str(e)}", ft.Colors.RED)
        finally:
            self.model_dropdown.update()
            self.page.update()

    def _reset_app(self, e):
        """Reseta a aplicação - limpa instâncias, cache e conhecimentos."""
        dlg = ft.AlertDialog(
            title=ft.Text("⚠️ Resetar Aplicação"),
            content=ft.Text(
                "Isto irá:\n"
                "• Limpar todos os conhecimentos\n"
                "• Resetar prompts customizados\n"
                "• Recarregar a aplicação\n\n"
                "Tem certeza?"
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self._close_dialog(dlg)),
                ft.TextButton(
                    "Resetar",
                    on_click=lambda _: self._do_reset(dlg),
                    style=ft.ButtonStyle(color=ft.Colors.RED)
                ),
            ]
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def _do_reset(self, dlg):
        """Executa o reset."""
        try:
            # Reseta knowledge manager
            self.knowledge_mgr.reset()
            dlg.open = False

            # Mostra notificação
            snack = ft.SnackBar(
                ft.Text("✅ App resetado com sucesso! Recarregando..."),
                bgcolor=ft.Colors.GREEN
            )
            self.page.snack_bar = snack
            snack.open = True
            self.page.update()

            # Aguarda e recarrega
            import asyncio
            async def reload():
                await asyncio.sleep(1)
                # Limpa toda a interface e reconstrói
                self.page.clean()
                App(self.page)

            asyncio.create_task(reload())
        except Exception as ex:
            print(f"❌ Erro ao resetar: {ex}")
            snack = ft.SnackBar(
                ft.Text(f"❌ Erro ao resetar: {ex}"),
                bgcolor=ft.Colors.RED
            )
            self.page.snack_bar = snack
            snack.open = True
            self.page.update()

    def _close_dialog(self, dlg):
        """Fecha dialog."""
        dlg.open = False
        self.page.update()

    def _show_settings_dialog(self, e):
        """Mostra dialog simples de gerenciamento de conhecimentos."""
        knowledge_items = []

        # Popula lista de conhecimentos
        for category, items in self.knowledge_mgr.list_knowledge().items():
            for i, item in enumerate(items):
                knowledge_items.append(
                    ft.ListTile(
                        title=ft.Text(f"[{category}] {item['title']}"),
                        subtitle=ft.Text(item['content'][:60] + "..."),
                        trailing=ft.IconButton(
                            ft.Icons.DELETE,
                            on_click=lambda _, cat=category, idx=i: self._delete_knowledge(cat, idx)
                        )
                    )
                )

        # Seção para adicionar novo conhecimento
        new_title = ft.TextField(label="Título", expand=True)
        new_content = ft.TextField(label="Conteúdo", multiline=True, min_lines=3, expand=True)
        new_category = ft.Dropdown(
            label="Categoria",
            value="geral",
            options=[
                ft.dropdown.Option("geral"),
                ft.dropdown.Option("projeto"),
                ft.dropdown.Option("dados"),
                ft.dropdown.Option("automacao"),
            ]
        )

        def add_knowledge(_):
            if new_title.value and new_content.value:
                self.knowledge_mgr.add_knowledge(
                    new_title.value,
                    new_content.value,
                    new_category.value or "geral"
                )
                new_title.value = ""
                new_content.value = ""
                dlg.open = False
                self.page.update()
                self._show_success_snack("✅ Conhecimento adicionado!")

        dlg = ft.AlertDialog(
            title=ft.Text("⚙️ Conhecimentos Anexados"),
            content=ft.Column([
                ft.Text("Seus conhecimentos:", weight="bold", size=14),
                ft.Container(
                    content=ft.ListView(
                        controls=knowledge_items if knowledge_items else [ft.Text("Nenhum conhecimento ainda")],
                        expand=True,
                        spacing=5
                    ),
                    height=250,
                    border=ft.Border.all(1, ft.Colors.GREY_700)
                ),
                ft.Divider(),
                ft.Text("Adicionar novo:", weight="bold", size=14),
                new_title,
                new_category,
                new_content,
            ], expand=True, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Adicionar", on_click=add_knowledge),
                ft.TextButton("Fechar", on_click=lambda _: self._close_dialog(dlg)),
            ]
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def _delete_knowledge(self, category: str, index: int):
        """Deleta um conhecimento."""
        self.knowledge_mgr.remove_knowledge(category, index)
        self.page.update()
        self._show_success_snack(f"✅ Conhecimento removido!")

    def _show_success_snack(self, msg: str):
        """Mostra notificação de sucesso."""
        snack = ft.SnackBar(ft.Text(msg), bgcolor=ft.Colors.GREEN)
        self.page.snack_bar = snack
        snack.open = True
        self.page.update()


async def main(page: ft.Page):
    try:
        App(page)
    except Exception as e:
        print("Erro fatal:", e)
        traceback.print_exc()
        page.snack_bar = ft.SnackBar(ft.Text(f"Erro fatal: {e}"), bgcolor=ft.Colors.RED_400)
        page.snack_bar.open = True
        page.update()

if __name__ == "__main__":
    ft.run(main)