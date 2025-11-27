"""Interface de processamento de documentos."""
import flet as ft
import asyncio
from features.document_processor.service import DocumentProcessorService

class DocumentProcessorView:
    """View de processamento de documentos CSV/Excel."""
    
    def __init__(self, page: ft.Page, service: DocumentProcessorService, get_model_fn):
        self.page = page
        self.service = service
        self.get_model_fn = get_model_fn
        self._is_processing = False
        
        # File Picker
        self.file_picker = ft.FilePicker(on_result=self._on_file_selected)
        self.page.overlay.append(self.file_picker)
        
        # Componentes
        self._build_components()
        
        self.container = ft.Container(
            content=ft.Column([
                self._build_header(),
                ft.Divider(),
                ft.Row([
                    self._build_left_panel(),
                    ft.VerticalDivider(width=1),
                    self._build_right_panel()
                ], expand=True, spacing=20)
            ], scroll=ft.ScrollMode.AUTO),
            padding=20,
            visible=False,
            expand=True
        )
    
    def _build_components(self):
        """Inicializa componentes."""
        # Status do arquivo
        self.file_status = ft.Text("Nenhum arquivo carregado", italic=True)
        
        # Tabela de preview
        self.data_table = ft.DataTable(
            columns=[],
            rows=[],
            border=ft.border.all(1, ft.Colors.GREY_800),
            border_radius=5,
            horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_700)
        )
        
        # Análise de colunas
        self.columns_list = ft.ListView(expand=True, spacing=5)
        
        # Filtros
        self.filter_column = ft.Dropdown(label="Coluna", width=200)
        self.filter_operation = ft.Dropdown(
            label="Operação",
            width=150,
            options=[
                ft.dropdown.Option("equals", "Igual a"),
                ft.dropdown.Option("contains", "Contém"),
                ft.dropdown.Option("greater", "Maior que"),
                ft.dropdown.Option("less", "Menor que"),
            ],
            value="contains"
        )
        self.filter_value = ft.TextField(label="Valor", width=200)
        
        # Resultado da análise com IA
        self.ai_result = ft.Markdown(
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            code_theme="atom-one-dark"
        )
        
        self.ai_question = ft.TextField(
            label="Pergunte sobre os dados",
            hint_text="Ex: Qual a média da coluna idade?",
            expand=True
        )
    
    def _build_header(self):
        """Cabeçalho com controles principais."""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.TABLE_CHART, size=30),
                    ft.Text("Processador de Documentos", size=24, weight=ft.FontWeight.BOLD)
                ], spacing=10),
                ft.Row([
                    ft.ElevatedButton(
                        "Carregar Arquivo",
                        icon=ft.Icons.UPLOAD_FILE,
                        on_click=lambda _: self.file_picker.pick_files(
                            allowed_extensions=["csv", "xlsx", "xls", "txt"]
                        )
                    ),
                    self.file_status,
                    ft.ElevatedButton(
                        "Exportar",
                        icon=ft.Icons.DOWNLOAD,
                        on_click=self._export_data,
                        disabled=True
                    )
                ], spacing=15)
            ]),
            padding=10,
            border=ft.border.all(1, ft.Colors.GREY_800),
            border_radius=10
        )
    
    def _build_left_panel(self):
        """Painel esquerdo - Análise e filtros."""
        return ft.Container(
            content=ft.Column([
                ft.Text("📊 Análise de Colunas", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=self.columns_list,
                    border=ft.border.all(1, ft.Colors.GREY_800),
                    border_radius=5,
                    padding=10,
                    height=200
                ),
                ft.Divider(),
                ft.Text("🔍 Filtros", size=16, weight=ft.FontWeight.BOLD),
                self.filter_column,
                self.filter_operation,
                self.filter_value,
                ft.ElevatedButton(
                    "Aplicar Filtro",
                    icon=ft.Icons.FILTER_ALT,
                    on_click=self._apply_filter,
                    width=200
                ),
                ft.Divider(),
                ft.Text("🤖 Análise com IA", size=16, weight=ft.FontWeight.BOLD),
                self.ai_question,
                ft.ElevatedButton(
                    "Analisar",
                    icon=ft.Icons.PSYCHOLOGY,
                    on_click=self._analyze_with_ai,
                    width=200
                ),
                ft.Container(
                    content=ft.Column([self.ai_result], scroll=ft.ScrollMode.AUTO),
                    border=ft.border.all(1, ft.Colors.GREY_800),
                    border_radius=5,
                    padding=10,
                    height=150
                )
            ], spacing=10),
            width=400
        )
    
    def _build_right_panel(self):
        """Painel direito - Preview dos dados."""
        return ft.Container(
            content=ft.Column([
                ft.Text("📄 Preview dos Dados", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Column([self.data_table], scroll=ft.ScrollMode.ALWAYS),
                    border=ft.border.all(1, ft.Colors.GREY_800),
                    border_radius=5,
                    padding=10,
                    expand=True
                )
            ]),
            expand=True
        )
    
    def _on_file_selected(self, e: ft.FilePickerResultEvent):
        """Callback de seleção de arquivo."""
        if not e.files or len(e.files) == 0:
            return
        
        file_path = e.files[0].path
        success, message, df = self.service.load_file(file_path)
        
        if success:
            self.file_status.value = message
            self.file_status.color = ft.Colors.GREEN
            self._update_preview(df)
            self._update_column_analysis()
            self._show_success(message)
        else:
            self.file_status.value = message
            self.file_status.color = ft.Colors.RED
            self._show_error(message)
        
        self.page.update()
    
    def _update_preview(self, df):
        """Atualiza preview da tabela."""
        # Limita a 10 linhas e 10 colunas para performance
        preview_df = df.head(10).iloc[:, :10]
        
        # Colunas
        self.data_table.columns = [
            ft.DataColumn(ft.Text(str(col), weight=ft.FontWeight.BOLD))
            for col in preview_df.columns
        ]
        
        # Linhas
        self.data_table.rows = [
            ft.DataRow(
                cells=[ft.DataCell(ft.Text(str(val)[:50])) for val in row]
            )
            for row in preview_df.values
        ]
        
        # Atualiza dropdown de filtro
        self.filter_column.options = [
            ft.dropdown.Option(col) for col in df.columns
        ]
        if len(df.columns) > 0:
            self.filter_column.value = df.columns[0]
    
    def _update_column_analysis(self):
        """Atualiza análise de colunas."""
        analysis = self.service.analyze_columns()
        self.columns_list.controls.clear()
        
        for col, info in analysis.items():
            tipo = info.get('tipo_semantico', info['tipo'])
            nulos = info['nulos']
            unicos = info['unicos']
            
            # Card de coluna
            card = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(self._get_column_icon(tipo), size=20),
                        ft.Text(col, weight=ft.FontWeight.BOLD, size=14)
                    ]),
                    ft.Text(f"Tipo: {tipo}", size=12),
                    ft.Text(f"Únicos: {unicos} | Nulos: {nulos}", size=11, color=ft.Colors.GREY_500),
                    ft.Text(f"Amostra: {', '.join(info['amostra'][:2])}", size=10, italic=True)
                ], spacing=3),
                padding=8,
                border=ft.border.all(1, ft.Colors.GREY_800),
                border_radius=5,
                bgcolor=ft.Colors.GREY_900
            )
            
            self.columns_list.controls.append(card)
        
        self.page.update()
    
    def _get_column_icon(self, tipo: str):
        """Retorna ícone baseado no tipo da coluna."""
        icons = {
            "Numérico": ft.Icons.NUMBERS,
            "Texto": ft.Icons.TEXT_FIELDS,
            "Data/Hora": ft.Icons.CALENDAR_TODAY,
            "Email": ft.Icons.EMAIL,
            "Telefone": ft.Icons.PHONE,
            "CPF/CNPJ": ft.Icons.BADGE
        }
        return icons.get(tipo, ft.Icons.HELP_OUTLINE)
    
    def _apply_filter(self, e):
        """Aplica filtro nos dados."""
        if self.service.current_data is None:
            self._show_error("Carregue um arquivo primeiro")
            return
        
        column = self.filter_column.value
        operation = self.filter_operation.value
        value = self.filter_value.value
        
        if not column or not value:
            self._show_error("Preencha todos os campos do filtro")
            return
        
        try:
            filtered_df = self.service.filter_data(column, value, operation)
            self._update_preview(filtered_df)
            self._show_success(f"✅ Filtro aplicado: {len(filtered_df)} linhas")
        except Exception as ex:
            self._show_error(f"Erro ao filtrar: {str(ex)}")
    
    async def _analyze_with_ai(self, e):
        """Analisa dados com IA."""
        if self.service.current_data is None:
            self._show_error("Carregue um arquivo primeiro")
            return
        
        if not self.ai_question.value:
            self._show_error("Digite uma pergunta")
            return
        
        model = self.get_model_fn()
        if not model:
            self._show_error("Selecione um modelo")
            return
        
        self.ai_result.value = "🤔 Analisando..."
        self.page.update()
        
        full_response = ""
        try:
            async for chunk in self.service.analyze_with_ai(self.ai_question.value, model):
                full_response += chunk
                self.ai_result.value = full_response
                self.page.update()
        except Exception as ex:
            self.ai_result.value = f"❌ Erro: {str(ex)}"
            self.page.update()
    
    def _export_data(self, e):
        """Exporta dados processados."""
        if self.service.current_data is None:
            self._show_error("Nenhum dado para exportar")
            return
        
        # TODO: Implementar dialog de salvamento
        self._show_success("🚧 Função de exportação em desenvolvimento")
    
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