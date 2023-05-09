import torch
import numpy as np
import torch.nn as nn
import torch.nn.functional as F

# Define neural network model
class PresidentNet(nn.Module):
    def __init__(self):
        super(PresidentNet, self).__init__()
        self.dropout0 = nn.Dropout(0.05)
        self.dropout1 = nn.Dropout(0.2)
        self.dropout2 = nn.Dropout(0.5)
        self.dropout3 = nn.Dropout(0.5)
        self.dropout4 = nn.Dropout(0.5)

        self.layer1 = nn.Sequential(
            nn.Linear(207,1024),
            nn.ReLU()
        )
        self.layer2 = nn.Sequential(
            nn.Linear(1024, 1024), 
            nn.ReLU()
        )
        self.layer3 = nn.Sequential(
            nn.Linear(1024,512),
            nn.ReLU()
        )
        self.layer4 = nn.Sequential(
            nn.Linear(512, 256),
            nn.ReLU()
        )
        self.layer5 = nn.Sequential(
            nn.Linear(256,55),
        )
       

    def forward(self, x):
        x = self.dropout0(x)
        x = self.layer1(x)
        x = self.dropout1(x)
        x = self.layer2(x)
        x = self.dropout2(x)
        x = self.layer3(x)
        x = self.dropout3(x)
        x = self.layer4(x)
        x = self.dropout4(x)
        x = self.layer5(x)
        output = F.relu6(x) + 1
        return output
