import os
import torch
from torch import nn
from torch.utils.data import DataLoader
from torch.utils.data import TensorDataset
import random
import glob
import pandas as pd
import numpy as np
#%%
# data loader
train = pd.read_csv('train_binary.csv')
train = train.drop(train.columns[0], axis = 1)

class2idx = {
    'Rarely': 0,
    'Possibly': 1,
    'Probably': 2,
    'Very likely': 3
}
class2idx_2 = {
    False: 0,
    True : 1
}

train['ban_binary'].replace(class2idx_2, inplace = True)

train = train.to_numpy()
np.random.shuffle(train)
train_set = train[:int(0.7* len(train))]
test_set = train[int(len(train_set)):]

train_label = train_set[:, -1:]
train_set = train_set[:,0:-1]
train_set = torch.tensor(train_set, dtype = torch.float)
train_label = torch.tensor(train_label, dtype= torch.float)
# train_label = torch.flatten(train_label)
train_data = TensorDataset(train_set, train_label)

train_loader = DataLoader(train_data, batch_size= 50)

test_label = test_set[:,-1:]
test_set = test_set[:,0:-1]
test_set = torch.tensor(test_set, dtype= torch.float)
test_label = torch.tensor(test_label, dtype=torch.float)
# test_label = torch.flatten(test_label)
test_data = TensorDataset(test_set, test_label)
test_loader = DataLoader(test_data, batch_size=50)

#%%
class model(nn.Module):
    def __init__(self, num_feature=45, num_label=2):
        super(model, self).__init__()
        self.layer1 = nn.Linear(num_feature, 128)
        self.layer2 = nn.Linear(128, 64)
        self.layer3 = nn.Linear(64, 32)
        self.layer4 = nn.Linear(32, 1)

    def forward(self, x):
        x = torch.relu(self.layer1(x))
        x = torch.relu(self.layer2(x))
        x = torch.relu(self.layer3(x))
        x = torch.sigmoid(self.layer4(x))
        return x


#%%
def train_():
    net = model()
    criterion = nn.BCELoss()
    optimizer = torch.optim.Adagrad(net.parameters(), lr = 0.0008)
    epoch = 5000
    for iter in range(epoch):
        running_loss = 0
        for data, label in train_loader:
            optimizer.zero_grad()
            pred_y = net(data)
            loss = criterion(pred_y, label)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        print("Iteration {:5d} | loss: {:6.8f}".format(iter, running_loss))
        total = 0
        correct = 0
        with torch.no_grad():
            for data, label in test_loader:
                pred_y = net(data)
                # _, pred_y = torch.max(pred_y, 1)
                pred_y = np.round(pred_y)
                if iter %10 == 0:
                    print(pred_y)
                    print(label)

                correct += (label == pred_y).sum().item()
                total += data.shape[0]
            print('Accuracy: %d %%' % (100.0 * correct / total))


#%%
train_()

#%%
