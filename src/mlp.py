import torch
import torch.nn as nn
from src.feature_extraction import build_dataset_with_labels
from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.preprocessing import StandardScaler

class KModel(nn.Module):

    def __init__(self, input_size, num_symbols, num_classes):
        super().__init__()

        self.net = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.3),

            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.3),

            nn.Linear(64, 32),
            nn.ReLU(),

            nn.Linear(32, num_symbols * num_classes)
        )

        self.num_symbols = num_symbols
        self.num_classes = num_classes

    def forward(self, x):
        x = self.net(x)
        x = x.view(-1, self.num_symbols, self.num_classes)
        return x



def get_features(folder):

    # load data
    X_df, y_df, alphabet = build_dataset_with_labels(folder)

    # split test
    X_test = X_df.iloc[:10]
    y_test = y_df.iloc[:10]
    X_temp = X_df.iloc[10:]
    y_temp = y_df.iloc[10:]

    # split train / val
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp,
        test_size=0.2,
        random_state=42
    )

    # convert to numpy
    X_train = X_train.values
    y_train = y_train.values

    X_val = X_val.values
    y_val = y_val.values

    X_test = X_test.values
    y_test = y_test.values

    # normalization
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_val = scaler.transform(X_val)
    X_test = scaler.transform(X_test)

    return X_train, y_train, X_val, y_val, X_test, y_test, alphabet

def train_single_model(model, X_train, y_train_col, X_val, y_val_col, epochs=200, lr=0.0005):

    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(epochs):

        model.train()
        optimizer.zero_grad()

        pred = model(X_train)[:, 0, :]
        train_loss = criterion(pred, y_train_col)

        train_loss.backward()
        optimizer.step()

        model.eval()
        with torch.no_grad():
            pred_val = model(X_val)[:, 0, :]
            val_loss = criterion(pred_val, y_val_col)

            k_pred = torch.argmax(pred_val, dim=1)
            hamming = (k_pred == y_val_col).float().mean()
            exact = (k_pred == y_val_col).float().mean()

        if epoch % 20 == 0:
            print(
                f"Epoch {epoch} | "
                f"Train Loss: {train_loss.item():.4f} | "
                f"Val Loss: {val_loss.item():.4f} | "
                f"Hamm: {hamming.item():.4f} | "
                f"Exact: {exact.item():.4f}"
            )

    return model

def runMLP(folder, num_k_classes=4, epochs=200, lr=0.0005):

    X_train, y_train, X_val, y_val, X_test, y_test, alphabet = get_features(folder)

    y_test_np = y_test.copy()

    X_train = torch.tensor(X_train, dtype=torch.float32)
    y_train = torch.tensor(y_train, dtype=torch.long) - 1

    X_val = torch.tensor(X_val, dtype=torch.float32)
    y_val = torch.tensor(y_val, dtype=torch.long) - 1

    X_test = torch.tensor(X_test, dtype=torch.float32)
    y_test_torch = torch.tensor(y_test, dtype=torch.long) - 1

    input_size = X_train.shape[1]
    num_symbols = y_train.shape[1]

    models = []

    for sym_idx in range(num_symbols):
        model = KModel(input_size, 1, num_k_classes)

        model = train_single_model(
            model,
            X_train,
            y_train[:, sym_idx],
            X_val,
            y_val[:, sym_idx],
            epochs=epochs,
            lr=lr
        )

        models.append(model)

    preds_raw = []

    for model in models:
        model.eval()
        with torch.no_grad():
            pred = model(X_test)[:, 0, :]
            k = torch.argmax(pred, dim=1)
            preds_raw.append(k)

    k_pred = torch.stack(preds_raw, dim=1)

    hamming = (k_pred == y_test_torch).float().mean()
    exact = (k_pred == y_test_torch).all(dim=1).float().mean()
    distance = torch.abs(k_pred - y_test_torch).float().mean()

    print("\ntest hamming:", hamming.item())
    print("test exact:", exact.item())
    print("distance:", distance.item())

    k_pred_np = (k_pred + 1).cpu().numpy()

    print("\ntrue vs predicted:\n")
    for i in range(min(10, len(k_pred_np))):
        print(f"sample {i}:")
        print("true:", y_test_np[i])
        print("pred:", k_pred_np[i])
        print("---")

    return k_pred_np
num_k_classes = 4
epochs = 100
folder = "../output/10_state/10_state"

k_vectors = runMLP(
    folder,
    num_k_classes=4,
    epochs=100,
    lr=0.001
)

print("Predicted k-vector:", k_vectors)

df = pd.DataFrame(k_vectors)
df.to_csv("../data/k_vectors.csv", index=False, header=False)