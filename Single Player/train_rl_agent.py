from shimmy import GymV26Compatibility
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from mario_kart_env import MarioKartEnv  

if __name__ == "__main__":
    raw_env = MarioKartEnv()

    #wrap
    env = GymV26Compatibility(raw_env)
    check_env(env, warn=True)

    model = PPO("CnnPolicy", env, verbose=1)
    model.learn(total_timesteps=10000) #train!
    model.save("ppo_mario_kart")

    #test model
    obs = env.reset()
    for _ in range(1000):
        action, _states = model.predict(obs)
        obs, rewards, done, info = env.step(action)
        if done:
            obs = env.reset()
