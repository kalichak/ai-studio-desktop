"""View de análise de projeto com tratamento robusto."""
import flet as ft
import asyncio
from features.project_analyzer.service import ProjectAnalyzerService
from shared.components import create_result_container

class ProjectAnalyzerView:
    """View de análise de projeto - Versão à prova de travamento."""
    
    def __init__(self, page: ft.Page, service: ProjectAnalyzerService, get_model_fn):
        self.page = page
        self.service = service
        self.get_model_fn = get_model_fn
        self._is_processing = False
        self._current_task = None
        
        # Componentes
        self.folder_path = ft.Text("Nenhuma pasta selecionada", italic=True)
        
        self.project_result = ft.Markdown(
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            code_theme="atom-one-dark"
        )
        
        self.btn_analyze = ft.ElevatedButton(
            "Analisar Projeto",
            icon=ft.Icons.ANALYTICS,
            on_click=self._analyze_project,
            disabled=False
        )
        
        self.btn_cancel = ft.ElevatedButton(
            "Cancelar",
            icon=ft.Icons.STOP,
            on_click=self._cancel_analysis,
            visible=False,
            color=ft.Colors.RED_400
        )
        
        self.file_picker = ft.FilePicker(on_result=self._on_folder_selected)
        self.page.overlay.append(self.file_picker)
        
        self.container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.ElevatedButton(
                        "Selecionar Pasta",
                        icon=ft.Icons.FOLDER,
                        on_click=lambda _: self.file_picker.get_directory_path()
                    ),
                    self.folder_path
                ]),
                ft.Row([
                    self.btn_analyze,
                    self.btn_cancel
                ]),
                ft.Divider(),
                create_result_container(self.project_result)
            ]),
            padding=20,
            visible=False,
            expand=True
        )
    
    def _on_folder_selected(self, e: ft.FilePickerResultEvent):
        """Callback de seleção de pasta."""
        if e.path:
            self.folder_path.value = e.path
            self.folder_path.update()
    
    async def _analyze_project(self, e):
        """Analisa projeto com tratamento de erros."""
        path = self.folder_path.value
        
        if "Nenhuma" in path:
            self._show_error("Selecione uma pasta primeiro")
            return
        
        model = self.get_model_fn()
        if not model:
            self._show_error("Selecione um modelo primeiro")
            return
        
        if self._is_processing:
            self._show_error("Análise já em andamento")
            return
        
        # Prepara UI
        self._set_processing_state(True)
        self.project_result.value = ""
        
        try:
            # Cria task cancelável
            self._current_task = asyncio.create_task(
                self._process_analysis(path, model)
            )
            await self._current_task
        
        except asyncio.CancelledError:
            self.project_result.value += "\n\n⚠️ **Análise cancelada pelo usuário**"
            self.page.update()
        
        except Exception as e:
            self.project_result.value = f"❌ **Erro durante análise:** {str(e)}\n\nTente novamente."
            self.page.update()
        
        finally:
            self._set_processing_state(False)
            self._current_task = None
    
    async def _process_analysis(self, path: str, model: str):
        """Processa análise com feedback em tempo real."""
        full_response = ""
        
        try:
            async for update in self.service.analyze(path, model):
                status = update.get("status")
                
                if status in ["reading", "analyzing"]:
                    self.btn_analyze.text = update["text"]
                    self.page.update()
                
                elif status == "streaming":
                    full_response += update["text"]
                    self.project_result.value = full_response
                    self.page.update()
                
                elif status == "error":
                    self.project_result.value = update["text"]
                    self.page.update()
                    break
                
                # Permite cancelamento
                await asyncio.sleep(0)
        
        except asyncio.CancelledError:
            raise
        
        except Exception as e:
            error_msg = f"❌ Erro: {str(e)}"
            self.project_result.value = full_response + "\n\n" + error_msg
            self.page.update()
    
    async def _cancel_analysis(self, e):
        """Cancela análise em andamento."""
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
            self.service.client.cancel_current_operation()
            self._show_success("⏹️ Análise cancelada")
    
    def _set_processing_state(self, is_processing: bool):
        """Altera estado dos controles."""
        self._is_processing = is_processing
        self.btn_analyze.disabled = is_processing
        self.btn_cancel.visible = is_processing
        
        if not is_processing:
            self.btn_analyze.text = "Analisar Projeto"
        
        self.page.update()
    
    def _show_error(self, msg: str):
        """Exibe erro."""
        self.page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=ft.Colors.RED_400)
        self.page.snack_bar.open = True
        self.page.update()
    
    def _show_success(self, msg: str):
        """Exibe sucesso."""
        self.page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=ft.Colors.GREEN)
        self.page.snack_bar.open = True
        self.page.update()