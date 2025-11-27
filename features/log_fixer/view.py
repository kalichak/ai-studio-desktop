"""View de correção de logs com tratamento robusto."""
import flet as ft
import asyncio
from features.log_fixer.service import LogFixerService
from shared.components import create_result_container

class LogFixerView:
    """View de correção de logs - Versão à prova de travamento."""
    
    def __init__(self, page: ft.Page, service: LogFixerService, get_model_fn):
        self.page = page
        self.service = service
        self.get_model_fn = get_model_fn
        self._is_processing = False
        self._current_task = None
        
        # Componentes
        self.log_input = ft.TextField(
            label="Cole o log de erro aqui",
            multiline=True,
            min_lines=5,
            hint_text="Exemplo: Traceback (most recent call last):\n  File 'app.py', line 42..."
        )
        
        self.log_result = ft.Markdown(
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            code_theme="atom-one-dark"
        )
        
        self.btn_fix = ft.ElevatedButton(
            "Analisar e Corrigir",
            icon=ft.Icons.BUG_REPORT,
            on_click=self._fix_log,
            disabled=False
        )
        
        self.btn_cancel = ft.ElevatedButton(
            "Cancelar",
            icon=ft.Icons.STOP,
            on_click=self._cancel_fix,
            visible=False,
            color=ft.Colors.RED_400
        )
        
        self.btn_clear = ft.IconButton(
            ft.Icons.CLEAR,
            on_click=self._clear_log,
            tooltip="Limpar log"
        )
        
        self.container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Corretor de Logs", size=18, weight=ft.FontWeight.BOLD),
                    self.btn_clear
                ]),
                self.log_input,
                ft.Row([
                    self.btn_fix,
                    self.btn_cancel
                ]),
                ft.Divider(),
                create_result_container(self.log_result)
            ]),
            padding=20,
            visible=False,
            expand=True
        )
    
    async def _fix_log(self, e):
        """Analisa e corrige log com tratamento de erros."""
        if not self.log_input.value or not self.log_input.value.strip():
            self._show_error("Cole um log de erro primeiro")
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
        self.log_result.value = "🔍 Analisando erro..."
        self.page.update()
        
        try:
            # Cria task cancelável
            self._current_task = asyncio.create_task(
                self._process_fix(self.log_input.value, model)
            )
            await self._current_task
        
        except asyncio.CancelledError:
            self.log_result.value += "\n\n⚠️ **Análise cancelada pelo usuário**"
            self.page.update()
        
        except Exception as e:
            self.log_result.value = f"❌ **Erro durante análise:** {str(e)}\n\nTente novamente."
            self.page.update()
        
        finally:
            self._set_processing_state(False)
            self._current_task = None
    
    async def _process_fix(self, log_text: str, model: str):
        """Processa correção com feedback em tempo real."""
        full_response = ""
        
        try:
            async for chunk in self.service.analyze_and_fix(log_text, model):
                full_response += chunk
                self.log_result.value = full_response
                self.page.update()
                
                # Permite cancelamento
                await asyncio.sleep(0)
        
        except asyncio.CancelledError:
            raise
        
        except Exception as e:
            error_msg = f"\n\n❌ Erro: {str(e)}"
            self.log_result.value = full_response + error_msg
            self.page.update()
    
    async def _cancel_fix(self, e):
        """Cancela correção em andamento."""
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
            self.service.client.cancel_current_operation()
            self._show_success("⏹️ Análise cancelada")
    
    def _clear_log(self, e):
        """Limpa campos."""
        self.log_input.value = ""
        self.log_result.value = ""
        self.page.update()
        self._show_success("🗑️ Campos limpos")
    
    def _set_processing_state(self, is_processing: bool):
        """Altera estado dos controles."""
        self._is_processing = is_processing
        self.log_input.disabled = is_processing
        self.btn_fix.disabled = is_processing
        self.btn_cancel.visible = is_processing
        self.btn_clear.disabled = is_processing
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