# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 14:12:47 2021

@author: Suleman_Sahib
"""

# Import necessary libraries
import tensorflow as tf
import gym
from gym.wrappers import Monitor
from collections import deque
import numpy as np
import random
import math
import time
import glob
import io
import base64
import matplotlib.pyplot as plt

from MDP_Development1 import HEMS_MDP
#from MDP_Test_DQN import HEMS_MDP

start = time.time()

# Initialize environment and get the number of state features and actions
env = HEMS_MDP()
num_features = env.observation_shape[0]
num_actions = env.action_space.n
print('Number of state features: {}'.format(num_features))
print('Number of possible actions: {}'.format(num_actions))

class DQN(tf.keras.Model):
  """Define the neural network (Q-network) for DQN."""
  def __init__(self):
    super(DQN, self).__init__()
    # Define layers of the network (fully connected)
    self.dense1 = tf.keras.layers.Dense(16, activation="relu")
    self.dense2 = tf.keras.layers.Dense(16, activation="relu")
    self.dense3 = tf.keras.layers.Dense(16, activation="relu")
    self.dense4 = tf.keras.layers.Dense(16, activation="relu")
    self.dense5 = tf.keras.layers.Dense(num_actions, dtype=tf.float32)  # Output layer for Q-values
    
  def call(self, x):
    """Forward pass of the neural network."""
    x = self.dense1(x)
    x = self.dense2(x)
    x = self.dense3(x)
    x = self.dense4(x)
    return self.dense5(x)  # Return the Q-values for each action

# Initialize two DQN models (main network and target network)
main_nn = DQN()
target_nn = DQN()

# Optimizer and loss function setup
optimizer = tf.keras.optimizers.Adam(1e-5)  # Adam optimizer with learning rate
mse = tf.keras.losses.MeanSquaredError()  # Mean Squared Error loss function

# Define replay buffer to store experience (state, action, reward, next_state, done)
class ReplayBuffer(object):
  """Experience replay buffer that samples uniformly."""
  def __init__(self, size):
    self.buffer = deque(maxlen=size)

  def add(self, state, action, reward, next_state, done):
    """Add experience tuple to the buffer."""
    self.buffer.append((state, action, reward, next_state, done))

  def __len__(self):
    """Return the size of the buffer."""
    return len(self.buffer)

  def sample(self, num_samples):
    """Sample a batch of experiences from the buffer."""
    states, actions, rewards, next_states, dones = [], [], [], [], []
    idx = np.random.choice(len(self.buffer), num_samples)  # Random indices
    for i in idx:
      elem = self.buffer[i]
      state, action, reward, next_state, done = elem
      states.append(np.array(state, copy=False))
      actions.append(np.array(action, copy=False))
      rewards.append(reward)
      next_states.append(np.array(next_state, copy=False))
      dones.append(done)
    # Return arrays of states, actions, rewards, etc.
    states = np.array(states, dtype=np.float32)
    actions = np.array(actions)
    rewards = np.array(rewards, dtype=np.float32)
    next_states = np.array(next_states, dtype=np.float32)
    dones = np.array(dones, dtype=np.float32)
    return states, actions, rewards, next_states, dones

# Epsilon-greedy action selection
def select_epsilon_greedy_action(state, epsilon):
  """Take random action with probability epsilon, else take best action."""
  result = tf.random.uniform((1,))
  if result < epsilon:
    return env.action_space.sample()  # Random action (left or right)
  else:
    return tf.argmax(main_nn(state)[0]).numpy()  # Greedy action for state

@tf.function
def train_step(states, actions, rewards, next_states, dones):
  """Perform a training iteration on a batch of data sampled from the experience
  replay buffer."""
  # Calculate targets using Bellman equation
  next_qs = target_nn(next_states)  # Get Q-values from target network
  max_next_qs = tf.reduce_max(next_qs, axis=-1)  # Get maximum Q-value for next state
  target = rewards + (1. - dones) * discount * max_next_qs  # Bellman target

  with tf.GradientTape() as tape:
    qs = main_nn(states)  # Q-values from the main network
    action_masks = tf.one_hot(actions, num_actions)  # One-hot encode actions
    masked_qs = tf.reduce_sum(action_masks * qs, axis=-1)  # Masked Q-values
    loss = mse(target, masked_qs)  # Compute loss
    
  grads = tape.gradient(loss, main_nn.trainable_variables)  # Compute gradients
  optimizer.apply_gradients(zip(grads, main_nn.trainable_variables))  # Update weights
  return loss  # Return the loss value

# Hyperparameters and training setup
espi = []
num_episodes = 5000
epsilon = 1.0
epsilon_decay_1 = 0.0003984  # Epsilon decay rate
batch_size = 64
discount = 0.87  # Discount factor
buffer = ReplayBuffer(100000)  # Replay buffer size
cur_frame = 0
min_reward = 0  # Minimum reward to save the model

# Training loop
last_100_ep_rewards = []  # Store rewards from the last 100 episodes
loss_value = []
loss_value_1 = []
rew = []
ep_reward = 0

# Loop through episodes
for episode in range(num_episodes+1):
  state = env.reset()  # Reset environment at the start of each episode
  ep_reward, done = 0, False
  loss = 0
  while not done:
    state_in = tf.expand_dims(state, axis=0)  # Expand dimensions for batch processing
    action = select_epsilon_greedy_action(state_in, epsilon)  # Select action using epsilon-greedy policy
    next_state, reward, done, _ = env.step(action)  # Take action and observe the result
    ep_reward += reward  # Accumulate episode reward

    # Add experience to the replay buffer
    buffer.add(state, action, reward, next_state, done)
    state = next_state  # Move to the next state
    cur_frame += 1

    # Copy weights from the main network to the target network periodically
    if cur_frame % 8000 == 0:
      target_nn.set_weights(main_nn.get_weights())

    # Train the neural network if the buffer has enough samples
    if len(buffer) >= batch_size:
      states, actions, rewards, next_states, dones = buffer.sample(batch_size)
      loss = train_step(states, actions, rewards, next_states, dones)
      loss_value_1.append(loss)

  # Decay epsilon over time
  epsilon -= epsilon_decay_1  # Reduce epsilon to encourage exploitation

  # Track the last 100 episode rewards
  if len(last_100_ep_rewards) == 100:
    last_100_ep_rewards = last_100_ep_rewards[1:]
  last_100_ep_rewards.append(ep_reward)

  # Save model weights if the reward improves
  if (np.mean(last_100_ep_rewards) > min_reward) and epsilon < 0.2:
    main_nn.save_weights("DQN_TF_MODEL_paper_weights.h5")
    min_reward = np.mean(last_100_ep_rewards)
    print("Weights Saved")

  # Log progress every 50 episodes
  if episode % 50 == 0:
    print(f'Episode {episode}/{num_episodes}. Epsilon: {epsilon:.3f}. '
          f'Reward in last 100 episodes: {np.mean(last_100_ep_rewards):.3f}')
    loss_value.append(loss)
    rew.append(np.mean(last_100_ep_rewards))
    espi.append(epsilon)

# Plot the loss and reward progress
plt.plot(loss_value)
plt.show()

plt.plot(loss_value_1)
plt.show()

plt.plot(rew)
plt.show()

# Save progress and model weights
np.save("DQN_LOSS_VALUE_paper_weights_average.npy", loss_value, allow_pickle=True)
np.save("DQN_Reward_paper_weights.npy", rew, allow_pickle=True)
np.save("DQN_LOSS_VALUE_paper_weights_all.npy", loss_value_1, allow_pickle=True) 
np.save("DQN_epsilon_paper_weights.npy", espi, allow_pickle=True)

main_nn.save_weights("END_dqn_Rew_Duling_TF_MODEL_paper_weights.h5")

end = time.time()
print(end-start)  # Print the total training time
