import os
import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.resources import resource_add_path
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from tkinter import Tk, filedialog
import html

# 日本語フォントの設定
resource_add_path('C:/Windows/Fonts')
LabelBase.register(DEFAULT_FONT, 'msgothic.ttc')

# Kivy設定
#Config.set('kivy', 'log_level', 'error')
# Kivy設定：ウィンドウサイズを固定し、サイズ変更を無効化
Config.set('graphics', 'width', '10')
Config.set('graphics', 'height', '30')
Config.set('graphics', 'resizable', '0')
Config.set('kivy', 'window_icon', '')  # アイコンを無効化（オプション）
Window.size = (500,300)

class ContentMerger(BoxLayout):
    def __init__(self, **kwargs):
        super(ContentMerger, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = [10, 10, 10, 10]  # 左、上、右、下のパディング
        self.spacing = 10

        self.folder_path = ""

        self.folder_button = Button(text="フォルダを選択", size_hint_y=None, height=40)
        self.folder_button.bind(on_press=self.show_folder_chooser)

        self.folder_label = Label(text="選択されたフォルダ: なし", size_hint_y=None, height=30)

        subfolder_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        subfolder_label = Label(text="サブフォルダーを含める")
        subfolder_box.add_widget(subfolder_label)
        self.subfolder_checkbox = CheckBox(active=True, size_hint_x=None, width=100)
        subfolder_box.add_widget(self.subfolder_checkbox)

        output_format_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        output_format_label = Label(text="出力形式:")
        self.output_format_spinner = Spinner(text='TXT', values=('TXT', 'HTML'), size_hint_x=None, width=100)
        output_format_box.add_widget(output_format_label)
        output_format_box.add_widget(self.output_format_spinner)

        self.merge_button = Button(text="処理開始", size_hint_y=None, height=40)
        self.merge_button.bind(on_press=self.merge_files)

        self.result_label = Label(text="", size_hint_y=None, height=30)

        self.add_widget(self.folder_button)
        self.add_widget(self.folder_label)
        self.add_widget(subfolder_box)
        self.add_widget(output_format_box)
        self.add_widget(self.merge_button)
        self.add_widget(self.result_label)

    def show_folder_chooser(self, instance):
        root = Tk()
        root.withdraw()
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_path = folder_path
            self.folder_label.text = f"選択されたフォルダ: {self.folder_path}"
        root.destroy()
        
    def get_file_type(self, file_extension):
        extension_map = {
            '.py': 'python',
            '.json': 'json',
            '.html': 'html',
            '.css': 'css',
            '.js': 'javascript',
            '.md': 'markdown',
            '.txt': 'text',
            '.docx': 'document',
            '.pdf': 'pdf'
        }
        return extension_map.get(file_extension.lower(), 'unknown')
        
    def merge_files(self, instance):
        if not self.folder_path:
            self.result_label.text = "フォルダが選択されていません"
            return
        
        output_format = self.output_format_spinner.text
        output_filename = f"merged_content.{output_format.lower()}"
        output_file = os.path.join(self.folder_path, output_filename)
        include_subfolders = self.subfolder_checkbox.active
        
        if output_format == 'HTML':
            self.merge_files_html(output_file, include_subfolders, output_filename)
        else:
            self.merge_files_txt(output_file, include_subfolders, output_filename)
        
        self.result_label.text = f"ファイルが作成されました: {output_file}"

    def merge_files_txt(self, output_file, include_subfolders, output_filename):
        with open(output_file, 'w', encoding='utf-8') as outfile:
            if include_subfolders:
                self.process_folder_txt(self.folder_path, outfile, output_filename)
            else:
                self.process_files_in_folder_txt(self.folder_path, outfile, output_filename)

    def process_folder_txt(self, folder_path, outfile, output_filename):
        for root, dirs, files in os.walk(folder_path):
            self.process_files_in_folder_txt(root, outfile, output_filename)

    def process_files_in_folder_txt(self, folder_path, outfile, output_filename):
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path) and file != output_filename:
                self.write_file_content_txt(file_path, outfile)

    def write_file_content_txt(self, file_path, outfile):
        file = os.path.basename(file_path)
        file_extension = os.path.splitext(file)[1]
        file_type = self.get_file_type(file_extension)
        
        creation_time = os.path.getctime(file_path)
        modification_time = os.path.getmtime(file_path)
        
        outfile.write(f"===== FILE_START: {file} =====\n")
        outfile.write(f"FILE_TYPE: {file_type}\n")
        outfile.write(f"CREATION_DATE: {datetime.datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d')}\n")
        outfile.write(f"LAST_MODIFIED: {datetime.datetime.fromtimestamp(modification_time).strftime('%Y-%m-%d')}\n\n")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as infile:
                outfile.write(infile.read())
        except UnicodeDecodeError:
            outfile.write(f"[Unable to read file: {file}. It may be a binary file.]\n")
        
        outfile.write(f"\n===== FILE_END: {file} =====\n\n")

    def merge_files_html(self, output_file, include_subfolders, output_filename):
        with open(output_file, 'w', encoding='utf-8') as outfile:
            outfile.write('''
            <!DOCTYPE html>
            <html lang="ja">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Merged Content</title>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }
                    h2 { color: #333; border-bottom: 1px solid #ccc; padding-bottom: 10px; }
                    pre { background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }
                    .file-info { margin-bottom: 10px; font-size: 0.9em; color: #666; }
                </style>
            </head>
            <body>
                <h1>Merged Content</h1>
            ''')
            
            if include_subfolders:
                self.process_folder_html(self.folder_path, outfile, output_filename)
            else:
                self.process_files_in_folder_html(self.folder_path, outfile, output_filename)
            
            outfile.write('</body></html>')

    def process_folder_html(self, folder_path, outfile, output_filename):
        for root, dirs, files in os.walk(folder_path):
            self.process_files_in_folder_html(root, outfile, output_filename)

    def process_files_in_folder_html(self, folder_path, outfile, output_filename):
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path) and file != output_filename:
                self.write_file_content_html(file_path, outfile)

    def write_file_content_html(self, file_path, outfile):
        file = os.path.basename(file_path)
        file_extension = os.path.splitext(file)[1]
        file_type = self.get_file_type(file_extension)
        
        creation_time = os.path.getctime(file_path)
        modification_time = os.path.getmtime(file_path)
        
        outfile.write(f'<h2>{html.escape(file)}</h2>')
        outfile.write('<div class="file-info">')
        outfile.write(f'<p>File Type: {file_type}</p>')
        outfile.write(f'<p>Creation Date: {datetime.datetime.fromtimestamp(creation_time).strftime("%Y-%m-%d")}</p>')
        outfile.write(f'<p>Last Modified: {datetime.datetime.fromtimestamp(modification_time).strftime("%Y-%m-%d")}</p>')
        outfile.write('</div>')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as infile:
                content = infile.read()
                outfile.write(f'<pre>{html.escape(content)}</pre>')
        except UnicodeDecodeError:
            outfile.write(f'<p>[Unable to read file: {html.escape(file)}. It may be a binary file.]</p>')

class ContentMergerApp(App):
    def build(self):
        return ContentMerger()

if __name__ == '__main__':
    ContentMergerApp().run()