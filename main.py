import sqlite3
import sys
import keyboard
import pyautogui
import time
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel,
    QLineEdit, QPushButton, QListWidget, QMenuBar, QMenu, QMessageBox, QDialog, QToolBar, QComboBox, QListWidgetItem, QHBoxLayout, QSpacerItem, QSizePolicy, QSystemTrayIcon
)

from PySide6.QtCore import Qt, QSettings, QTimer
from PySide6.QtGui import QAction, QIcon


class Planner(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Repeat Amount")
        self.setFixedSize(300, 150)

        self.repeat_amount = 1

        layout = QVBoxLayout()

        self.label = QLabel("Enter Repeat Amount:")
        layout.addWidget(self.label)

        self.label2 = QLabel(f"Repeat Amount: {self.repeat_amount}")
        layout.addWidget(self.label2)

        self.input_field_text = QLineEdit()
        layout.addWidget(self.input_field_text) 

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_repeat_amount)
        layout.addWidget(self.save_button)

        self.setLayout(layout)
    
    def save_repeat_amount(self):
        amount = self.input_field_text.text()
        if amount == "" or amount == " ":
            self.repeat_amount = 1
        else:
            self.repeat_amount = int(amount)
        self.label2.setText(f"Repeat Amount: {self.repeat_amount}")
        
        self.accept()

    def get_repeat_amount(self):
        return self.repeat_amount

