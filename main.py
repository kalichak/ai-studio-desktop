"""
main.py - AI Studio Desktop (todas as features ativadas)

Dependências (ver requirements.txt):
- flet
- google-generativeai
- python-dotenv
- pandas
- openpyxl
"""

import flet as ft
import traceback
from config.settings import settings
from core.gemini_client import GeminiClient

# Services
from features.chat.service import ChatService
from features.project_analyzer.service import ProjectAnalyzerService
from features.log_fixer.service import LogFixerService
from features.automations.service import AutomationsService
# Data Randomizer service is used inside the view; view imports it
from features.data_randomizer.view import DataRandomizerView

# Views
from features.chat.view import ChatView
from features.project_analyzer.view import ProjectAnalyzerView
from features.log_fixer.view import LogFixerView
from features.automations.view import AutomationsView

class App:
    """Aplicação principal - inicializa serviços e views."""

    def __init__(self, page: ft.Page):
        self.page = page
        self._setup_page()

        # --- Core client (Gemini) ---
        # Se a key estiver no .env, o GeminiClient poderá inicializar com ela
        try:
            self.gemini = GeminiClient(api_key=settings.GEMINI_API_KEY) if getattr(settings, "GEMINI_API_KEY", "") else GeminiClient()
        except Exception:
            # Em caso de erro ao inicializar o cliente, instanciamos vazio (algumas features podem operar offline)
            self.gemini = GeminiClient()

        # --- Services (criar antes das views) ---
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

        # --- UI: Config section (API key + modelo) ---
        self.api_key_field = ft.TextField(
            label="Gemini API Key",
            password=True,
            width=360,
            value=settings.GEMINI_API_KEY,
            hint_text="Cole sua chave aqui"
        )

        self.model_dropdown = ft.Dropdown(
            label="Modelo",
            width=360,
            hint_text="Carregue a chave primeiro",
            on_change=self._on_model_change
        )

        self.status_text = ft.Text("", size=12)

        self.config_bar = ft.Container(
            content=ft.Row([
                self.api_key_field,
                ft.IconButton(ft.Icons.REFRESH, on_click=lambda _: self._load_models(), tooltip="Recarregar Modelos"),
                self.model_dropdown,
                self.status_text
            ], alignment=ft.MainAxisAlignment.START, spacing=12),
            padding=10,
            bgcolor=ft.Colors.BLACK12
        )

        # --- NavigationRail (todas as features) ---
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            destinations=[
                ft.NavigationRailDestination(icon=ft.Icons.CHAT, label="Chat"),
                ft.NavigationRailDestination(icon=ft.Icons.FOLDER, label="Projeto"),
                ft.NavigationRailDestination(icon=ft.Icons.TERMINAL, label="Logs"),
                ft.NavigationRailDestination(icon=ft.Icons.AUTO_MODE, label="Automações"),
                ft.NavigationRailDestination(icon=ft.Icons.SHUFFLE, label="Randomizar"),
            ],
            on_change=self._change_view,
        )

        # --- Views (criar antes do layout) ---
        # Usamos try/except para garantir que, se um view falhar na importação, o app não quebre.
        try:
            self.chat_view = ChatView(self.page, self.chat_service, self._get_selected_model)
        except Exception as e:
            print("Erro iniciando ChatView:", e)
            traceback.print_exc()
            self.chat_view = None

        try:
            self.project_view = ProjectAnalyzerView(self.page, self.project_service, self._get_selected_model)
        except Exception as e:
            print("Erro iniciando ProjectAnalyzerView:", e)
            traceback.print_exc()
            self.project_view = None

        try:
            self.log_fixer_view = LogFixerView(self.page, self.log_fixer_service, self._get_selected_model)
        except Exception as e:
            print("Erro iniciando LogFixerView:", e)
            traceback.print_exc()
            self.log_fixer_view = None

        try:
            self.automations_view = AutomationsView(self.page, self.automations_service, self._get_selected_model)
        except Exception as e:
            print("Erro iniciando AutomationsView:", e)
            traceback.print_exc()
            self.automations_view = None

        try:
            self.data_randomizer_view = DataRandomizerView(self.page)
        except Exception as e:
            print("Erro iniciando DataRandomizerView:", e)
            traceback.print_exc()
            self.data_randomizer_view = None

        # --- Layout (stack das views) ---
        self._build_layout()

        # Auto-load se tiver chave no .env
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

    def _build_layout(self):
        """Monta layout principal com verificação de views existentes."""
        # Lista de containers visíveis (na ordem de abas)
        stack_children = []

        # Chat view
        if self.chat_view and getattr(self.chat_view, "container", None):
            self.chat_view.container.visible = True  # default first
            stack_children.append(self.chat_view.container)
        else:
            # fallback: placeholder
            stack_children.append(self._placeholder_container("Chat indisponível"))

        # Project view
        if self.project_view and getattr(self.project_view, "container", None):
            self.project_view.container.visible = False
            stack_children.append(self.project_view.container)
        else:
            stack_children.append(self._placeholder_container("Project Analyzer indisponível"))

        # Log fixer view
        if self.log_fixer_view and getattr(self.log_fixer_view, "container", None):
            self.log_fixer_view.container.visible = False
            stack_children.append(self.log_fixer_view.container)
        else:
            stack_children.append(self._placeholder_container("Log Fixer indisponível"))

        # Automations
        if self.automations_view and getattr(self.automations_view, "container", None):
            self.automations_view.container.visible = False
            stack_children.append(self.automations_view.container)
        else:
            stack_children.append(self._placeholder_container("Automações indisponível"))

        # Data Randomizer
        if self.data_randomizer_view and getattr(self.data_randomizer_view, "container", None):
            self.data_randomizer_view.container.visible = False
            stack_children.append(self.data_randomizer_view.container)
        else:
            stack_children.append(self._placeholder_container("Randomizer indisponível"))

        # Monta UI
        main_column = ft.Column([
            self.config_bar,
            ft.Stack(stack_children, expand=True)
        ], expand=True)

        self.page.add(
            ft.Row([
                self.nav_rail,
                ft.VerticalDivider(width=1),
                main_column
            ], expand=True)
        )

        self.page.update()

    def _placeholder_container(self, text: str):
        """Gera container simples para fallback quando uma view não existir."""
        return ft.Container(
            content=ft.Center(ft.Text(text, italic=True)),
            padding=20,
            visible=False,
            expand=True
        )

    # --- Event handlers / utilities ---

    def _on_model_change(self, e):
        """Atualiza modelo selecionado."""
        self.current_model = e.control.value

    def _get_selected_model(self) -> str:
        """Retorna modelo atualmente selecionado (ou None)."""
        return getattr(self, "current_model", None)

    def _change_view(self, e):
        """Alterna entre views (mapear índices para containers seguros)."""
        idx = e.control.selected_index

        # Map indices -> containers in same order as nav_rail/destinations
        containers = []

        # Build list in same order as stack_children in _build_layout
        # Use getattr to avoid AttributeError if view missing
        containers.append(getattr(self.chat_view, "container", None))
        containers.append(getattr(self.project_view, "container", None))
        containers.append(getattr(self.log_fixer_view, "container", None))
        containers.append(getattr(self.automations_view, "container", None))
        containers.append(getattr(self.data_randomizer_view, "container", None))

        # Hide all first
        for c in containers:
            if c is not None:
                c.visible = False

        # Show selected (if exists), otherwise the placeholder created earlier will be at same position
        selected = containers[idx] if idx < len(containers) else None
        if selected is not None:
            selected.visible = True
        else:
            # show placeholder container that is at same stack index: we can rely on stack order
            pass

        self.page.update()

    def _update_status(self, text: str, color):
        """Atualiza texto de status (barra superior)."""
        self.status_text.value = text
        self.status_text.color = color
        self.page.update()

    def _show_snackbar(self, msg: str, color=ft.Colors.BLUE):
        """Exibe snackbar."""
        self.page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=color)
        self.page.snack_bar.open = True
        self.page.update()

    def _load_models(self):
        """Carrega modelos disponíveis usando o GeminiClient."""
        key = self.api_key_field.value.strip()
        if not key:
            self._update_status("Insira uma chave API.", ft.Colors.RED)
            return

        # Atualiza o client com nova key (se suportado)
        try:
            # Recreate client with provided API key if constructor supports it
            self.gemini = GeminiClient(api_key=key)
        except Exception:
            try:
                # fallback: set attribute if class implemented differently
                self.gemini.api_key = key
            except Exception:
                pass

        # Tenta obter modelos de maneira segura
        try:
            options, msg = self.gemini.get_available_models()  # deve retornar (list, message) conforme seu client
            if options:
                self.model_dropdown.options = [ft.dropdown.Option(key=o["key"], text=o["text"]) for o in options]
                self.model_dropdown.value = options[0]["key"]
                self.current_model = options[0]["key"]
                self._update_status(f"✅ {len(options)} modelos disponíveis", ft.Colors.GREEN)
            else:
                self._update_status(f"❌ {msg}", ft.Colors.RED)
        except Exception as e:
            self._update_status(f"Erro ao carregar modelos: {e}", ft.Colors.RED)
            print("Erro _load_models:", e)
        finally:
            self.page.update()


async def main(page: ft.Page):
    """Entry point da app (flet)."""
    try:
        App(page)
    except Exception as e:
        # Erro não esperado: mostramos stack no console e um snackbar leve
        print("Erro na inicialização da App:", e)
        traceback.print_exc()
        page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao iniciar a aplicação: {e}"), bgcolor=ft.Colors.RED_400)
        page.snack_bar.open = True
        page.update()

if __name__ == "__main__":
    ft.app(target=main)
