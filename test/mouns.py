import pyautogui
import random
import time

# 测试pyautogui库

def main():
    pyautogui.moveTo(150, 150)
    start_time = time.time()
    while True:
        # 检查是否超过10秒钟
        if time.time() - start_time > 10:
            break
        # 生成随机坐标
        ranX = random.randint(100, 300)
        ranY = random.randint(100, 300)
        pyautogui.moveTo(ranX, ranY)
        time.sleep(0.5)  # 添加500毫秒的间隔


if __name__ == "__main__":
    main()