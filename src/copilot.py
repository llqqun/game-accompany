import sys
import json
import time
import ctypes
import numpy as np
import cv2
import pyautogui
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QMessageBox, QFileDialog, QLabel, QComboBox, QDialog, QListWidget
import psutil
import pygetwindow as gw
from PyQt6.QtCore import Qt


class GameAssistant(QWidget):
    def __init__(self):
        super().__init__()
        self.steps = []
        self.recording = False
        self.learning = False
        self.current_game = None
        self.game_hwnd = None  # 保存游戏窗口句柄

        # Q - learning 参数
        self.alpha = 0.1  # 学习率
        self.gamma = 0.9  # 折扣因子
        self.epsilon = 0.9  # 探索率
        self.q_table = {}  # Q 表

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.game_label = QLabel('当前游戏: 未选择')
        layout.addWidget(self.game_label)

        self.select_game_button = QPushButton('选择游戏')
        self.select_game_button.clicked.connect(self.select_game)
        layout.addWidget(self.select_game_button)

        self.start_record_button = QPushButton('开始记录')
        self.start_record_button.clicked.connect(self.start_recording)
        layout.addWidget(self.start_record_button)

        self.stop_record_button = QPushButton('停止记录')
        self.stop_record_button.clicked.connect(self.stop_recording)
        self.stop_record_button.setEnabled(False)
        layout.addWidget(self.stop_record_button)

        self.save_record_button = QPushButton('保存记录')
        self.save_record_button.clicked.connect(self.save_recording)
        self.save_record_button.setEnabled(False)
        layout.addWidget(self.save_record_button)

        self.load_record_button = QPushButton('加载记录')
        self.load_record_button.clicked.connect(self.load_recording)
        layout.addWidget(self.load_record_button)

        self.execute_record_button = QPushButton('执行记录')
        self.execute_record_button.clicked.connect(self.execute_recording)
        self.execute_record_button.setEnabled(False)
        layout.addWidget(self.execute_record_button)

        self.start_learning_button = QPushButton('开始学习')
        self.start_learning_button.clicked.connect(self.start_learning)
        layout.addWidget(self.start_learning_button)

        self.stop_learning_button = QPushButton('停止学习')
        self.stop_learning_button.clicked.connect(self.stop_learning)
        self.stop_learning_button.setEnabled(False)
        layout.addWidget(self.stop_learning_button)

        self.setLayout(layout)
        self.setWindowTitle('游戏助手')
        self.show()

    def select_game(self):
        QMessageBox.information(self, '选择游戏', '请点击目标游戏窗口')
        self.setWindowOpacity(0.5)
        self.showMinimized()
        time.sleep(2)  # 给用户时间去点击目标窗口

        hwnd = pyautogui.getActiveWindow()
        print(hwnd)
        if hwnd:
            self.current_game = hwnd.title
            self.game_label.setText(f'当前游戏: {self.current_game}')
            self.game_hwnd = {'name': hwnd.title, 'x': hwnd.left, 'y': hwnd.top }
        else:
            QMessageBox.critical(self, '选择失败', '未找到目标窗口')

        self.setWindowOpacity(1)
        self.showNormal()

    def start_recording(self):
        self.recording = True
        self.start_record_button.setEnabled(False)
        self.stop_record_button.setEnabled(True)
        self.save_record_button.setEnabled(False)
        self.execute_record_button.setEnabled(False)
        self.steps = []
        self.record()

    def stop_recording(self):
        self.recording = False
        self.start_record_button.setEnabled(True)
        self.stop_record_button.setEnabled(False)
        self.save_record_button.setEnabled(True)
        if self.steps:
            self.execute_record_button.setEnabled(True)

    def save_recording(self):
        file_path, _ = QFileDialog.getSaveFileName(self, '保存记录', '', 'JSON files (*.json)')
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.steps, f)
                QMessageBox.information(self, '保存成功', f'记录已保存到 {file_path}')
            except Exception as e:
                QMessageBox.critical(self, '保存失败', f'保存记录时出错: {str(e)}')

    def load_recording(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '加载记录', '', 'JSON files (*.json)')
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    self.steps = json.load(f)
                QMessageBox.information(self, '加载成功', f'记录已从 {file_path} 加载')
                self.execute_record_button.setEnabled(True)
            except Exception as e:
                QMessageBox.critical(self, '加载失败', f'加载记录时出错: {str(e)}')

    def execute_recording(self):
        for step in self.steps:
            action, args = step
            if action == 'click':
                x, y = args
                if self.is_within_game_window(x, y):
                    pyautogui.click(x, y)
            elif action == 'typewrite':
                text = args
                pyautogui.typewrite(text)
            time.sleep(0.5)

    def is_within_game_window(self, x, y):
        if self.game_hwnd:
            window = gw.getWindowsWithTitle(self.game_hwnd['name'])[0]
            if window:
                left, top, right, bottom = window.left, window.top, window.right, window.bottom
                return left <= x <= right and top <= y <= bottom
        return False

    def record(self):
        if self.recording:
            x, y = pyautogui.position()
            if pyautogui.mouseDown():
                self.steps.append(('click', (x, y)))
            QApplication.processEvents()
            QApplication.instance().thread().sleep(0.1)
            self.record()

    def start_learning(self):
        if not self.current_game:
            QMessageBox.warning(self, '未选择游戏', '请先选择一个游戏')
            return

        self.learning = True
        self.start_learning_button.setEnabled(False)
        self.stop_learning_button.setEnabled(True)
        # self.activate_game()
        self.move_mouse_to_game_window()
        self.learning_loop()

    def move_mouse_to_game_window(self):
        if self.game_hwnd:
            print(self.game_hwnd['name'])
            window = gw.getWindowsWithTitle(self.game_hwnd['name'])[0]
            print(window)
            if window:
                x = (window.left + window.right) // 2
                y = (window.top + window.bottom) // 2
                pyautogui.moveTo(x, y)
                pyautogui.click()

    def activate_game(self):
        if self.game_hwnd:
            pid = self.game_hwnd['pid']
            try:
                proc = psutil.Process(pid)
                proc.resume()
                # 激活窗口
                windows = gw.getWindowsWithTitle(proc.name())
                print(windows)
                if windows:
                    window = windows[0]
                    window.restore()
                    window.activate()
                else:
                    QMessageBox.critical(self, '激活失败', '未找到游戏窗口')
            except Exception as e:
                QMessageBox.critical(self, '激活失败', f'激活游戏进程时出错: {str(e)}')

    def stop_learning(self):
        self.learning = False
        self.start_learning_button.setEnabled(True)
        self.stop_learning_button.setEnabled(False)

    def detect_human_intervention(self):
        initial_mouse_pos = pyautogui.position()
        time.sleep(0.1)
        current_mouse_pos = pyautogui.position()
        if initial_mouse_pos != current_mouse_pos or pyautogui.mouseDown():
            return True
        return False

    #截取当前屏幕的截图，并将其转换为一个状态表示。这个状态表示是通过计算截图的平均颜色值来实现的
    def get_state(self):
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        state = tuple(np.mean(screenshot, axis=(0, 1)).astype(int))
        return state

    def get_reward(self):
        return 1

    #根据当前状态选择一个动作
    def choose_action(self, state):
        if state not in self.q_table:
            actions = [('click', (100, 100)), ('click', (200, 200))]
            self.q_table[state] = {action: 0 for action in actions}
        if np.random.uniform(0, 1) < self.epsilon:
            action = list(self.q_table[state].keys())[np.random.choice(len(self.q_table[state]))]
        else:
            action = max(self.q_table[state], key=self.q_table[state].get)
        return action

    def update_q_table(self, state, action, reward, next_state):
        if state not in self.q_table:
            actions = [('click', (100, 100)), ('click', (200, 200))]
            self.q_table[state] = {action: 0 for action in actions}
        if next_state not in self.q_table:
            actions = [('click', (100, 100)), ('click', (200, 200))]
            self.q_table[next_state] = {action: 0 for action in actions}
        max_q_next = max(self.q_table[next_state].values())
        self.q_table[state][action] = (1 - self.alpha) * self.q_table[state][action] + \
                                      self.alpha * (reward + self.gamma * max_q_next)

    def learning_loop(self):
        if self.learning:
            if self.detect_human_intervention():
                self.stop_learning()
                QMessageBox.information(self, '学习停止', '检测到人为干预，学习过程已停止')
                return

            # 获取当前状态
            state = self.get_state()
            # 根据当前状态选择动作
            action = self.choose_action(state)
            action_type, args = action
            print(action_type, args)
            if action_type == 'click':
                x, y = args
                if self.is_within_game_window(x, y):
                    # 移动鼠标并点击
                    pyautogui.moveTo(x, y)
                    pyautogui.click()
            elif action_type == 'typewrite':
                text = args
                # 执行动作
                pyautogui.typewrite(text)
            time.sleep(0.5)
            # 获取下一个状态
            next_state = self.get_state()
            # 获取奖励
            reward = self.get_reward()
            # 更新 Q 表
            self.update_q_table(state, action, reward, next_state)
            print(f"State: {state}, Action: {action}, Reward: {reward}, Next State: {next_state}")
            QApplication.processEvents()
            QApplication.instance().thread().sleep(1)
            self.learning_loop()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GameAssistant()
    sys.exit(app.exec())