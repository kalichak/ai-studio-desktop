"""Interface da Central de Automações."""
import flet as ft
import asyncio
from features.automations.service import AutomationsService

class AutomationsView:
    """Central de Automações - IA + Scripts externos."""
    
    def __init__(self, page: ft.Page, service: AutomationsService, get_model_fn):
        self.page = page
        self.service = service
        self.get_model_fn = get_model_fn
        self._is_processing = False
        self._current_task = None
        
        # File picker para scripts
        self.script_picker = ft.FilePicker(on_result=self._on_script_selected)
        self.page.overlay.append(self.script_picker)
        
        # Componentes
        self._build_components()
        
        self.container = ft.Container(
            content=ft.Column([
                self._build_header(),
                ft.Divider(),
                ft.Row([
                    self._build_automations_list(),
                    ft.VerticalDivider(width=1),
                    self._build_execution_panel()
                ], expand=True, spacing=20)
            ], scroll=ft.ScrollMode.AUTO),
            padding=20,
            visible=False,
            expand=True
        )
    
    def _build_components(self):
        """Inicializa componentes."""
        self.automations_list = ft.ListView(expand=True, spacing=10)
        
        self.input_code = ft.TextField(
            label="Entrada (Cole código, texto, etc)",
            multiline=True,
            min_lines=8,
            max_lines=15,
            hint_text="Cole aqui o código ou texto para processar..."
        )
        
        self.result_output = ft.Markdown(
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            code_theme="atom-one-dark"
        )
        
        self.btn_run = ft.ElevatedButton(
            "Executar",
            icon=ft.Icons.PLAY_ARROW,
            on_click=self._run_automation,
            disabled=True
        )
        
        self.btn_cancel = ft.ElevatedButton(
            "Cancelar",
            icon=ft.Icons.STOP,
            on_click=self._cancel_automation,
            visible=False,
            color=ft.Colors.RED_400
        )
        
        self.selected_automation = None
    
    def _build_header(self):
        """Cabeçalho."""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.AUTO_MODE, size=30),
                    ft.Text("Central de Automações", size=24, weight=ft.FontWeight.BOLD)
                ], spacing=10),
                ft.Text(
                    "Execute automações com IA ou scripts/apps personalizados",
                    size=14,
                    color=ft.Colors.GREY_500
                ),
                ft.Row([
                    ft.ElevatedButton(
                        "Adicionar Script/App",
                        icon=ft.Icons.ADD,
                        on_click=self._show_add_script_dialog
                    ),
                    ft.ElevatedButton(
                        "Gerenciar Scripts",
                        icon=ft.Icons.SETTINGS,
                        on_click=self._show_manage_scripts
                    )
                ], spacing=10)
            ]),
            padding=10,
            border=ft.border.all(1, ft.Colors.GREY_800),
            border_radius=10
        )
    
    def _build_automations_list(self):
        """Painel de lista de automações."""
        return ft.Container(
            content=ft.Column([
                ft.Text("📋 Automações Disponíveis", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=self.automations_list,
                    border=ft.border.all(1, ft.Colors.GREY_800),
                    border_radius=5,
                    padding=10,
                    expand=True
                )
            ]),
            width=350
        )
    
    def _build_execution_panel(self):
        """Painel de execução."""
        return ft.Container(
            content=ft.Column([
                ft.Text("⚙️ Executar Automação", size=16, weight=ft.FontWeight.BOLD),
                self.input_code,
                ft.Row([self.btn_run, self.btn_cancel], spacing=10),
                ft.Divider(),
                ft.Text("📤 Resultado", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Column([self.result_output], scroll=ft.ScrollMode.AUTO),
                    border=ft.border.all(1, ft.Colors.GREY_800),
                    border_radius=5,
                    padding=10,
                    expand=True
                )
            ], spacing=10),
            expand=True
        )
    
    def _load_automations(self):
        """Carrega lista de automações."""
        self.automations_list.controls.clear()
        automations = self.service.get_all_automations()
        
        for auto in automations:
            card = self._create_automation_card(auto)
            self.automations_list.controls.append(card)
        
        self.page.update()
    
    def _create_automation_card(self, automation: dict):
        """Cria card de automação."""
        is_selected = (self.selected_automation == automation["id"])
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(automation["icon"], size=24),
                    ft.Column([
                        ft.Text(automation["name"], weight=ft.FontWeight.BOLD, size=14),
                        ft.Text(automation["description"], size=11, color=ft.Colors.GREY_500)
                    ], spacing=2, expand=True)
                ], spacing=10),
                ft.Row([
                    ft.Chip(
                        label=ft.Text(automation["type"].upper(), size=10),
                        bgcolor=ft.Colors.BLUE_900 if automation["type"] == "ai" else ft.Colors.GREEN_900
                    )
                ]) if automation["type"] in ["ai", "script"] else None
            ], spacing=5),
            padding=10,
            border=ft.border.all(2 if is_selected else 1, ft.Colors.BLUE if is_selected else ft.Colors.GREY_800),
            border_radius=8,
            bgcolor=ft.Colors.BLUE_GREY_900 if is_selected else ft.Colors.GREY_900,
            on_click=lambda e, auto_id=automation["id"]: self._select_automation(auto_id)
        )
    
    def _select_automation(self, automation_id: str):
        """Seleciona automação."""
        self.selected_automation = automation_id
        self.btn_run.disabled = False
        self._load_automations()  # Recarrega para atualizar seleção visual
        self._show_success(f"✅ Automação selecionada")
    
    async def _run_automation(self, e):
        """Executa automação selecionada."""
        if not self.selected_automation:
            self._show_error("Selecione uma automação")
            return
        
        if not self.input_code.value:
            self._show_error("Cole o código/texto de entrada")
            return
        
        model = self.get_model_fn()
        if not model:
            self._show_error("Selecione um modelo")
            return
        
        self._set_processing_state(True)
        self.result_output.value = "🔄 Processando...\n\n"
        self.page.update()
        
        try:
            self._current_task = asyncio.create_task(
                self._process_automation()
            )
            await self._current_task
        
        except asyncio.CancelledError:
            self.result_output.value += "\n\n⚠️ **Execução cancelada pelo usuário**"
            self.page.update()
        
        except Exception as ex:
            self.result_output.value += f"\n\n❌ **Erro:** {str(ex)}"
            self.page.update()
        
        finally:
            self._set_processing_state(False)
            self._current_task = None
    
    async def _process_automation(self):
        """Processa automação com feedback."""
        full_response = ""
        model = self.get_model_fn()
        
        async for chunk in self.service.run_automation(
            self.selected_automation,
            self.input_code.value,
            model
        ):
            full_response += chunk
            self.result_output.value = full_response
            self.page.update()
            await asyncio.sleep(0)
    
    async def _cancel_automation(self, e):
        """Cancela execução."""
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
            self._show_success("⏹️ Execução cancelada")
    
    def _set_processing_state(self, is_processing: bool):
        """Altera estado dos controles."""
        self._is_processing = is_processing
        self.input_code.disabled = is_processing
        self.btn_run.disabled = is_processing
        self.btn_cancel.visible = is_processing
        self.page.update()
    
    def _show_add_script_dialog(self, e):
        """Mostra dialog para adicionar script."""
        name_field = ft.TextField(label="Nome do Script/App", width=400)
        desc_field = ft.TextField(label="Descrição", width=400)
        path_field = ft.TextField(
            label="Caminho do executável",
            hint_text="/caminho/para/script.py ou script.exe",
            width=400
        )
        
        def add_script(e):
            if not name_field.value or not path_field.value:
                self._show_error("Preencha nome e caminho")
                return
            
            self.service.register_external_script(
                name_field.value,
                path_field.value,
                desc_field.value
            )
            
            dlg.open = False
            self.page.update()
            self._load_automations()
            self._show_success(f"✅ Script '{name_field.value}' adicionado")
        
        def select_file(e):
            self.script_picker.pick_files(
                dialog_title="Selecione o executável/script"
            )
        
        dlg = ft.AlertDialog(
            title=ft.Text("Adicionar Script/App"),
            content=ft.Column([
                name_field,
                desc_field,
                ft.Row([
                    path_field,
                    ft.IconButton(ft.Icons.FOLDER, on_click=select_file)
                ])
            ], tight=True, spacing=15),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: setattr(dlg, 'open', False) or self.page.update()),
                ft.TextButton("Adicionar", on_click=add_script)
            ]
        )
        
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()
    
    def _on_script_selected(self, e: ft.FilePickerResultEvent):
        """Callback de seleção de script."""
        # TODO: Implementar quando necessário
        pass
    
    def _show_manage_scripts(self, e):
        """Mostra dialog de gerenciamento."""
        scripts = [s for s in self.service.external_scripts]
        
        if not scripts:
            self._show_error("Nenhum script registrado ainda")
            return
        
        scripts_list = ft.ListView(height=300)
        
        for script in scripts:
            scripts_list.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.CODE),
                    title=ft.Text(script["name"]),
                    subtitle=ft.Text(script["path"]),
                    trailing=ft.IconButton(
                        ft.Icons.DELETE,
                        on_click=lambda e, sid=script["id"]: self._remove_script(sid)
                    )
                )
            )
        
        dlg = ft.AlertDialog(
            title=ft.Text("Gerenciar Scripts"),
            content=scripts_list,
            actions=[
                ft.TextButton("Fechar", on_click=lambda _: setattr(dlg, 'open', False) or self.page.update())
            ]
        )
        
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()
    
    def _remove_script(self, script_id: str):
        """Remove script."""
        self.service.remove_script(script_id)
        self._load_automations()
        self._show_success("🗑️ Script removido")
        
        # Fecha dialog
        if self.page.dialog:
            self.page.dialog.open = False
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