import gymnasium as gym

# 初始化环境
env = gym.make("LunarLander-v3", render_mode="human")

# 重置环境以生成第一个观察值
observation, info = env.reset(seed=42)
for _ in range(1000):
    # 这里是插入你的策略的地方
    action = env.action_space.sample()

    # 使用动作在环境中进行一步（过渡）
    # 接收下一个观察值、奖励以及该回合是否已终止或截断
    observation, reward, terminated, truncated, info = env.step(action)

    # 如果回合已结束，我们可以重置以开始新回合
    if terminated or truncated:
        observation, info = env.reset()

# 关闭环境
env.close()