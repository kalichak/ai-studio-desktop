"""Componentes reutilizáveis da UI."""
import flet as ft

def create_message_bubble(role: str, text: str) -> ft.Row:
    """Cria bolha de mensagem estilizada."""
    is_user = (role == "user")
    
    markdown = ft.Markdown(
        text,
        selectable=True,
        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
        code_theme="atom-one-dark"
    )
    
    bubble = ft.Container(
        content=markdown,
        padding=15,
        border_radius=10,
        bgcolor=ft.Colors.BLUE_GREY_900 if is_user else ft.Colors.BLACK26,
        expand=True
    )
    
    return ft.Row(
        [bubble],
        alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
    )

def create_section_card(title: str, content: ft.Control, icon: str = None) -> ft.Container:
    """Cria card de seção com título."""
    header_content = [ft.Text(title, size=18, weight=ft.FontWeight.BOLD)]
    if icon:
        header_content.insert(0, ft.Icon(icon))
    
    return ft.Container(
        content=ft.Column([
            ft.Row(header_content, spacing=10),
            ft.Divider(),
            content
        ]),
        padding=20,
        border=ft.border.all(1, ft.Colors.GREY_800),
        border_radius=10
    )

def create_result_container(content: ft.Control) -> ft.Container:
    """Container para exibição de resultados."""
    return ft.Container(
        content=ft.Column([content], scroll=ft.ScrollMode.ALWAYS),
        expand=True,
        border=ft.border.all(1, ft.Colors.GREY_800),
        border_radius=5,
        padding=10
    )