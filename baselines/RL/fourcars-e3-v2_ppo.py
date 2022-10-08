from spinup.utils.run_utils import ExperimentGrid
from spinup import ppo_pytorch
import torch
import gym
from spinup.utils.logx import Logger
from spinup.utils.test_policy import load_policy_and_env, run_policy

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    logger = Logger()

    eg = ExperimentGrid(name='fourcars-env3-v2_ppo')
    eg.add('env_name', 'gym_lass:HighwayFourCars-env3-v2', '', in_name=True)
    eg.add('seed', [50])
    eg.add('epochs', 100)
    eg.add('max_ep_len', 1000)
    eg.add('steps_per_epoch', 5000)
    eg.add('ac_kwargs:hidden_sizes', [(64, 64)], 'hid')
    eg.add('ac_kwargs:activation', [torch.nn.Tanh], '')
    eg.add('pi_lr', 1e-3)
    eg.add('vf_lr', 1e-2)
    eg.add('gamma', 0.99)
    output_dir = eg.run(ppo_pytorch, num_cpu=1)

    logger.log("Train finished! Press ENTER to continue...")
    input()
    # remake env and test policy
    _, get_action = load_policy_and_env(output_dir[0]) # TODO: display multi train results
    env = gym.make('HighwayFourCars-env3-v2', display=False, record=True)
    run_policy(env, get_action, num_episodes=1)
