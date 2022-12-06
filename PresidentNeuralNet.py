import torch
import numpy as np
import torch.nn as nn
import torch.nn.functional as F
# Define neural network model
class PresidentNet(nn.Module):
    def __init__(self):
        super(PresidentNet, self).__init__()
        self.dropout = nn.Dropout(0.5)
        self.layer1 = nn.Sequential(
            nn.Linear(168,504),
            nn.ELU()
        )
        self.layer2 = nn.Sequential(
            #nn.Dropout(0.5),
            nn.Linear(504, 504), 
            nn.ELU()
        )
        self.layer3 = nn.Sequential(
            #nn.Dropout(0.5),
            nn.Linear(504,256),
            nn.ELU()
        )
        self.layer4 = nn.Sequential(
            #nn.Dropout(0.5),
            nn.Linear(256, 128),
            nn.Tanh()
            
        )
        self.layer5 = nn.Sequential(
            nn.Linear(128,55)
        )
       

    def forward(self, x):
        x = self.layer1(x)
        x = self.dropout(x)
        x = self.layer2(x)
        x = self.dropout(x)
        x = self.layer3(x)
        x = self.dropout(x)
        x = self.layer4(x)
        x = self.dropout(x)
        x = self.layer5(x)
        output = F.log_softmax(x, dim=0)
        return output

device = "cpu"
model = PresidentNet().to(device)  # use GPU