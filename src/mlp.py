import torch
import torch.nn as nn
from src.feature_extraction import build_dataset_with_labels
from sklearn.model_selection import train_test_split

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

def get_features(folder):

    # LOAD DATA
    X_df, y_df, alphabet = build_dataset_with_labels(folder)

    #  SPLIT: 1 test sample
    X_temp, X_test, y_temp, y_test = train_test_split(
        X_df, y_df,
        test_size=1,
        random_state=42
    )

    # SPLIT: train / val
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp,
        test_size=0.2,
        random_state=42
    )

    #  TO NUMPY
    X_train = X_train.values
    y_train = y_train.values

    X_val = X_val.values
    y_val = y_val.values

    X_test = X_test.values
    y_test = y_test.values

    return X_train, y_train, X_val, y_val, X_test, y_test, alphabet

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

def runMLP(folder, num_k_classes=4, epochs=100, lr=0.001):

    #  GET FEATURES
    X_train, y_train, X_val, y_val, X_test, y_test, alphabet = get_features(folder)

    # TO TORCH
    X_train = torch.tensor(X_train, dtype=torch.float32)
    y_train = torch.tensor(y_train, dtype=torch.long) - 1

    X_val = torch.tensor(X_val, dtype=torch.float32)
    y_val = torch.tensor(y_val, dtype=torch.long) - 1

    X_test = torch.tensor(X_test, dtype=torch.float32)

    # MODEL
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

    # PREDICT ONE TEST SAMPLE
    model.eval()

    with torch.no_grad():
        pred = model(X_test[0].unsqueeze(0))

    k_vector = torch.argmax(pred, dim=2) + 1
    k_vector = k_vector.squeeze().tolist()

    return k_vector

num_k_classes = 4
epochs = 100
folder = "../output/10_state/10_state"

k_vector = runMLP(
    folder,
    num_k_classes=4,
    epochs=100,
    lr=0.001
)

print("Predicted k-vector:", k_vector)