class Settings(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(300, 300)

        layout = QVBoxLayout()

        self.hotkey_add_label = QLabel("Create new Hotkey:")
        layout.addWidget(self.hotkey_add_label)

        self.input_hotkey = QLineEdit()
        self.input_hotkey.setPlaceholderText("Key")
        layout.addWidget(self.input_hotkey)

        self.input_type = QLineEdit()
        self.input_type.setPlaceholderText("Type (Key, ControlKey, ..., other)")
        layout.addWidget(self.input_type)

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(lambda:self.new_hotkey())
        layout.addWidget(self.save_button)

        layout.setContentsMargins(5, 5, 5, 5) 
        layout.setSpacing(5) 
        self.setLayout(layout)

    def new_hotkey(self):
        input_hotkey_text = self.input_hotkey.text()
        input_type_text = self.input_type.text()

        if not input_hotkey_text or not input_type_text:
            QMessageBox.warning(self, "Input Error", "Please fill in both fields.")
            return

        reply = QMessageBox.question(self, "Save Hotkey", "Are you sure you want to save this hotkey?",
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                with sqlite3.connect("keyboard_data.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO keys (name, description, type) VALUES (?, ?, ?)",
                               (input_hotkey_text, " ", input_type_text))
                    conn.commit()

                self.input_hotkey.clear()
                self.input_type.clear()

                self.close()
                QMessageBox.information(self, "Success", "Hotkey saved successfully.")
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
            


class run_task():
    def __init__(self, step_details, repeat_amount):
        self.step_details = step_details
        self.repeat_amount = repeat_amount
        print(repeat_amount)
        time.sleep(3)
        self.execute_steps(step_details)

    def execute_steps(self, step_details):
        for i in range(self.repeat_amount):
            for index, step in enumerate(step_details, start=1):
                if isinstance(step, dict) and "action" in step:
                    action = step["action"]
                    if self.action_exists(action):
                        self.press_key(action)
                    elif action.lower().endswith("seconds"):
                        self.sleep_for_seconds(action)
                    else:
                        self.write_action(action)
                else:
                    print(f"Invalid step structure: {step}")
            time.sleep(1)

        

    def action_exists(self, action):
        return self.query_db("SELECT COUNT(*) FROM keys WHERE name = ?", (action,)) > 0

    def query_db(self, query, params=()):
        conn = sqlite3.connect("keyboard_data.db")
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()
        return result[0]

    def press_key(self, action):
        action = action.replace(" ", "")

        if "+" in action:
            keys = action.split("+")
            print(f"Simulating key combination: {keys}")
            keys = [key.lower() for key in keys]
            pyautogui.hotkey(*keys)
        else:
            print(f"Simulating key press: {action}")
            pyautogui.press(action)
        time.sleep(0.2)

    def sleep_for_seconds(self, action):
        try:
            sleep_time = int(action.lower().replace("seconds", "").strip())
            print(f"Sleeping for {sleep_time} seconds.")
            time.sleep(sleep_time)
        except ValueError:
            print(f"Invalid time format in action: {action}")

    def write_action(self, action):
        print(f"Executing action as string: {action}")
        keyboard.write(action)
        time.sleep(0.2)

class show_task():
    def __init__(self):
        pass
    def get_task(self, task_name):
        conn = sqlite3.connect("task_manager.db")
        cursor = conn.cursor()

        cursor.execute("SELECT title FROM tasks")
        tasks = cursor.fetchall()

        for task in tasks:
            if task[0] == task_name:
               # print(f"Task found: {task_name}")
                cursor.execute("SELECT * FROM tasks WHERE title = ?", (task_name,))
                task_details = cursor.fetchone()

                return task_details
        else:
            print(f"Task '{task_name}' not found.")
        
        conn.close()

    def get_steps(self, task_name):
        conn = sqlite3.connect("task_manager.db")
        cursor = conn.cursor()

        # Task-Details und Schritte basierend auf dem Titel abrufen
        cursor.execute("""
            SELECT t.title, t.description, s.step_order, s.action
            FROM tasks t
            JOIN steps s ON t.id = s.task_id
            WHERE t.title = ?
            ORDER BY s.step_order;
        """, (task_name,))
    
        steps = cursor.fetchall()

        if steps:
           # print(f"Steps for Task '{task_name}':")
            # for step in steps:
            #     print(f"Step {step[2]}: {step[3]}")

            step_details = {
                "title": steps[0][0],
                "description": steps[0][1],
                "steps": [{"step_order": step[2], "action": step[3]} for step in steps],
            }
            conn.close()
            return step_details["steps"]
        else:
            print(f"Task '{task_name}' not found.")
            conn.close()
            return None

        
class TaskManager():
    def __init__(self):
        pass
    def keys(self):
        conn = sqlite3.connect("keyboard_data.db")
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM keys")
        tasks = cursor.fetchall()
        conn.close()
        return tasks
        

    def save_tasks(self, title, description, task_dialog):
        self.title = title
        self.description = description

        now = datetime.now()
        formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
        self.created_at = formatted_now

        print(self.title, self.description, self.created_at)
        
        conn = sqlite3.connect("task_manager.db")
        cursor = conn.cursor()

        cursor.execute('''
        INSERT INTO tasks (title, description, created_at) VALUES (?, ?, ?)
        ''', (self.title, self.description, self.created_at))

        task_id = cursor.lastrowid

        
        items = task_dialog.get_all_items()
        for step_order, item_name in enumerate(items, start=1):
            cursor.execute('''
            INSERT INTO steps (task_id, step_order, action)
            VALUES (?, ?, ?)
            ''', (task_id, step_order, item_name))

        conn.commit()
        conn.close()



class Dialog_Manager(QDialog):
    def __init__(self,type,parent = None):
        super().__init__(parent)
        self.type = type
        self.setWindowTitle(f"Enter {type}")
        self.setFixedSize(300, 150)

        layout = QVBoxLayout()

        self.label = QLabel(f"Enter {type}:")
        layout.addWidget(self.label)

        self.input_field_text = QLineEdit()
        layout.addWidget(self.input_field_text) 

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.on_save)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def on_save(self):
        text = self.input_field_text.text()
        self.accept()
        return text

class TaskDialog(QDialog): 
    def __init__(self, task_manager, parent=None):
        super().__init__(parent)
        
        self.task_manager = task_manager
        self.setWindowTitle("Create Task")
        self.setFixedSize(300, 500)

        layout = QVBoxLayout()

        self.label = QLabel("Enter Task:")
        layout.addWidget(self.label)

        self.combo_box = QComboBox()
        self.combo_box.setFixedHeight(40)
        self.combo_box.setMaxVisibleItems(6)

        tasks = task_manager.keys()
        for task in tasks:
            self.combo_box.addItem(task[0])
        layout.addWidget(self.combo_box)


        self.add_button = QPushButton("Add Task")
        self.add_button.clicked.connect(self.add_task)
        layout.addWidget(self.add_button)

        self.task_listbox = QListWidget()
        self.task_listbox.setDragEnabled(True)  
        self.task_listbox.setAcceptDrops(True) 
        self.task_listbox.setDropIndicatorShown(True)
        self.task_listbox.setDefaultDropAction(Qt.MoveAction)
        layout.addWidget(self.task_listbox)
        
        self.label2 = QLabel("Enter Title:")
        layout.addWidget(self.label2)
        self.input_field_title = QLineEdit()
        layout.addWidget(self.input_field_title)

        self.label3 = QLabel("Enter Description:")
        layout.addWidget(self.label3)
        self.input_field_description = QLineEdit()
        layout.addWidget(self.input_field_description)


        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.on_save)
        layout.addWidget(self.save_button)

        layout.setContentsMargins(15, 15, 15, 15)
        self.setLayout(layout)
    
    def on_save(self):
        title = self.input_field_title.text()
        description = self.input_field_description.text() 
        self.task_manager.save_tasks(title, description, self)
        items = self.get_all_items()
        # for item in items:
        #     print(item)

        self.accept()

    def get_all_items(self):
        items = []
        for i in range(self.task_listbox.count()):
            item = self.task_listbox.item(i)
            items.append(item.text())
        return items

    def add_task(self):
        task = self.combo_box.currentText() 

        if task == "Text":  
            dialog = Dialog_Manager("Text" ,self)
            if dialog.exec() == QDialog.Accepted:
                text = dialog.on_save()
                self.task_listbox.addItem(text)
        elif task == "Wait":
            dialog = Dialog_Manager("Time (Seconds)",self)
            if dialog.exec() == QDialog.Accepted:
                text = dialog.on_save()
                self.task_listbox.addItem(f"{text} Seconds")

        elif task:
            self.task_listbox.addItem(task)
        else:
            QMessageBox.warning(self, "Input Error", "Please select a task.")



