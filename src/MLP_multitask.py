import copy
import torch
import torch.nn as nn
from src.feature_extraction import build_dataset_with_labels
from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.preprocessing import StandardScaler


class MultiTaskKModel(nn.Module):
    """
    Multi-task MLP for k-vector prediction.

    Input:
        x: [batch_size, input_size]
    Output:
        logits: [batch_size, num_symbols, num_classes]

    Meaning:
        logits[:, i, :] predicts the k class for the i-th alphabet symbol.
    """

    def __init__(self, input_size, num_symbols, num_classes):
        super().__init__()

        # Shared representation learner: learns global PTA structural features once.
        self.shared = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.3),

            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.1),

            nn.Linear(64, 32),
            nn.ReLU(),
        )

        # Symbol-specific heads: one classifier for each component of the k-vector.
        self.heads = nn.ModuleList([
            nn.Linear(32, num_classes)
            for _ in range(num_symbols)
        ])

        self.num_symbols = num_symbols
        self.num_classes = num_classes

    def forward(self, x):
        h = self.shared(x)  # [batch_size, 32]

        outputs = []
        for head in self.heads:
            outputs.append(head(h))  # each: [batch_size, num_classes]

        return torch.stack(outputs, dim=1)  # [batch_size, num_symbols, num_classes]


def get_features(folder):
    # load data
    X_df, y_df, alphabet = build_dataset_with_labels(folder)

    # split test: keep the first 10 samples as test set, same as the original code
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


def evaluate_k_vector_prediction(k_pred, y_true):
    """
    k_pred: [batch_size, num_symbols], zero-based class indices
    y_true: [batch_size, num_symbols], zero-based class indices
    """
    hamming = (k_pred == y_true).float().mean()
    exact = (k_pred == y_true).all(dim=1).float().mean()
    distance = torch.abs(k_pred - y_true).float().mean()
    return hamming, exact, distance


'''def train_multitask_model(model, X_train, y_train, X_val, y_val, epochs=200, lr=0.0005):
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss()

    num_classes = model.num_classes

    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()

        pred = model(X_train)  # [B, S, C]

        # CrossEntropyLoss expects:
        # input:  [N, C]
        # target: [N]
        # Therefore we flatten [B, S, C] into [B*S, C]
        # and [B, S] into [B*S].
        train_loss = criterion(
            pred.reshape(-1, num_classes),
            y_train.reshape(-1)
        )

        train_loss.backward()
        optimizer.step()

        model.eval()
        with torch.no_grad():
            pred_val = model(X_val)  # [B, S, C]
            val_loss = criterion(
                pred_val.reshape(-1, num_classes),
                y_val.reshape(-1)
            )

            k_pred_val = torch.argmax(pred_val, dim=2)  # [B, S]
            hamming, exact, distance = evaluate_k_vector_prediction(k_pred_val, y_val)

        if epoch % 20 == 0:
            print(
                f"Epoch {epoch} | "
                f"Train Loss: {train_loss.item():.4f} | "
                f"Val Loss: {val_loss.item():.4f} | "
                f"Hamming: {hamming.item():.4f} | "
                f"Exact: {exact.item():.4f} | "
                f"Distance: {distance.item():.4f}"
            )

    return model'''
def train_multitask_model(model, X_train, y_train, X_val, y_val, epochs=300, lr=0.0005):
    import copy

    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss()

    num_classes = model.num_classes

    best_state = None
    best_exact = -1.0
    best_hamming = -1.0
    best_distance = float("inf")
    best_epoch = 0

    patience = 40
    wait = 0

    for epoch in range(epochs):
        # ---------- train ----------
        model.train()
        optimizer.zero_grad()

        pred = model(X_train)  # [B, S, C]

        train_loss = criterion(
            pred.reshape(-1, num_classes),
            y_train.reshape(-1)
        )

        train_loss.backward()
        optimizer.step()

        # ---------- validation ----------
        model.eval()
        with torch.no_grad():
            pred_val = model(X_val)

            val_loss = criterion(
                pred_val.reshape(-1, num_classes),
                y_val.reshape(-1)
            )

            k_pred_val = torch.argmax(pred_val, dim=2)
            hamming, exact, distance = evaluate_k_vector_prediction(k_pred_val, y_val)

        hamming_value = hamming.item()
        exact_value = exact.item()
        distance_value = distance.item()

        # ---------- choose best model ----------
        # 优先 exact，其次 hamming，最后 distance
        improved = False

        if exact_value > best_exact:
            improved = True
        elif exact_value == best_exact and hamming_value > best_hamming:
            improved = True
        elif exact_value == best_exact and hamming_value == best_hamming and distance_value < best_distance:
            improved = True

        if improved:
            best_exact = exact_value
            best_hamming = hamming_value
            best_distance = distance_value
            best_epoch = epoch
            best_state = copy.deepcopy(model.state_dict())
            wait = 0
        else:
            wait += 1

        if epoch % 20 == 0:
            print(
                f"Epoch {epoch} | "
                f"Train Loss: {train_loss.item():.4f} | "
                f"Val Loss: {val_loss.item():.4f} | "
                f"Hamming: {hamming_value:.4f} | "
                f"Exact: {exact_value:.4f} | "
                f"Distance: {distance_value:.4f}"
            )

        if wait >= patience:
            print(f"Early stopping at epoch {epoch}")
            break

    if best_state is not None:
        model.load_state_dict(best_state)

    print(
        f"Best model from epoch {best_epoch} | "
        f"Val Exact: {best_exact:.4f} | "
        f"Val Hamming: {best_hamming:.4f} | "
        f"Val Distance: {best_distance:.4f}"
    )

    return model


def runMultiTaskMLP(folder, num_k_classes=4, epochs=200, lr=0.0005):
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

    print("Input feature size:", input_size)
    print("Number of symbols:", num_symbols)
    print("Alphabet:", alphabet)

    model = MultiTaskKModel(
        input_size=input_size,
        num_symbols=num_symbols,
        num_classes=num_k_classes
    )

    model = train_multitask_model(
        model,
        X_train,
        y_train,
        X_val,
        y_val,
        epochs=epochs,
        lr=lr
    )

    model.eval()
    with torch.no_grad():
        pred_test = model(X_test)  # [B, S, C]
        k_pred = torch.argmax(pred_test, dim=2)  # [B, S]

    hamming, exact, distance = evaluate_k_vector_prediction(k_pred, y_test_torch)

    print("\ntest hamming:", hamming.item())
    print("test exact:", exact.item())
    print("distance:", distance.item())

    # Convert from zero-based class index back to real k values: 0..3 -> 1..4
    k_pred_np = (k_pred + 1).cpu().numpy()

    print("\ntrue vs predicted:\n")
    for i in range(min(10, len(k_pred_np))):
        print(f"sample {i}:")
        print("true:", y_test_np[i])
        print("pred:", k_pred_np[i])
        print("---")

    return k_pred_np


if __name__ == "__main__":
    num_k_classes = 2
    epochs = 300
    folder = "C:/Users/11603/Desktop/adaptive-k-tails-automata-main/output/10_state/10_state"
    k_vectors = runMultiTaskMLP(
        folder,
        num_k_classes=num_k_classes,
        epochs=epochs,
        lr=0.0005
    )

    print("Predicted k-vector:", k_vectors)

    df = pd.DataFrame(k_vectors)
    df.to_csv("output/k_vectors_multitask.csv", index=False, header=False)
