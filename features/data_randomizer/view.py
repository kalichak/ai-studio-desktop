import flet as ft
import pandas as pd
from features.data_randomizer.service import DataRandomizerService
import os

class DataRandomizerView:

    def __init__(self, page: ft.Page):
        self.page = page
        self.service = DataRandomizerService()

        self.file_path_text = ft.Text("Nenhum arquivo selecionado", italic=True)
        self.preview_data = ft.Text("", selectable=True)
        self.btn_randomize = ft.ElevatedButton("Randomizar", disabled=True, on_click=self._randomize)

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
                ft.Text("Prévia:", weight="bold"),
                self.preview_data,
                ft.Divider(),
                self.btn_randomize
            ])
        )

        self.loaded_df = None

    def _select_file(self, e):
        """Permite inserir caminho do arquivo manualmente."""
        dlg = ft.AlertDialog(
            title=ft.Text("Selecionar Arquivo"),
            content=ft.Column([
                ft.Text("Digite o caminho do arquivo:", size=14),
                ft.TextField(
                    label="Caminho do arquivo",
                    hint_text="Ex: C:\\Users\\seu_usuario\\arquivo.csv"
                )
            ]),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: setattr(dlg, 'open', False) or self.page.update()),
                ft.TextButton("OK", on_click=lambda _: self._load_from_path(dlg.content.controls[1].value) or setattr(dlg, 'open', False) or self.page.update())
            ]
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def _load_from_path(self, file_path: str):
        """Carrega arquivo do caminho fornecido."""
        if not file_path:
            return

        self.file_path_text.value = file_path
        self.file_path_text.update()

        try:
            df = self.service.load_document(file_path)
            self.loaded_df = df
            self.preview_data.value = df.head().to_string()
            self.preview_data.update()
            self.btn_randomize.disabled = False
            self.btn_randomize.update()
        except Exception as err:
            self.preview_data.value = f"Erro: {err}"
            self.preview_data.update()

    def _file_selected(self, e):
        if not e.files:
            return

        file = e.files[0]
        self.file_path_text.value = file.path
        self.file_path_text.update()

        try:
            df = self.service.load_document(file.path)
            self.loaded_df = df
            self.preview_data.value = df.head().to_string()
            self.preview_data.update()
            self.btn_randomize.disabled = False
            self.btn_randomize.update()

        except Exception as err:
            self.preview_data.value = f"Erro: {err}"
            self.preview_data.update()

    def _randomize(self, e):
        if self.loaded_df is None:
            return

        df2 = self.service.randomize_dataframe(self.loaded_df)

        out_path = "randomized_output.xlsx"
        df2.to_excel(out_path, index=False)

        self.page.snack_bar = ft.SnackBar(
            ft.Text(f"Arquivo gerado: {out_path}"), bgcolor=ft.Colors.GREEN
        )
        self.page.snack_bar.open = True
        self.page.update()