class HotkeyManager:
    def __init__(self):
        self.hotkey = ""

    def set_hotkey(self, hotkey):
        self.hotkey = hotkey
        QMessageBox.information(None, "Hotkey", f"Hotkey gesetzt: {self.hotkey}")

    def get_hotkey(self):
        return self.hotkey

class HotkeyDialog(QDialog):
    def __init__(self, hotkey_manager, parent=None):
        super().__init__(parent)
        self.hotkey_manager = hotkey_manager
        self.setWindowTitle("Set Hotkey")
        self.setFixedSize(300, 150)

        layout = QVBoxLayout()

        self.label = QLabel("Enter Hotkey:")
        layout.addWidget(self.label)

        self.input_field = QLineEdit()
        layout.addWidget(self.input_field)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_hotkey)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def save_hotkey(self):
        hotkey = self.input_field.text()
        self.hotkey_manager.set_hotkey(hotkey)
        self.accept()

class TaskManager_Gui(QMainWindow):
    def __init__(self):
        super().__init__()

        self.delete_button = None
        self.run_button = None

        self.setWindowIcon(QIcon('./to-do-list.png'))
        
        self.hotkey_manager = HotkeyManager()
        self.task_manager = TaskManager()

        self.settings = QSettings("Luca_Dev", "TaskManager")

        self.repeat_amount = 1

        self.setWindowTitle("Task Manager")
        self.setGeometry(100, 100, 600, 400)

        # Hauptlayout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        # Layout für Task-Listen und Button
        self.main_layout = QVBoxLayout()

        # Task Listbox
        self.task_listbox = QListWidget()
        self.main_layout.addWidget(self.task_listbox)

        # Füge den Hauptlayout zum zentralen Widget hinzu
        self.layout.addLayout(self.main_layout)

        # Füge den Button in einem separaten Layout hinzu
        self.bottom_layout = QVBoxLayout()  # Layout für den Button
        self.layout.addLayout(self.bottom_layout)

        self.create_menubar()
        self.create_toolbar()
        self.create_tables()

        self.restore_state()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_tasks_toolbar)  # Verbinde das Timeout-Signal mit show_tasks_toolbar
        self.timer.start(2000)

    def create_menubar(self):
        # Erstellen der nativen Menüleiste
        menu_bar = self.menuBar()

        # File Menu
        file_menu = QMenu("File", self)
        file_menu.addAction("Settings",self.open_settings)
        file_menu.addAction("Exit", self.close)
        menu_bar.addMenu(file_menu)

        # Hotkey Menu
        hotkey_menu = QMenu("Hotkey", self)
        hotkey_menu.addAction("Set Hotkey", self.open_hotkey_window)
        menu_bar.addMenu(hotkey_menu)

        # Task Menu
        task_menu = QMenu("Tasks", self)
        task_menu.addAction("Add Task", self.open_task_window)
        menu_bar.addMenu(task_menu)

        # Planner Menu
        planner_menu = QMenu("Planner", self)
        planner_menu.addAction("Task Repeat Amount", self.open_repeat_menu)
        planner_menu.addAction("Add Time", self.close)
        planner_menu.addAction("Show Time", self.close)
        menu_bar.addMenu(planner_menu)

    def create_toolbar(self):
        self.toolbar_tasks = QToolBar("Tasks", self)
        self.addToolBar(self.toolbar_tasks)

    def create_tables(self):
        connection = sqlite3.connect('task_manager.db')
        cursor = connection.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            step_order INTEGER NOT NULL,
            action TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
        );
        """)
        connection.commit()
        connection.close()
 
    def open_hotkey_window(self):
        dialog = HotkeyDialog(self.hotkey_manager, self)
        dialog.exec()
    def open_task_window(self):
        dialog = TaskDialog(self.task_manager, self)
        dialog.exec()
    def open_settings(self):
        dialog = Settings(self)
        dialog.exec()
    def open_repeat_menu(self):
        dialog = Planner(self)
        dialog.exec()
        self.repeat_amount = dialog.get_repeat_amount()

    def restore_state(self):
        try:
            with open("toolbar_state.dat", "rb") as f:
                state = f.read()
                self.restoreState(state)
               # print("Toolbar-Position geladen.")
        except FileNotFoundError:
            print("Kein gespeicherter Zustand gefunden, Standardwert wird verwendet.")

    def save_state(self):
        state = self.saveState()
        with open("toolbar_state.dat", "wb") as f:
            f.write(state)
       # print("Toolbar-Position gespeichert.")

    def closeEvent(self, event):
        self.save_state()
        event.accept()

    def show_tasks_toolbar(self):

        self.toolbar_tasks.clear()

        conn = sqlite3.connect("task_manager.db")
        cursor = conn.cursor()

        cursor.execute("SELECT title FROM tasks")
        tasks = cursor.fetchall()

        for task_title in tasks:
           # print(task_title[0])
            action = self.toolbar_tasks.addAction(task_title[0])
            action.triggered.connect(lambda checked, task_name=task_title[0]: self.on_task_clicked(task_name))


        conn.close()

    def on_task_clicked(self, task_name):
        self.task_listbox.clear()
        self.show_task = show_task()
        task_details = self.show_task.get_task(task_name)
        step_details = self.show_task.get_steps(task_name)

        if self.delete_button:
            self.layout.removeWidget(self.delete_button)
            self.delete_button.deleteLater()
        
        if self.run_button:
            self.layout.removeWidget(self.run_button)
            self.run_button.deleteLater()


        if task_details and step_details:
            task_id, title, description, created_at, updated_at = task_details

            self.task_listbox.addItem(f"ID: {task_id}")
            self.task_listbox.addItem(f"Title: {title}")
            self.task_listbox.addItem(f"Description: {description}")
            self.task_listbox.addItem(f"Created At: {created_at}")
            self.task_listbox.addItem(f"Updated At: {updated_at}")
            self.task_listbox.addItem(" ")

            for step in step_details:
                self.task_listbox.addItem(f"Step {step['step_order']}: {step['action']}")

           
            button_layout = QHBoxLayout()

            # Run Task Button
            self.run_button = QPushButton("Run Task")
            self.run_button.clicked.connect(lambda :run_task(step_details, self.repeat_amount))
            self.run_button.setStyleSheet("""
                QPushButton {
                    height: 12px;
                    background-color: #4CAF50;  /* Green background for run button */
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 10px;
                    border-radius: 8px;
                    margin-top: 5px;
                }
                QPushButton:hover {
                    background-color: #45a049;  /* Darker green on hover */
                }
            """)
            button_layout.addWidget(self.run_button)

            # Delete Task Button
            self.delete_button = QPushButton("Delete Task")
            self.delete_button.setStyleSheet("""
                QPushButton {
                    height: 12px;
                    background-color: #D32F2F;  /* Red background for delete button */
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 10px;
                    border-radius: 8px;
                    margin-top: 5px;
                }
                QPushButton:hover {
                    background-color: #ab2424;  /* Darker red on hover */
                }
            """)
            self.delete_button.clicked.connect(lambda checked, task_id=task_id: self.delete_task(task_id))

            button_layout.addWidget(self.delete_button)

            # Button-Layout zum Bottom-Layout hinzufügen
            self.bottom_layout.addLayout(button_layout)
        else:
                print(f"Task '{task_name}' not found.")

    def delete_task(self, task_id):
        # Bestätigungsdialog anzeigen, bevor die Aufgabe gelöscht wird
        reply = QMessageBox.question(self, "Delete Task", "Are you sure you want to delete this task?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = sqlite3.connect("task_manager.db")
            cursor = conn.cursor()

            # Lösche die Schritte für diese Aufgabe
            cursor.execute("DELETE FROM steps WHERE task_id = ?", (task_id,))
            # Lösche die Aufgabe selbst
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

            conn.commit()
            conn.close()

            print(f"Task with ID {task_id} deleted.")

            # Zeige die aktualisierte Task-Liste an
            self.show_tasks_toolbar()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Setze globales Stylesheet für Dark-Mode mit grünen Akzenten
    app.setStyleSheet("""
        QMainWindow {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        QMenuBar {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QMenuBar::item {
            background-color: transparent;
            padding: 5px 15px;
        }
        QMenuBar::item:selected {
            background-color: #3a3a3a;
        }
        QMenu {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QMenu::item:selected {
            background-color: #3a3a3a;
        }
        QListWidget {
            background-color: #262626;
            border: 1px solid #3a3a3a;
            color: #ffffff;
        }
        QPushButton {
            background-color: #4CAF50;
            color: #ffffff;
            border-radius: 5px;
            padding: 7px 10px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QLabel {
            color: #ffffff;
            font-size: 14px;
        }
        QLineEdit {
            background-color: #2b2b2b;
            color: #ffffff;
            border: 1px solid #3a3a3a;
            border-radius: 3px;
            padding: 5px;
        }
        QLineEdit:focus {
            border: 1px solid #4CAF50;
        }
    """)

    task_manager = TaskManager_Gui()
    task_manager.show()

    app.exec()
