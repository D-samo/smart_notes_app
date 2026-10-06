import flet as ft
from ai_service import SmartAIService
import json
import os

GEMINI_API_KEYS = [
    "AQ.Ab8RN6IGf1W4YlxlyRjLANQDo00_DGS8Zi9h401C9DQ2poqzUQ",
    "AQ.Ab8RN6Kht1ZwYdMV7ejU8gmTQQLOOtmhE5ybbsFW6ub69qszOg",
    "AQ.Ab8RN6KRLslW7GmObWNlYSKqBkFc4LQjbMq08mO_s6LgYxJIzQ",
    "AQ.Ab8RN6IFY-L3GN67rbwJrwvwz6wSbCIyjS096tzzylFeUYcehA",
    "AQ.Ab8RN6IkyfatTSDLuA5wIHbF6rUs6y_YoOdIxldIGbUDRB3hhg"
]

DATA_FILE = "ders_asistani_data.json"

# --- %100 DİL SÖZLÜĞÜ ---
LANG = {
    "tr": {
        "app_title": "📚 Ders Asistanı",
        "tab_lessons": "Dersler",
        "tab_settings": "Ayarlar",
        "theme": "Karanlık Mod",
        "theme_sub": "Arayüz renk temasını değiştirir",
        "language": "Uygulama Dili",
        "language_sub": "Türkçe / English",
        "reset_data": "Tüm Verileri Sıfırla",
        "reset_sub": "Kayıtlı notları ve tokenları siler",
        "folders_title": "Klasörlerim",
        "empty_folder": "Bu klasörde henüz fotoğraf yok.",
        "items": "Öğe",
        "upload_btn": "📸 Fotoğraf Çek / Not Ekle",
        "add_photo_title": "Not Fotoğrafı Ekle",
        "camera": "Kameradan Çek",
        "gallery": "Galeriden Seç",
        "chat_title": "💬 AI Sohbeti",
        "chat_placeholder": "Soru veya isteğinizi yazın...",
        "quiz_btn": "📝 Quiz Üret (150 Token)",
        "close": "Kapat",
        "tokens": "Token",
        "reward_msg": "🎁 Ödüllü reklam izlendi: +100 Token eklendi! ✨",
        "ai_loading": "AI Fotoğrafı analiz ediyor... 🤖",
        "deleted_msg": "🗑️ Fotoğraf klasörden silindi.",
        "reset_msg": "🗑️ Tüm veriler başarıyla sıfırlandı.",
        "insufficient_token": "❌ Yetersiz Token!",
        "chat_intro": "🤖 Not yüklendi! Soru sorabilir veya alt menüden Quiz üretebilirsin.",
        "quiz_prompt": "Bu nottan bir quiz (sınav) üret.",
        "folders": [
            "Matematik", "Fen Bilimleri", "Sosyal Bilgiler", "Türkçe / Türk Dili ve Edebiyatı",
            "Fizik", "Kimya", "Biyoloji", "Tarih", "Coğrafya", "Yabancı Dil",
            "Din Kültürü ve Ahlak Bilgisi", "Gruplandırılacak"
        ]
    },
    "en": {
        "app_title": "📚 Study Assistant",
        "tab_lessons": "Lessons",
        "tab_settings": "Settings",
        "theme": "Dark Mode",
        "theme_sub": "Changes interface color theme",
        "language": "App Language",
        "language_sub": "English / Türkçe",
        "reset_data": "Reset All Data",
        "reset_sub": "Deletes saved notes and tokens",
        "folders_title": "My Folders",
        "empty_folder": "No photos in this folder yet.",
        "items": "Items",
        "upload_btn": "📸 Take Photo / Add Note",
        "add_photo_title": "Add Note Photo",
        "camera": "Take with Camera",
        "gallery": "Choose from Gallery",
        "chat_title": "💬 AI Chat",
        "chat_placeholder": "Type your question or request...",
        "quiz_btn": "📝 Generate Quiz (150 Tokens)",
        "close": "Close",
        "tokens": "Tokens",
        "reward_msg": "🎁 Rewarded ad watched: +100 Tokens added! ✨",
        "ai_loading": "AI is analyzing the photo... 🤖",
        "deleted_msg": "🗑️ Photo deleted from folder.",
        "reset_msg": "🗑️ All data successfully reset.",
        "insufficient_token": "❌ Insufficient Tokens!",
        "chat_intro": "🤖 Note loaded! Ask a question or generate a Quiz from below.",
        "quiz_prompt": "Generate a quiz from this note.",
        "folders": [
            "Mathematics", "Science", "Social Studies", "English & Literature",
            "Physics", "Chemistry", "Biology", "History", "Geography", "Foreign Language",
            "Ethics & Philosophy", "Uncategorized"
        ]
    }
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"tokens": 500, "theme": "dark", "lang": "tr", "folders": {}}

