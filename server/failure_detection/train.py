import torch
import torch.nn as nn
import pandas as pd
from tqdm import tqdm
from dataset import HddSmartDataset
from torch.utils.data import DataLoader
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print(device)


class Classifier(nn.Module):

    def __init__(self, use_bce = True, lr = 0.01):
        super().__init__()

        self.use_bce = use_bce
        self.lr = lr
        self.model = nn.Sequential(
            nn.Linear(162, 200),
            nn.LeakyReLU(0.02),
            nn.Linear(200,2),
            nn.Sigmoid(),
        )
        self.loss_funciton = nn.CrossEntropyLoss()
        #self.loss_funciton = nn.MSELoss()

        #self.optimiser = torch.optim.SGD(self.parameters(), lr = self.lr)
        self.optimiser = torch.optim.Adam(self.parameters())

        self.counter = 0
        self.progress = []

    def forward(self, inputs):
        return self.model(inputs)

    
    def train(self, inputs, targets):

        outputs = self.forward(inputs)
        
        if self.use_bce:
            loss = self.loss_funciton(outputs, targets)
        else:
            loss = self.loss_funciton(outputs, targets)


        self.optimiser.zero_grad()
        loss.backward()
        self.optimiser.step()

        self.counter += 1
        if self.counter % 10 == 0:
            self.progress.append(loss.item())
            pass

        if self.counter % 10000 == 0:
            print(f"counter = {self.counter}")
            pass

    def plot_progress(self):

        df = pd.DataFrame(self.progress, columns=['loss'])
        #df.plot(ylim=(0,1.0), figsize=(16,8), alpha=0.1, marker='.', grid=True, yticks=(0,0.25,0.5))
        df.plot(ylim=(0,1.0), alpha=0.1, marker='.', grid=True, yticks=(0,0.25,0.5))

def train():
    dataset = HddSmartDataset()
    C = Classifier(use_bce=False, lr = 0.1).to(device)
    loader = DataLoader(dataset=dataset, batch_size=64, shuffle=True)
    n_epochs = 3
    for epoch in range(n_epochs):
        print(f"epoch {epoch}")
        for label, image_tensor, target_tensor in tqdm(loader):
            C.train(image_tensor.to(device), targets=target_tensor.to(device))
    C.plot_progress()

if __name__ == "__main__":
    train()