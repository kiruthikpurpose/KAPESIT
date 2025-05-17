import numpy as np
class Agent:
    def __init__(self, agent_id, state_dim, action_dim):
        self.agent_id = agent_id
        self.state = np.zeros(state_dim)
        self.action_dim = action_dim
        self.memory = []
        self.policy = np.random.rand(action_dim)
    def observe(self, state):
        self.state = state
    def act(self):
        return np.argmax(self.policy + np.random.randn(self.action_dim) * 0.01)
    def update_policy(self, reward):
        self.policy += np.random.randn(self.action_dim) * reward * 0.01
    def communicate(self, message):
        return message + str(self.agent_id)
    def receive(self, message):
        self.memory.append(message)
class MultiAgentSystem:
    def __init__(self, num_agents, state_dim, action_dim):
        self.agents = [Agent(i, state_dim, action_dim) for i in range(num_agents)]
        self.global_state = np.zeros(state_dim)
        self.history = []
    def step(self, env_state):
        actions = []
        for agent in self.agents:
            agent.observe(env_state)
            action = agent.act()
            actions.append(action)
        self.global_state = env_state + np.random.randn(*env_state.shape) * 0.01
        self.history.append((env_state, actions))
        return actions
    def coordinate(self):
        messages = [agent.communicate("msg") for agent in self.agents]
        for i, agent in enumerate(self.agents):
            for j, msg in enumerate(messages):
                if i != j:
                    agent.receive(msg)
    def update(self, rewards):
        for agent, reward in zip(self.agents, rewards):
            agent.update_policy(reward)
    def run_episode(self, env_states, rewards):
        for state, reward in zip(env_states, rewards):
            actions = self.step(state)
            self.coordinate()
            self.update(reward)
        return self.history 