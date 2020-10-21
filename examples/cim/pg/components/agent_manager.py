# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import torch.nn as nn
from torch.optim import Adam, RMSprop

from .agent import CIMAgent
from maro.rl import AgentMode, SimpleAgentManager, LearningModel, DecisionLayers, PolicyGradient, \
    PolicyGradientHyperParameters
from maro.utils import set_seeds


def create_pg_agents(agent_id_list, mode, config):
    if mode in {AgentMode.TRAIN, AgentMode.TRAIN_INFERENCE}:
        return {agent_id: PolicyGradient(
                            policy_model=None,
                            optimizer_cls=None,
                            optimizer_params=None,
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

        algorithm = PolicyGradient(
            policy_model=policy_model,
            optimizer_cls=Adam,
            optimizer_params=config.algorithm.optimizer,
            hyper_params=PolicyGradientHyperParameters(
                num_actions=num_actions,
                **config.algorithm.hyper_parameters,
            )
        )

        agent_dict[agent_id] = CIMAgent(name=agent_id, mode=mode, algorithm=algorithm)

    return agent_dict


class PGAgentManager(SimpleAgentManager):
    def train(self, experiences_by_agent: dict):
        for agent_id, experiences in experiences_by_agent.items():
            self.agent_dict[agent_id].train(experiences["states"], experiences["actions"], experiences["rewards"])
