import sys
import json
import time
import numpy as np
import cv2
import pyautogui
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QMessageBox, QFileDialog


class GameAssistant(QWidget):
    def __init__(self):
        super().__init__()
        self.steps = []
        self.recording = False
        self.learning = False

        # Q - learning 参数
        self.alpha = 0.1  # 学习率
        self.gamma = 0.9  # 折扣因子
        self.epsilon = 0.1  # 探索率
        self.q_table = {}  # Q 表

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

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
                pyautogui.click(x, y)
            elif action == 'typewrite':
                text = args
                pyautogui.typewrite(text)
            time.sleep(0.5)

    def record(self):
        if self.recording:
            x, y = pyautogui.position()
            if pyautogui.mouseDown():
                self.steps.append(('click', (x, y)))
            QApplication.processEvents()
            QApplication.instance().thread().sleep(0.1)
            self.record()

    def start_learning(self):
        self.learning = True
        self.start_learning_button.setEnabled(False)
        self.stop_learning_button.setEnabled(True)
        self.learning_loop()

    def stop_learning(self):
        self.learning = False
        self.start_learning_button.setEnabled(True)
        self.stop_learning_button.setEnabled(False)

    def get_state(self):
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        state = tuple(np.mean(screenshot, axis=(0, 1)).astype(int))
        return state

    def get_reward(self):
        return 1

    def choose_action(self, state):
        if state not in self.q_table:
            actions = [('click', (100, 100)), ('click', (200, 200))]
            self.q_table[state] = {action: 0 for action in actions}
        if np.random.uniform(0, 1) < self.epsilon:
            action = np.random.choice(list(self.q_table[state].keys()))
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
            state = self.get_state()
            action = self.choose_action(state)
            action_type, args = action
            if action_type == 'click':
                x, y = args
                pyautogui.click(x, y)
            elif action_type == 'typewrite':
                text = args
                pyautogui.typewrite(text)
            time.sleep(0.5)
            next_state = self.get_state()
            reward = self.get_reward()
            self.update_q_table(state, action, reward, next_state)
            QApplication.processEvents()
            QApplication.instance().thread().sleep(1)
            self.learning_loop()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GameAssistant()
    sys.exit(app.exec())