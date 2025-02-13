import torch
import cv2
import pyautogui
from PyQt6.QtWidgets import QApplication, QLabel
# from stable_baselines3 import PPO
# from stable_baselines3.common.env_util import make_vec_env

print(f"PyTorch版本: {torch.__version__}")
print(f"CUDA可用: {torch.cuda.is_available()}")
print(f"CUDA版本: {torch.version.cuda}")
print("OpenCV版本:", cv2.__version__)

# PyAutoGUI功能测试
# 获取鼠标当前位置
print(pyautogui.position())
# 截取屏幕左上角100x100区域
pyautogui.screenshot('test.png', region=(0,0,300,300))

# OpenCV图像处理测试
img = cv2.imread('test.png')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv2.imwrite('gray_test.png', gray)

# print('强化学习环境验证')
# env = make_vec_env('CartPole-v1', n_envs=1)
# model = PPO('MlpPolicy', env, verbose=1)
# model.learn(total_timesteps=10000)

app = QApplication([])
label = QLabel("环境测试成功！")
label.show()
app.exec()