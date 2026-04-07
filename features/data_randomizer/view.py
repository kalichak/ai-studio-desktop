import flet as ft
import pandas as pd
from features.data_randomizer.service import DataRandomizerService
from utils.file_picker import select_file
import os

class DataRandomizerView:

    def __init__(self, page: ft.Page):
        self.page = page
        self.service = DataRandomizerService()

        self.file_path_text = ft.Text("Nenhum arquivo selecionado", italic=True)
        self.preview_data = ft.Text("", selectable=True)
        self.btn_anonymize = ft.ElevatedButton("🔒 Anonimizar", disabled=True, on_click=self._anonymize)
        self.btn_randomize = ft.ElevatedButton("🔀 Randomizar", disabled=True, on_click=self._randomize)

        self.loaded_df = None

        self.container = ft.Container(
            padding=20,
            expand=True,
            content=ft.Column([
                ft.Row([
                    ft.ElevatedButton(
                        "Selecionar Arquivo",
                        icon=ft.Icons.UPLOAD_FILE,
                        on_click=self._select_file
                    ),
                    self.file_path_text
                ]),
                ft.Divider(),
                ft.Text("Prévia dos dados:", weight="bold"),
                self.preview_data,
                ft.Divider(),
                ft.Row([
                    self.btn_anonymize,
                    self.btn_randomize
                ])
            ])
        )

        self.loaded_df = None

    def _select_file(self, e):
        """Abre seletor nativo de arquivo do Windows."""
        try:
            file_path = select_file(
                "Selecionar Arquivo",
                filetypes=[
                    ("Arquivos de Dados", "*.csv *.xlsx *.xls *.txt"),
                    ("CSV files", "*.csv"),
                    ("Excel files", "*.xlsx *.xls"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ]
            )
            if file_path:
                self._load_from_path(file_path)
                print(f"✅ Arquivo selecionado: {file_path}")
            else:
                print("ℹ️ Nenhum arquivo selecionado")
        except Exception as ex:
            print(f"❌ Erro: {ex}")
            import traceback
            traceback.print_exc()

    def _load_from_path(self, file_path: str):
        """Carrega arquivo do caminho fornecido."""
        if not file_path or not file_path.strip():
            self.preview_data.value = "❌ Caminho vazio"
            self.preview_data.update()
            return

        self.file_path_text.value = file_path
        self.file_path_text.update()

        try:
            print(f"📂 Carregando: {file_path}")
            df = self.service.load_document(file_path)
            self.loaded_df = df
            preview = f"✅ Arquivo carregado ({len(df)} linhas, {len(df.columns)} colunas)\n\n{df.head().to_string()}"
            self.preview_data.value = preview
            self.preview_data.update()
            self.btn_randomize.disabled = False
            self.btn_anonymize.disabled = False
            self.btn_randomize.update()
            self.btn_anonymize.update()
            print(f"✅ Arquivo pronto para processar")
        except Exception as err:
            print(f"❌ Erro ao carregar: {err}")
            import traceback
            traceback.print_exc()
            self.preview_data.value = f"❌ Erro: {str(err)}"
            self.preview_data.update()


    def _anonymize(self, e):
        """Anonimiza preservando estrutura dos dados (DATA FAKE SUITE)."""
        if self.loaded_df is None:
            return

        try:
            df_anon = self.service.anonymize_dataframe(self.loaded_df)
            out_path = "anonymized_output.xlsx"
            df_anon.to_excel(out_path, index=False)

            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"✅ Arquivo anonimizado: {out_path}"), bgcolor=ft.Colors.GREEN
            )
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as err:
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"❌ Erro: {err}"), bgcolor=ft.Colors.RED
            )
            self.page.snack_bar.open = True
            self.page.update()

    def _randomize(self, e):
        """Randomiza gerando novos valores (modo legacy)."""
        if self.loaded_df is None:
            return

        try:
            df2 = self.service.randomize_dataframe(self.loaded_df)
            out_path = "randomized_output.xlsx"
            df2.to_excel(out_path, index=False)

            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"✅ Arquivo randomizado: {out_path}"), bgcolor=ft.Colors.GREEN
            )
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as err:
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"❌ Erro: {err}"), bgcolor=ft.Colors.RED
            )
            self.page.snack_bar.open = True
            self.page.update()
