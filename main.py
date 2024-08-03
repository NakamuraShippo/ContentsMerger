import os
import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.resources import resource_add_path
from kivy.config import Config
from tkinter import Tk, filedialog

# 日本語フォントの設定
resource_add_path('C:/Windows/Fonts')
LabelBase.register(DEFAULT_FONT, 'msgothic.ttc')

# Kivy設定
Config.set('kivy', 'log_level', 'error')

class FolderContentMerger(BoxLayout):
    def __init__(self, **kwargs):
        super(FolderContentMerger, self).__init__(**kwargs)
        self.orientation = 'vertical'
        
        self.folder_path = ""
        
        self.folder_button = Button(text="フォルダを選択", size_hint_y=None, height=50)
        self.folder_button.bind(on_press=self.show_folder_chooser)
        
        self.folder_label = Label(text="選択されたフォルダ: なし", size_hint_y=None, height=30)
        
        # サブフォルダーを含めるかどうかのチェックボックス
        subfolder_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        subfolder_label = Label(text="サブフォルダーを含める")
        self.subfolder_checkbox = CheckBox(active=True)
        subfolder_box.add_widget(subfolder_label)
        subfolder_box.add_widget(self.subfolder_checkbox)
        
        self.merge_button = Button(text="処理開始", size_hint_y=None, height=50)
        self.merge_button.bind(on_press=self.merge_files)
        
        self.result_label = Label(text="", size_hint_y=None, height=30)
        
        self.add_widget(self.folder_button)
        self.add_widget(self.folder_label)
        self.add_widget(subfolder_box)
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
        
        output_file = os.path.join(self.folder_path, "merged_content.txt")
        include_subfolders = self.subfolder_checkbox.active
        
        with open(output_file, 'w', encoding='utf-8') as outfile:
            if include_subfolders:
                self.process_folder(self.folder_path, outfile)
            else:
                self.process_files_in_folder(self.folder_path, outfile)
        
        self.result_label.text = f"ファイルが作成されました: {output_file}"
    
    def process_folder(self, folder_path, outfile):
        for root, dirs, files in os.walk(folder_path):
            self.process_files_in_folder(root, outfile)
    
    def process_files_in_folder(self, folder_path, outfile):
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                self.write_file_content(file_path, outfile)

    def write_file_content(self, file_path, outfile):
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

class FolderContentMergerApp(App):
    def build(self):
        return FolderContentMerger()

if __name__ == '__main__':
    FolderContentMergerApp().run()