# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import torch.nn as nn
from torch.optim import Adam, RMSprop

from .agent import CIMAgent
from maro.rl import AgentMode, SimpleAgentManager, LearningModel, DecisionLayers, ActorCritic, \
    ActorCriticHyperParameters
from maro.utils import set_seeds


def create_ac_agents(agent_id_list, mode, config):
    if mode in {AgentMode.TRAIN, AgentMode.TRAIN_INFERENCE}:
        return {agent_id: ActorCritic(
                            policy_model=None,
                            value_model=None,
                            value_loss_func=None,
                            policy_optimizer_cls=None,
                            policy_optimizer_params=None,
                            value_optimizer_cls=None,
                            value_optimizer_params=None,
                            hyper_params=None,
                            )
                for agent_id in agent_id_list}

    set_seeds(config.seed)
    num_actions = config.algorithm.num_actions
    agent_dict = {}

    for agent_id in agent_id_list:
        policy_model = LearningModel(
            decision_layers=DecisionLayers(
                name=f'{agent_id}.policy', input_dim=config.algorithm.input_dim, output_dim=num_actions,
                activation=nn.Tanh, **config.algorithm.policy_model
            )
        )

        value_model = LearningModel(
            decision_layers=DecisionLayers(
                name=f'{agent_id}.value', input_dim=config.algorithm.input_dim, output_dim=1,
                activation=nn.LeakyReLU, **config.algorithm.value_model
            )
        )

        algorithm = ActorCritic(
            policy_model=policy_model,
            value_model=value_model,
            value_loss_func=nn.functional.smooth_l1_loss,
            policy_optimizer_cls=Adam,
            policy_optimizer_params=config.algorithm.policy_optimizer,
            value_optimizer_cls=RMSprop,
            value_optimizer_params=config.algorithm.value_optimizer,
            hyper_params=ActorCriticHyperParameters(
                num_actions=num_actions,
                **config.algorithm.hyper_parameters,
            )
        )

        agent_dict[agent_id] = CIMAgent(name=agent_id, mode=mode, algorithm=algorithm)

    return agent_dict


class ACAgentManager(SimpleAgentManager):
    def train(self, experiences_by_agent: dict):
        for agent_id, experiences in experiences_by_agent.items():
            self.agent_dict[agent_id].train(experiences["states"], experiences["actions"], experiences["rewards"])
