import os
import asyncio
import flet as ft
from pathlib import Path
from core.controller import Controller
from core.convertor_mercury_class import Mercury
from core.converter_set_class import SetMeter
from core.facade_class import CreateProfileFiles
from flet import (Text, ElevatedButton, OutlinedButton, AlertDialog)
from app_appbar import page_appbar


class Converter(ft.UserControl):

    def __init__(self, page, overlay):
        self.page = page
        self.overlay = overlay

        self.mercury_controller = None
        self.set_controller = None
        self.mercury_meter = None
        self.set_meter = None

        self.excel_path = os.path.join(os.getcwd(), 'Excel')

        self.directory_path = ft.Text("", color=ft.colors.GREEN)
        self.get_directory_dialog = ft.FilePicker(on_result=self.get_directory_result)
        self.pick_files_dialog = ft.FilePicker(on_result=self.pick_files_result)

        self.confirm_dialog = AlertDialog(
            modal=True,
            content=Text("Вы действительно хотите выйти?", size=14),
            actions=[
                ElevatedButton("Да", on_click=self.yes_click),
                OutlinedButton("Нет", on_click=self.no_click),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        self.text_field = ft.ListView(width=500, height=330, auto_scroll=True)

        self.text_field.controls.append(ft.Text(f"Добро пожаловать!"))

        self.text_field_container = ft.Container(
            alignment=ft.alignment.top_center,
            padding=10,
            bgcolor=ft.colors.SECONDARY_CONTAINER,
            border_radius=5,
            content=ft.Column(
                controls=[self.text_field],
                expand=True,
            ),
        )
        self.open_folder_button = ft.ElevatedButton("Открыть папку", icon=ft.icons.FOLDER_OPEN,
                                                    on_click=lambda _: self.get_directory_dialog.get_directory_path(),
                                                    )
        self.open_file_button = ft.ElevatedButton("Открыть файл", icon=ft.icons.FILE_OPEN,
                                                  on_click=lambda _: self.pick_files_dialog.pick_files(
                                                      allow_multiple=True
                                                  ),
                                                  )
        self.start_button = ft.ElevatedButton("СТАРТ", icon=ft.icons.START, icon_color=ft.colors.GREEN,
                                              disabled=True, on_click=self.start_app)
        self.stop_button = ft.ElevatedButton("СТОП", icon=ft.icons.STOP, icon_color=ft.colors.RED,
                                             disabled=True)

        self.opening = ft.Container(
            alignment=ft.alignment.center,
            padding=10,
            border_radius=5,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[self.open_folder_button, self.open_file_button],
            ),
        )

        self.starting = ft.Container(
            alignment=ft.alignment.center,
            padding=10,
            border_radius=5,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[self.start_button, self.stop_button],
            ),
        )

        self.closing = ft.Container(
            alignment=ft.alignment.center,
            padding=10,
            border_radius=5,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[ft.ElevatedButton("Выход", icon=ft.icons.EXIT_TO_APP, on_click=self.close_click)],
            ),
        )

        super().__init__()

    def yes_click(self, _):
        self.page.window_destroy()

    def no_click(self, _):
        self.confirm_dialog.open = False
        self.page.update()

    def close_click(self, _):
        self.page.dialog = self.confirm_dialog
        self.confirm_dialog.open = True
        self.page.update()

    @staticmethod
    def find_excel_files(path):
        folder_count = len([1 for _ in Path(path).iterdir()])
        return folder_count

    def start_app(self, _):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        profile_files = CreateProfileFiles(self.directory_path.value)

        self.mercury_meter = Mercury(profile_files)
        self.set_meter = SetMeter(profile_files)

        self.mercury_controller = Controller(meter_obj=self.mercury_meter)
        self.set_controller = Controller(meter_obj=self.set_meter)

        self.text_field.controls.append(
            ft.Text(f"Всего файлов - {len(profile_files.all_files)}", color=ft.colors.BLUE_700))
        self.text_field.controls.append(
            ft.Text(f"Текстовых файлов - {len(profile_files.txt_files)}", color=ft.colors.BLUE_700))
        self.text_field.controls.append(
            ft.Text(f"HTML файлов - {len(profile_files.html_files)}\n", color=ft.colors.BLUE_700))
        self.page.update()

        set_data = loop.create_task(self.set_controller.meter_obj.make_report())
        mercury_data = loop.create_task(self.mercury_controller.meter_obj.make_report())

        loop.run_until_complete(asyncio.wait([set_data, mercury_data]))

        if len(self.set_controller.meter_obj.all_files) == 0:
            self.text_field.controls.append(
                ft.Text(f"[!] Папка пуста!", color=ft.colors.RED_300))
            self.page.update()
            return

        self.text_field.controls.append(
            ft.Text(f"[!] Запущен процесс конвертации...", color=ft.colors.RED_300))

        self.start_button.disabled = True
        self.stop_button.disabled = False
        self.open_folder_button.disabled = True
        self.page.update()

        count_try_files = len(self.set_controller.meter_obj.txt_files) + len(self.set_controller.meter_obj.html_files)

        self.text_field.controls.append(
            ft.Text(f"[+] Процесс конвертации завершен!", color=ft.colors.GREEN))

        self.text_field.controls.append(
            ft.Text(
                f"Обработано файлов - {count_try_files} (из {len(profile_files.all_files)})",
                color=ft.colors.BLUE_700))

        self.text_field.controls.append(
            ft.Text(f"Невалидных текстовых файлов - {len(self.set_controller.meter_obj.bad_txt_files)}",
                    color=ft.colors.BLUE_700))

        self.text_field.controls.append(
            ft.Text(f"Невалидных HTML файлов - {len(self.mercury_controller.meter_obj.bad_html_files)}\n",
                    color=ft.colors.BLUE_700))

        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.open_folder_button.disabled = False
        self.open_file_button.disabled = False
        self.update()

    def pick_files_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.directory_path.value = None
            self.directory_path.value = [f.path for f in e.files]
            self.text_field.controls.append(ft.Text(f"Выбраны файлы:", color=ft.colors.GREEN))

            for i, file in enumerate(e.files):
                self.text_field.controls.append(ft.Text(f"{i}.{file.name}", color=ft.colors.GREEN))

            self.start_button.disabled = False
            self.open_file_button.disabled = True
            self.update()

    def get_directory_result(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.directory_path.value = None
            self.directory_path.value = e.path
            self.text_field.controls.append(ft.Text(f"Выбран каталог - {e.path}", color=ft.colors.GREEN))
            self.start_button.disabled = False
            self.open_file_button.disabled = True
            self.update()

    def build(self):
        self.overlay.extend([self.get_directory_dialog, self.pick_files_dialog])
        return ft.Row(
            controls=[
                ft.Column(controls=[self.opening, ft.Divider(), self.starting, ft.Divider(), self.closing],
                          expand=1,
                          ),

                ft.Column(controls=[self.text_field_container],
                          expand=2,
                          ),
            ]
        )

        # return Stack(controls=[rows])


def main(page: ft.Page):
    page.title = "1C Profile Converter (2023)"

    page.window_height = 500
    page.window_width = 800
    page.window_max_height = 500
    page.window_max_width = 800
    page.window_maximized = False
    # page.update()
    # page.window_resizable = False

    page.fonts = {
        "Roboto Mono": "RobotoMono-VariableFont_wght.ttf",
    }

    page.update()
    page.appbar = page_appbar()
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.theme.Theme(color_scheme_seed="blue")

    page.add(Converter(page, page.overlay))
    page.update()


ft.app(target=main)
