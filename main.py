"""
********************************************************************************
*                                                                              *
*                          TIME KEEPER                                         *
*                                                                              *
* Author: John Flammer                                                         *
* Email: johnf@proficientpc.com                                                *
* Website: www.proficientpc.com                                                *
*                                                                              *
********************************************************************************
"""
import os
import sys
import csv
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
        self.action_export_to_file = QAction("Export to File", self)
        self.settings_menu.addAction(self.action_export_to_file)
        self.action_export_to_file.triggered.connect(self.export_to_file)
        
    def export_to_file(self):
        db = self.create_database_connection()
        cursor = db.cursor()
        sql = "SELECT * FROM tasks"
        cursor.execute(sql)
        tasks = cursor.fetchall()
        # Get column names for the CSV headers
        column_names = [i[0] for i in cursor.description]
        cursor.close()
        db.close()
        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(script_dir, 'task_data.csv')

        try:
            with open(file_path, 'w') as f:
                writer = csv.writer(f)
                writer.writerow(column_names)
                for task in tasks:
                    # Convert the start_time and end_time to 12 hour format
                    if not self.action_24hour_format.isChecked():
                        task = list(task)
                        if task[2]:  # start_time is not None
                            task[2] = task[2].strftime('%I:%M:%S %p')
                        if task[3]:  # end_time is not None
                            task[3] = task[3].strftime('%I:%M:%S %p')
                    writer.writerow(task)
            # Show a message box indicating successful export
            QMessageBox.information(self, "Export Success", "Data has been successfully exported.")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export data: {e}")

    def update_current_time(self):
        if self.action_24hour_format.isChecked():
            current_time = QTime.currentTime().toString('HH:mm:ss')
        else:
            current_time = QTime.currentTime().toString('hh:mm:ss AP')
        self.current_time_label.setText(current_time)
        
    def load_tasks_from_database(self):
        db = self.create_database_connection()
        cursor = db.cursor()
        sql = "SELECT task_name, duration FROM tasks"
        cursor.execute(sql)
        tasks = cursor.fetchall()
        for task in tasks:
            self.task_comboBox.addItem(task[0])
            self.task_times[task[0]] = task[1] * 1000  # Converting duration from seconds to milliseconds
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

    def start_task(self):
        if self.current_task:
            db = self.create_database_connection()
            cursor = db.cursor()
            sql = """
            UPDATE tasks 
            SET start_time = NOW() 
            WHERE task_name = %s
            """
            val = (self.current_task,)
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()

    def start_stop_timer(self):
        task_name = self.task_line_edit.text().strip()
        if not task_name and not self.current_task:
            QMessageBox.warning(self, "No Task Selected", "Please select or a task before starting the timer.")
            return
        if self.timer_is_running:
            self.timer.stop()
            self.start_stop_timer_button.setText('Start')
            self.start_stop_timer_button.setStyleSheet("background-color: green")
            if self.current_task:
                self.task_times[self.current_task] += self.elapsed_timer.elapsed()
            self.end_task()  # Update end_time and duration in database
            self.elapsed_timer.restart()
            self.timer_is_running = False
        else:   
            if task_name:
                self.add_task()
                index = self.task_comboBox.findText(task_name)
                self.task_comboBox.setCurrentIndex(index)
                self.current_task = self.task_comboBox.currentText()
                if self.current_task not in self.task_times:
                    self.task_times[self.current_task] = 0
            self.timer.start(1000)
            self.start_stop_timer_button.setText('Pause')  # Change here
            self.start_stop_timer_button.setStyleSheet("background-color: red")
            self.elapsed_timer.start()
            self.start_task()  # Record the start time in database
            self.timer_is_running = True
        self.task_line_edit.setText(self.current_task)
        
    def task_exists(self, task_name):
        db = self.create_database_connection()
        cursor = db.cursor()
        sql = "SELECT task_name FROM tasks WHERE task_name = %s"
        val = (task_name,)
        cursor.execute(sql, val)
        result = cursor.fetchone()
        cursor.close()
        db.close()
        return result is not None

    def update_task_time_in_database(self, task_name, total_elapsed_msec):
        db = self.create_database_connection()
        cursor = db.cursor()
        sql = "UPDATE tasks SET total_elapsed_msec = %s WHERE task_name = %s"
        val = (total_elapsed_msec, task_name)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
    
    def stop_task(self):
        self.task_times[self.current_task] += self.elapsed_timer.elapsed()
        self.update_task_time_in_database(self.current_task, self.task_times[self.current_task])

    def update_timer(self):
        if self.current_task:
            elapsed_msec = self.elapsed_timer.elapsed()
            total_elapsed_time = QTime.fromMSecsSinceStartOfDay(self.task_times[self.current_task] + elapsed_msec)
            text = total_elapsed_time.toString('hh:mm:ss')
            self.timer_label.setText(f'<p align="right">{text}</p>')
        self.date_label.setText(QDate.currentDate().toString())

    def create_database_connection(self):
        return mysql.connector.connect(
            host="192.168.1.1",
            user="johnf_time_keeper0001",
            password="*******",
            database="time_keeper_database"
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
            confirmation = QMessageBox.question(self, 'Confirmation', "Are you sure you want to remove this task?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if confirmation == QMessageBox.Yes:
                task_name = self.task_comboBox.currentText()
                self.task_comboBox.removeItem(current_index)
                db = self.create_database_connection()
                cursor = db.cursor()
                sql = "DELETE FROM tasks WHERE task_name = %s"
                val = (task_name,)
                cursor.execute(sql, val)
                db.commit()
                cursor.close()
                db.close()
    
    def change_task(self):
        new_task = self.task_comboBox.currentText()
        if self.timer_is_running:
            QMessageBox.warning(self, "Timer Running", "Please stop the timer before changing tasks.")
            index = self.task_comboBox.findText(self.current_task)
            self.task_comboBox.setCurrentIndex(index)
        else:
            self.current_task = new_task
            self.task_line_edit.setText(self.current_task)
            # Update the timer label with stored time for the selected task
            if self.current_task in self.task_times:
                stored_time = QTime.fromMSecsSinceStartOfDay(self.task_times[self.current_task])
                self.timer_label.setText(stored_time.toString('hh:mm:ss'))
            else:
                self.timer_label.setText('00:00:00')
    
    def end_task(self):
        if self.current_task:
            db = self.create_database_connection()
            cursor = db.cursor()
            sql = """
            UPDATE tasks 
            SET end_time = NOW(), 
                duration = TIMESTAMPDIFF(SECOND, start_time, end_time) 
            WHERE task_name = %s AND end_time IS NULL
            """
            val = (self.current_task,)
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
        
    def closeEvent(self, event):
        if self.timer_is_running:
            reply = QMessageBox.question(self, 'Warning', "Timer is still running. Are you sure you want to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.end_task()  # End the task if user decides to quit
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
