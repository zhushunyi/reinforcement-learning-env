import gym
from gym import spaces
import numpy as np
import random


class water_pump(gym.Env):
    # node initialize
    class node():
        def __init__(self):
            self.issatisfied = 0
            self.min = 0.15
            self.max = 0.4
            self.isover = 0
            self.pressure = 0

        def update(self, action):
            if action == '000':
                return
            for i in range(0, len(action)):
                if action[i] == '1':
                    self.pressure = self.pressure + 0.1
                if action[i] == '2':
                    self.pressure = self.pressure - 0.1
            if self.pressure >= self.min:
                self.issatisfied = 1
                self.over = 0
            if self.pressure > self.max:
                self.over = 1
            if self.pressure < self.min:
                self.issatisfied = self.over = 0
            return

        def satisfied(self):
            return self.issatisfied == 1

        def over(self):
            return self.isover == 1

        def node_reset(self):
            self.pressure = 0
            self.issatisfied = 0
            self.isover = 0

        def get_rewarcd(self, action):
            if action == '000':
                if self.isover == 1:
                    return -13
                else:
                    return 0
            if self.isover == 0 and self.issatisfied == 1:
                return 10
            if self.issatisfied == 0 and self.isover == 0:
                return 0

    matadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second': 2
    }

    def __init__(self):
        self.node_1 = self.node()
        self.node_2 = self.node()
        self.node_3 = self.node()
        self.node_4 = self.node()
        self.node_5 = self.node()
        self.node_6 = self.node()
        self.node_7 = self.node()
        # 7 nodes
        self.node_list = [self.node_1, self.node_2, self.node_3, self.node_4, self.node_5, self.node_6, self.node_7]
        self.states = [i for i in range(0, 128)]
        self.terminate_states = dict()  # terminate state
        self.terminate_states[127] = 1
        self.actions = [i for i in range(0, 8)]
        self.wp1 = 0
        self.wp2 = 0
        self.wp3 = 0
        # choice to turn on
        self.turnon_choice = [1, 2, 3]
        self.turnoff_choice = []

        # discount factor
        self.gamma = 0.8

        self.viewer = None
        self.state = None

    def getTerminal(self):
        return self.terminate_states

    def getGamma(self):
        return self.gamma

    def getStates(self):
        return self.states

    def getActions(self):
        return self.actions

    def setAction(self, s):
        self.state = s

    def ActionState(self, current, next):
        str = ''
        for i in range(0, len(current)):
            if current[i] == next[i]:
                str = str + '0'
            if current[i] > next[i]:
                str = str + '1'
            if current[i] < next[i]:
                str = str + '2'
        return str

    def StateUpdate(self, state, action):
        if action == '000':
            next_state = state
        else:
            str = ''
            state_str = bin(state)[2:]
            num = 0
            for i in action:
                if i == '0':
                    str = str + state_str[num]
                if i == '1':
                    str = str + '1'
                if i == '2':
                    str = str + '0'
                num = num + 1
            next_state = int(str, 2)
            return next_state

    def ActionSelection(self, state):
        '''action_set = []
        for i in self.actions:
            action_set.append(bin(i)[2:])'''
        # eliminate the actions that cannot be chosen
        ac_1 = ['0', '1', '2']
        ac_2 = ['0', '1', '2']
        ac_3 = ['0', '1', '2']
        if state[0] == '0':
            ac_1.remove('2')
        if state[0] == '1':
            ac_1.remove('1')
        if state[1] == '0':
            ac_2.remove('2')
        if state[1] == '1':
            ac_2.remove('1')
        if state[2] == '0':
            ac_3.remove('2')
        if state[2] == '1':
            ac_3.remove('1')
        index = np.random.randint(0,2,size = 3)
        action = ac_1[index[0]] + ac_2[index[1]] + ac_3[index[2]]
        return action

    def _step(self, action):
        # current state
        state = self.state
        if state in self.terminate_states:
            return state, 0, True, {}
        if action == '000':
            next_state = state
        else:
            next_state = self.StateUpdate(action)

        self.state = next_state

        isterminal = False
        if next_state in self.terminate_states:
            isterminal = True

        reward = 0
        for i in self.node_list:
            reward = reward + i.get_rewarcd(action)

        return next_state, reward, isterminal, {}

    def _reset(self):
        self.state = 0
        return self.state