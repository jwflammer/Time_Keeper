import os
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QComboBox, QAction
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, QTimer, QTime, QDate, QPoint, QElapsedTimer
from PyQt5.QtWidgets import QMenu
import mysql.connector

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        myAppUI = os.path.join(os.path.dirname(__file__), "time_keeper.ui")
        loadUi(myAppUI, self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        try:
            with open('time_keeper_style.css', 'r') as style_sheet:
                self.setStyleSheet(style_sheet.read())
                style_sheet.close()
        except Exception as e:
            print(f"Could not load style sheet: {e}")
        self.close_button.clicked.connect(self.close)
        self.min_button.clicked.connect(self.showMinimized)
        self.start_stop_timer_button.clicked.connect(self.start_stop_timer)
        self.add_task_button.clicked.connect(self.add_task)
        self.remove_task_button.clicked.connect(self.remove_task)
        self.task_comboBox.currentIndexChanged.connect(self.change_task)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer_is_running = False
        self.elapsed_timer = QElapsedTimer()
        self.drag_start_position = None
        self.total_elapsed_msec = 0
        self.current_task = None
        self.task_times = {}
        self.load_tasks_from_database()
        self.settings_menu = QMenu(self)
        self.settings_menu_button.setMenu(self.settings_menu)
        self.settings_menu_button.setEnabled(True)
        self.action_24hour_format = QAction("24 Hour Format", self)
        self.action_24hour_format.setCheckable(True)
        self.settings_menu.addAction(self.action_24hour_format)
        self.date_label.setText(QDate.currentDate().toString())
        self.current_time_timer = QTimer(self)
        self.current_time_timer.timeout.connect(self.update_current_time)
        self.current_time_timer.start(1000)
        self.update_current_time()

    def update_current_time(self):
        if self.action_24hour_format.isChecked():
            current_time = QTime.currentTime().toString('HH:mm:ss')
        else:
            current_time = QTime.currentTime().toString('hh:mm:ss AP')
        self.current_time_label.setText(current_time)
        
    def load_tasks_from_database(self):
        db = self.create_database_connection()
        cursor = db.cursor()

        sql = "SELECT task_name FROM tasks"
        cursor.execute(sql)

        tasks = cursor.fetchall()

        for task in tasks:
            self.task_comboBox.addItem(task[0])

        cursor.close()
        db.close()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.drag_start_position = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.RightButton and self.drag_start_position:
            self_pos = self.pos()
            new_position = self_pos + (event.globalPos() - self.drag_start_position)
            self.move(new_position)
            self.drag_start_position = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton and self.drag_start_position:
            self.drag_start_position = None

    def start_stop_timer(self):
        task_name = self.task_line_edit.text().strip()
        new_task = None

        if task_name:
            self.add_task()
            index = self.task_comboBox.findText(task_name)
            self.task_comboBox.setCurrentIndex(index)
            new_task = self.task_comboBox.currentText()

        if not new_task and not self.current_task:
            QMessageBox.warning(self, "No Task Selected", "Please select or a task before starting the timer.")
            return

        if self.timer_is_running:
            if new_task != self.current_task:
                self.timer.stop()
                self.start_stop_timer_button.setText('Start')
                self.start_stop_timer_button.setStyleSheet("background-color: green")
                if self.current_task:
                    self.task_times[self.current_task] += self.elapsed_timer.elapsed()
                self.elapsed_timer.restart()
                self.timer.start(1000)
                self.start_stop_timer_button.setText('Stop')
                self.start_stop_timer_button.setStyleSheet("background-color: red")
                if new_task and new_task not in self.task_times:
                    self.task_times[new_task] = 0
                self.current_task = new_task if new_task else self.current_task
                self.elapsed_timer.start()
                self.timer_is_running = True
            else:
                self.timer.stop()
                self.start_stop_timer_button.setText('Start')
                self.start_stop_timer_button.setStyleSheet("background-color: green")
                if self.current_task:
                    self.task_times[self.current_task] += self.elapsed_timer.elapsed()
                    self.insert_task_time(self.current_task, "stop")
                self.elapsed_timer.restart()
                self.timer_is_running = False
        else:   
            self.timer.start(1000)
            self.start_stop_timer_button.setText('Stop')
            self.start_stop_timer_button.setStyleSheet("background-color: red")
            if new_task and new_task not in self.task_times:
                self.task_times[new_task] = 0
                self.insert_task_time(new_task, "start")
            self.current_task = new_task if new_task else self.current_task
            self.elapsed_timer.start()
            self.timer_is_running = True

        self.task_line_edit.setText(self.current_task)
        
    def insert_task_time(self, task_name, action):
        db = self.create_database_connection()
        cursor = db.cursor()

        sql = "INSERT INTO task_times (task_name, action, timestamp) VALUES (%s, %s, NOW())"
        val = (task_name, action)
        cursor.execute(sql, val)

        db.commit()

        cursor.close()
        db.close()

    def update_timer(self):
        if self.current_task:
            elapsed_msec = self.elapsed_timer.elapsed()
            total_elapsed_time = QTime.fromMSecsSinceStartOfDay(self.task_times[self.current_task] + elapsed_msec)
            text = total_elapsed_time.toString('hh:mm:ss')
            self.timer_label.setText(f'<p align="right">{text}</p>')
        self.date_label.setText(QDate.currentDate().toString())

    def create_database_connection(self):
        return mysql.connector.connect(
            host="your_host",
            user="johnf_time_keeper0001",
            password="your_password",
            database="time_keeper"
        )
        
    def insert_task(self, task_name):
        db = self.create_database_connection()
        cursor = db.cursor()

        sql = "INSERT INTO tasks (task_name) VALUES (%s)"
        val = (task_name,)
        cursor.execute(sql, val)

        db.commit()

        cursor.close()
        db.close()
        
    def add_task(self):
        task_name = self.task_line_edit.text()
        if task_name:
            if self.task_comboBox.findText(task_name) == -1:
                self.task_comboBox.addItem(task_name)
                self.insert_task(task_name)
            self.task_line_edit.clear()
            
    def remove_task(self):
        current_index = self.task_comboBox.currentIndex()
        if current_index != -1:
            self.task_comboBox.removeItem(current_index)
    
    def change_task(self):
        new_task = self.task_comboBox.currentText()
        if self.timer_is_running:
            QMessageBox.warning(self, "Timer Running", "Please stop the timer before changing tasks.")
            index = self.task_comboBox.findText(self.current_task)
            self.task_comboBox.setCurrentIndex(index)
        else:
            self.current_task = new_task
            self.task_line_edit.setText(self.current_task)
            
    def closeEvent(self, event):
        if self.timer_is_running:
            reply = QMessageBox.question(self, 'Warning', "Timer is still running. Are you sure you want to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())