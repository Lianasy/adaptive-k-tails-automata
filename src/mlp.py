import torch
import torch.nn as nn
import torch.nn.functional as F

class KModel(nn.Module):

    def __init__(self, input_size, num_symbols, num_classes):
        super().__init__()

        self.fc1 = nn.Linear(input_size, 64)
        self.fc2 = nn.Linear(64, 32)

        # size of output = num_symbols * num_classes
        self.out = nn.Linear(32, num_symbols * num_classes)

        self.num_symbols = num_symbols
        self.num_classes = num_classes

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.out(x)
        x = x.view(-1, self.num_symbols, self.num_classes)
        return x

def get_features(train_samples, train_labels, val_samples, val_labels, test_sample):
    pass

def train_model(model, X_train, y_train, X_val, y_val, epochs=100, lr=0.001):

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(epochs):

        # Train
        model.train()

        optimizer.zero_grad()

        pred = model(X_train)

        train_loss = 0

        for i in range(y_train.shape[1]):
            train_loss += criterion(pred[:, i, :], y_train[:, i])

        train_loss.backward()
        optimizer.step()

        # Val
        model.eval()

        with torch.no_grad():

            pred_val = model(X_val)

            val_loss = 0

            for i in range(y_val.shape[1]):
                val_loss += criterion(pred_val[:, i, :], y_val[:, i])

            # accuracy
            k_pred = torch.argmax(pred_val, dim=2)

            correct = (k_pred == y_val).float().mean()

        # Print logs
        if epoch % 10 == 0:
            print(
                f"Epoch {epoch} | "
                f"Train Loss: {train_loss.item():.4f} | "
                f"Val Loss: {val_loss.item():.4f} | "
                f"Val Acc: {correct.item():.4f}"
            )

    return model

def runMLP(train_samples, train_labels, val_samples, val_labels, test_sample, num_k_classes=4, epochs=100, lr=0.001):
    X_train, y_train, X_val, y_val, test_features = get_features(train_samples, train_labels, val_samples, val_labels, test_sample)
    X_train = torch.tensor(X_train, dtype=torch.float32)
    y_train = torch.tensor(y_train, dtype=torch.long) - 1

    X_val = torch.tensor(X_val, dtype=torch.float32)
    y_val = torch.tensor(y_val, dtype=torch.long) - 1

    input_size = X_train.shape[1]
    num_symbols = y_train.shape[1]

    model = KModel(input_size, num_symbols, num_k_classes)
    model = train_model(
        model,
        X_train, y_train,
        X_val, y_val,
        epochs=epochs,
        lr=lr
    )
    model.eval()

    with torch.no_grad():
        pred = model(test_features)
    k_vector = torch.argmax(pred, dim=2) + 1
    k_vector = k_vector.squeeze().tolist()
    return k_vector

num_k_classes = 4
epochs = 100
train_samples = None
train_labels = None
val_samples = None
val_labels = None
test_sample = None

k_vector = runMLP(train_samples, train_labels, val_samples, val_labels, test_sample, num_k_classes=4, epochs=100, lr=0.001)