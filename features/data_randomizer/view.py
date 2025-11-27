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

        self.file_picker = ft.FilePicker(on_result=self._file_selected)
        self.page.overlay.append(self.file_picker)

        self.container = ft.Container(
            padding=20,
            expand=True,
            content=ft.Column([
                ft.Row([
                    ft.ElevatedButton(
                        "Selecionar Arquivo",
                        icon=ft.Icons.UPLOAD_FILE,
                        on_click=lambda _: self.file_picker.pick_files(
                            allow_multiple=False,
                            allowed_extensions=["csv", "xlsx", "txt"]
                        )
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

    def _file_selected(self, e: ft.FilePickerResultEvent):
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
