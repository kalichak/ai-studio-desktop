"""View de análise de projeto com ferramentas de exportação."""
import flet as ft
import asyncio
from features.project_analyzer.service import ProjectAnalyzerService
from shared.components import create_result_container

class ProjectAnalyzerView:
    """View de análise de projeto - Versão à prova de travamento com Exportação."""
    
    def __init__(self, page: ft.Page, service: ProjectAnalyzerService, get_model_fn):
        self.page = page
        self.service = service
        self.get_model_fn = get_model_fn
        self._is_processing = False
        self._current_task = None
        
        # --- Componentes de Arquivo ---
        self.folder_path = ft.Text("Nenhuma pasta selecionada", italic=True)
        
        # File Pickers
        self.folder_picker = ft.FilePicker(on_result=self._on_folder_selected)
        self.save_picker = ft.FilePicker(on_result=self._on_save_file)
        self.page.overlay.extend([self.folder_picker, self.save_picker])
        
        # --- Área de Resultado ---
        self.project_result = ft.Markdown(
            selectable=True, # Mantém selecionável, mas os botões ajudam
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            code_theme="atom-one-dark"
        )
        
        # --- Botões de Ação ---
        self.btn_analyze = ft.ElevatedButton(
            "Analisar Projeto",
            icon=ft.Icons.ANALYTICS,
            on_click=self._analyze_project,
        )
        
        self.btn_cancel = ft.ElevatedButton(
            "Cancelar",
            icon=ft.Icons.STOP,
            on_click=self._cancel_analysis,
            visible=False,
            color=ft.Colors.RED_400
        )

        # Botões de Exportação (Inicialmente desabilitados)
        self.btn_copy = ft.IconButton(
            icon=ft.Icons.COPY,
            tooltip="Copiar tudo para área de transferência",
            on_click=self._copy_to_clipboard,
            disabled=True
        )
        
        self.btn_save = ft.IconButton(
            icon=ft.Icons.SAVE_ALT,
            tooltip="Salvar relatório em arquivo (.md)",
            on_click=lambda _: self.save_picker.save_file(
                allowed_extensions=["md", "txt"],
                file_name="analise_projeto.md"
            ),
            disabled=True
        )
        
        # --- Layout ---
        self.container = ft.Container(
            content=ft.Column([
                # 1. Seleção de Pasta
                ft.Row([
                    ft.ElevatedButton(
                        "Selecionar Pasta",
                        icon=ft.Icons.FOLDER,
                        on_click=lambda _: self.folder_picker.get_directory_path()
                    ),
                    self.folder_path
                ]),
                
                # 2. Botões de Controle
                ft.Row([
                    self.btn_analyze,
                    self.btn_cancel
                ]),
                
                ft.Divider(),
                
                # 3. Barra de Ferramentas do Resultado
                ft.Row(
                    controls=[
                        ft.Text("Resultado da Análise:", weight=ft.FontWeight.BOLD, size=16),
                        ft.Row([self.btn_copy, self.btn_save])
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                
                # 4. Conteúdo do Resultado (Com scroll)
                create_result_container(self.project_result)
            ]),
            padding=20,
            visible=False,
            expand=True
        )
    
    # --- Lógica de Arquivos ---
    
    def _on_folder_selected(self, e: ft.FilePickerResultEvent):
        """Callback de seleção de pasta."""
        if e.path:
            self.folder_path.value = e.path
            self.folder_path.update()

    def _on_save_file(self, e: ft.FilePickerResultEvent):
        """Salva o conteúdo do markdown em um arquivo."""
        if e.path:
            try:
                with open(e.path, 'w', encoding='utf-8') as f:
                    f.write(self.project_result.value)
                self._show_success(f"Arquivo salvo com sucesso em: {e.path}")
            except Exception as ex:
                self._show_error(f"Erro ao salvar arquivo: {ex}")

    def _copy_to_clipboard(self, e):
        """Copia todo o conteúdo para o clipboard."""
        if self.project_result.value:
            self.page.set_clipboard(self.project_result.value)
            self._show_success("📋 Conteúdo copiado para a área de transferência!")

    # --- Lógica de Análise ---
    
    async def _analyze_project(self, e):
        path = self.folder_path.value
        
        if "Nenhuma" in path:
            self._show_error("Selecione uma pasta primeiro")
            return
        
        model = self.get_model_fn()
        if not model:
            self._show_error("Selecione um modelo primeiro")
            return
        
        if self._is_processing: return
        
        self._set_processing_state(True)
        self.project_result.value = ""
        
        try:
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
            # Habilita botões de exportação se houver conteúdo
            if self.project_result.value:
                self.btn_copy.disabled = False
                self.btn_save.disabled = False
                self.page.update()
    
    async def _process_analysis(self, path: str, model: str):
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
                
                await asyncio.sleep(0)
        
        except asyncio.CancelledError:
            raise
        except Exception as e:
            self.project_result.value = full_response + f"\n\n❌ Erro: {str(e)}"
            self.page.update()
    
    async def _cancel_analysis(self, e):
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
            self.service.client.cancel_current_operation()
            self._show_success("⏹️ Análise cancelada")
    
    def _set_processing_state(self, is_processing: bool):
        self._is_processing = is_processing
        self.btn_analyze.disabled = is_processing
        self.btn_cancel.visible = is_processing
        
        # Desabilita exportação durante processamento
        if is_processing:
            self.btn_copy.disabled = True
            self.btn_save.disabled = True
        
        if not is_processing:
            self.btn_analyze.text = "Analisar Projeto"
        
        self.page.update()
    
    def _show_error(self, msg: str):
        self.page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=ft.Colors.RED_400)
        self.page.snack_bar.open = True
        self.page.update()
    
    def _show_success(self, msg: str):
        self.page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=ft.Colors.GREEN)
        self.page.snack_bar.open = True
        self.page.update()