def save_data(tokens, theme, lang, folders):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"tokens": tokens, "theme": theme, "lang": lang, "folders": folders}, f, ensure_ascii=False, indent=4)

def main(page: ft.Page):
    app_data = load_data()
    
    current_lang = app_data.get("lang", "tr")
    t = LANG[current_lang]
    
    page.title = "Ders Asistanı AI"
    page.theme_mode = ft.ThemeMode.DARK if app_data.get("theme", "dark") == "dark" else ft.ThemeMode.LIGHT
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    tokens_count = app_data.get("tokens", 500)
    user_tokens_text = ft.Text(f"{tokens_count} {t['tokens']}", weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400)
    
    folder_contents = app_data.get("folders", {})
    for df in t["folders"]:
        if df not in folder_contents:
            folder_contents[df] = []

    ai_service = SmartAIService(api_keys=GEMINI_API_KEYS)
    
    main_container = ft.Column(expand=True)
    settings_container = ft.Column(expand=True, visible=False)

    def trigger_save():
        save_data(tokens_count, "dark" if page.theme_mode == ft.ThemeMode.DARK else "light", current_lang, folder_contents)

    def refresh_header():
        user_tokens_text.value = f"{tokens_count} {t['tokens']}"
        trigger_save()
        page.update()

    def add_reward_tokens(e):
        nonlocal tokens_count
        tokens_count += 100
        refresh_header()
        page.open(ft.SnackBar(ft.Text(t["reward_msg"])))

    def open_image_viewer(image_path):
        viewer_dialog = ft.AlertDialog(
            content=ft.Image(src=image_path, fit=ft.ImageFit.CONTAIN),
            content_padding=0,
            actions=[ft.TextButton(t["close"], on_click=lambda _: page.close(viewer_dialog))]
        )
        page.open(viewer_dialog)

    def open_chat_modal(image_path, folder_name):
        nonlocal tokens_count
        
        chat_session = ai_service.start_chat_session(image_path)
        messages_list = ft.ListView(expand=True, spacing=10, padding=10, height=250)
        
        def reset_chat_ui():
            nonlocal chat_session
            chat_session = ai_service.start_chat_session(image_path)
            messages_list.controls.clear()
            messages_list.controls.append(
                ft.Container(
                    content=ft.Text(t["chat_intro"], size=12, color=ft.Colors.AMBER_200),
                    bgcolor=ft.Colors.GREY_900 if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.BLUE_GREY_800, 
                    padding=10, border_radius=8
                )
            )
            page.update()

        reset_chat_ui()

        prompt_input = ft.TextField(
            hint_text=t["chat_placeholder"],
            expand=True, border_radius=10, content_padding=10,
            on_submit=lambda e: send_chat_message()
        )

        loading_ring = ft.ProgressRing(visible=False, width=20, height=20, stroke_width=2)

        def send_chat_message(custom_text=None, cost=50):
            nonlocal tokens_count
            user_text = custom_text if custom_text else prompt_input.value.strip()
            if not user_text: return

            if tokens_count < cost:
                page.open(ft.SnackBar(ft.Text(f"{t['insufficient_token']} (Cost: {cost})")))
                return

            tokens_count -= cost
            refresh_header()

            messages_list.controls.append(
                ft.Row([
                    ft.Container(
                        content=ft.Text(user_text, color=ft.Colors.WHITE, size=13),
                        bgcolor=ft.Colors.BLUE_700, padding=10, border_radius=10
                    )
                ], alignment=ft.MainAxisAlignment.END)
            )

            prompt_input.value = ""
            loading_ring.visible = True
            send_btn.disabled = True
            quiz_btn.disabled = True
            page.update()

            if custom_text == t["quiz_prompt"]:
                ai_response = ai_service.generate_quiz(image_path)
            else:
                ai_response = chat_session.send_message(user_text)

            messages_list.controls.append(
                ft.Row([
                    ft.Container(
                        content=ft.Markdown(ai_response, selectable=True, extension_set=ft.MarkdownExtensionSet.GITHUB_WEB),
                        bgcolor=ft.Colors.GREY_800 if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.BLUE_GREY_600, 
                        padding=12, border_radius=10, width=320
                    )
                ], alignment=ft.MainAxisAlignment.START)
            )

            loading_ring.visible = False
            send_btn.disabled = False
            quiz_btn.disabled = False
            page.update()

        def delete_current_image(e):
            folder_contents[folder_name].remove(image_path)
            trigger_save()
            page.close(modal_dialog)
            open_folder_detail(folder_name)
            page.open(ft.SnackBar(ft.Text(t["deleted_msg"])))

        send_btn = ft.IconButton(icon=ft.Icons.SEND_ROUNDED, icon_color=ft.Colors.BLUE_400, on_click=lambda _: send_chat_message())
        
        quiz_btn = ft.ElevatedButton(
            t["quiz_btn"], 
            color=ft.Colors.AMBER_400, bgcolor=ft.Colors.GREY_900,
            on_click=lambda _: send_chat_message(t["quiz_prompt"], 150)
        )

        modal_dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Text(t["chat_title"], size=16, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.IconButton(ft.Icons.REFRESH, tooltip="Reset", icon_size=20, on_click=lambda _: reset_chat_ui()),
                    ft.IconButton(ft.Icons.DELETE_OUTLINED, tooltip="Delete", icon_color=ft.Colors.RED_400, icon_size=20, on_click=delete_current_image)
                ])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            content=ft.Column([
                ft.GestureDetector(
                    content=ft.Container(
                        content=ft.Image(src=image_path, height=120, fit=ft.ImageFit.CONTAIN),
                        alignment=ft.alignment.center
                    ),
                    on_tap=lambda _: open_image_viewer(image_path)
                ),
                ft.Divider(height=1),
                messages_list,
                quiz_btn,
                loading_ring,
                ft.Row([prompt_input, send_btn])
            ], tight=True, height=540, width=400),
            actions=[ft.TextButton(t["close"], on_click=lambda _: page.close(modal_dialog))]
        )
        page.open(modal_dialog)

    def open_folder_detail(folder_name):
        main_container.controls.clear()
        images_grid = ft.GridView(runs_count=3, max_extent=120, spacing=10, run_spacing=10)
        
        for img_path in folder_contents.get(folder_name, []):
            images_grid.controls.append(
                ft.GestureDetector(
                    content=ft.Container(
                        content=ft.Image(src=img_path, fit=ft.ImageFit.COVER, border_radius=8),
                        border=ft.border.all(1, ft.Colors.GREY_700), border_radius=8
                    ),
                    on_tap=lambda _, path=img_path: open_chat_modal(path, folder_name)
                )
            )

        main_container.controls.extend([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: show_main_folders()),
                ft.Text(f"📂 {folder_name}", size=20, weight=ft.FontWeight.BOLD)
            ]),
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            images_grid if len(folder_contents.get(folder_name, [])) > 0 else ft.Text(t["empty_folder"], color=ft.Colors.GREY_500)
        ])
        page.update()

    def show_main_folders():
        main_container.controls.clear()
        folders_grid = ft.GridView(runs_count=2, max_extent=180, child_aspect_ratio=1.0, spacing=10, run_spacing=10)

        for folder_name in t["folders"]:
            item_count = len(folder_contents.get(folder_name, []))
            folders_grid.controls.append(
                ft.GestureDetector(
                    content=ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Icon(ft.Icons.FOLDER, size=36, color=ft.Colors.BLUE_400),
                                ft.Text(folder_name, weight=ft.FontWeight.BOLD, size=11, text_align=ft.TextAlign.CENTER),
                                ft.Text(f"{item_count} {t['items']}", color=ft.Colors.AMBER_300 if item_count > 0 else ft.Colors.GREY_400, size=11)
                            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=10,
                        )
                    ),
                    on_tap=lambda _, name=folder_name: open_folder_detail(name)
                )
            )

        main_container.controls.extend([ft.Text(t["folders_title"], size=18, weight=ft.FontWeight.W_600), folders_grid])
        page.update()

    def on_file_selected(e: ft.FilePickerResultEvent):
        if e.files:
            file_path = e.files[0].path
            page.open(ft.SnackBar(ft.Text(t["ai_loading"])))

            detected_category = ai_service.classify_image(file_path)
            
            if detected_category not in folder_contents:
                folder_contents[detected_category] = []

            folder_contents[detected_category].append(file_path)
            trigger_save()
            show_main_folders()

    file_picker = ft.FilePicker(on_result=on_file_selected)
    page.overlay.append(file_picker)

    def open_camera_menu(e):
        def pick_action(e):
            page.close(camera_bottom_sheet)
            file_picker.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE)
            
        camera_bottom_sheet = ft.BottomSheet(
            ft.Container(
                ft.Column(
                    [
                        ft.Text(t["add_photo_title"], size=16, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        ft.ListTile(leading=ft.Icon(ft.Icons.CAMERA_ALT, color=ft.Colors.BLUE_400), title=ft.Text(t["camera"]), on_click=pick_action),
                        ft.ListTile(leading=ft.Icon(ft.Icons.PHOTO_LIBRARY, color=ft.Colors.AMBER_400), title=ft.Text(t["gallery"]), on_click=pick_action),
                    ],
                    tight=True,
                ),
                padding=20,
            ),
            open=True
        )
        page.open(camera_bottom_sheet)

    app_title_text = ft.Text(t["app_title"], size=22, weight=ft.FontWeight.BOLD)
    
    header = ft.Row(
        controls=[
            app_title_text,
            ft.Row([
                ft.IconButton(ft.Icons.CARD_GIFTCARD, tooltip="+100 Tokens", icon_color=ft.Colors.AMBER_400, on_click=add_reward_tokens),
                ft.Container(
                    content=ft.Row([ft.Icon(ft.Icons.KEYBOARD_COMMAND_KEY, color=ft.Colors.AMBER_400, size=16), user_tokens_text]),
                    bgcolor=ft.Colors.GREY_900 if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.BLUE_GREY_100, 
                    padding=8, border_radius=12
                )
            ])
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    upload_button = ft.ElevatedButton(
        text=t["upload_btn"], icon=ft.Icons.ADD_CIRCLE,
        bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE, height=48,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=open_camera_menu
    )

    home_view = ft.Column([header, ft.Divider(height=10, color=ft.Colors.TRANSPARENT), upload_button, ft.Divider(height=10, color=ft.Colors.TRANSPARENT), main_container], expand=True)

    def update_ui_language():
        nonlocal t
        t = LANG[current_lang]
        app_title_text.value = t["app_title"]
        upload_button.text = t["upload_btn"]
        nav_bar.destinations[0].label = t["tab_lessons"]
        nav_bar.destinations[1].label = t["tab_settings"]
        
        # Ayarlar listesini güncelle
        settings_container.controls[0].value = t["tab_settings"]
        settings_container.controls[2].title.value = t["theme"]
        settings_container.controls[2].subtitle.value = t["theme_sub"]
        settings_container.controls[3].title.value = t["language"]
        settings_container.controls[3].subtitle.value = t["language_sub"]
        settings_container.controls[4].title.value = t["reset_data"]
        settings_container.controls[4].subtitle.value = t["reset_sub"]
        
        refresh_header()
        show_main_folders()

    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        trigger_save()
        header.controls[1].controls[1].bgcolor = ft.Colors.GREY_900 if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.BLUE_GREY_100
        page.update()
        
    def toggle_lang(e):
        nonlocal current_lang
        current_lang = "en" if e.control.value else "tr"
        trigger_save()
        update_ui_language()

    def reset_app_data(e):
        nonlocal tokens_count, folder_contents
        tokens_count = 500
        folder_contents = {df: [] for df in t["folders"]}
        trigger_save()
        refresh_header()
        page.open(ft.SnackBar(ft.Text(t["reset_msg"])))

    settings_container.controls.extend([
        ft.Text(t["tab_settings"], size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        ft.ListTile(
            leading=ft.Icon(ft.Icons.DARK_MODE),
            title=ft.Text(t["theme"]),
            subtitle=ft.Text(t["theme_sub"]),
            trailing=ft.Switch(value=page.theme_mode == ft.ThemeMode.DARK, on_change=toggle_theme)
        ),
        ft.ListTile(
            leading=ft.Icon(ft.Icons.LANGUAGE),
            title=ft.Text(t["language"]),
            subtitle=ft.Text(t["language_sub"]),
            trailing=ft.Switch(value=current_lang == "en", on_change=toggle_lang)
        ),
        ft.ListTile(
            leading=ft.Icon(ft.Icons.DELETE_FOREVER, color=ft.Colors.RED_400),
            title=ft.Text(t["reset_data"], color=ft.Colors.RED_400),
            subtitle=ft.Text(t["reset_sub"]),
            on_click=reset_app_data
        ),
        ft.Divider(),
        ft.Container(
            content=ft.Column([
                ft.Text("Ders Asistanı AI v1.0", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400),
                ft.Text("Akıllı Görsel Analiz ve Ders Rehberi", size=12, color=ft.Colors.GREY_500)
            ]),
            padding=10
        )
    ])

    def switch_tab(e):
        index = e.control.selected_index
        if index == 0:
            home_view.visible = True
            settings_container.visible = False
            show_main_folders()
        elif index == 1:
            home_view.visible = False
            settings_container.visible = True
        page.update()

    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationDestination(icon=ft.Icons.LIBRARY_BOOKS, label=t["tab_lessons"]),
            ft.NavigationDestination(icon=ft.Icons.SETTINGS, label=t["tab_settings"]),
        ],
        on_change=switch_tab
    )
    
    page.navigation_bar = nav_bar

    page.add(ft.Stack([home_view, settings_container], expand=True))
    show_main_folders()

ft.app(target=main)