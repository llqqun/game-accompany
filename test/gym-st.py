import gymnasium as gym
from stable_baselines3 import A2C, PPO
import os
# 初始化环境
module_dir = './modules/PPO-test'
module_file_path = f'{module_dir}/LunarLander-v3-500.zip'
if not os.path.exists(module_dir):
    os.makedirs(module_dir)

env = gym.make("LunarLander-v3", render_mode="human")
env.reset()
model = PPO("MlpPolicy", env, verbose=1)
vec_env = model.get_env()
episodes = 5
TIMESETPS = 100
iters = 0

# 训练模型保存
""" while iters < episodes:
    iters += 1
    model.learn(total_timesteps=TIMESETPS, reset_num_timesteps=False)
    model.save(module_dir + f"/LunarLander-v3-{TIMESETPS * iters}") """

# 加载模型
if os.path.exists(module_file_path):
    model.load(module_file_path, env=env)

for _ in range(episodes):
    obs = vec_env.reset()
    done = False
    while not done:
        action, state = model.predict(obs, deterministic=True)
        obs, reward, done, info = vec_env.step(action)
        vec_env.render("human")
        print("观察值:", reward, done)


# print('查看所有可使用环境配置',gym.pprint_registry())

# 重置环境以生成第一个观察值
# observation, info = env.reset(seed=42)

# print("初始观察值:", observation, info)
# for _ in range(episodes):
#     done = False
#     while not done:
#         action, state = model.predict(obs, deterministic=True)
#         obs, reward, done, info = vec_env.step(action)
#         vec_env.render("human")
#         print("观察值:", reward, done)
""" 
    # 这里是插入你的策略的地方
    action = env.action_space.sample()
    # print("当前观察动作:", action)

    # 使用动作在环境中进行一步（过渡）
    # 接收下一个观察值、奖励以及该回合是否已终止或截断
    observation, reward, terminated, truncated, info = env.step(action)
    # print("当前观察动作结果:", action, terminated, truncated, info)

    # 如果回合已结束，我们可以重置以开始新回合
    if terminated or truncated:
        observation, info = env.reset() 
"""

# 关闭环境
env.close()