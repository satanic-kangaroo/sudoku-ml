"""
آموزش مدل CNN روی دیتاست سودوکوی رندر‌شده
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, callbacks
import matplotlib.pyplot as plt


def load_dataset(data_dir="data"):
    X_train = np.load(f"{data_dir}/X_train.npy")
    y_train = np.load(f"{data_dir}/y_train.npy")
    X_test = np.load(f"{data_dir}/X_test.npy")
    y_test = np.load(f"{data_dir}/y_test.npy")

    X_train = X_train.astype("float32") / 255.0
    X_test = X_test.astype("float32") / 255.0

    X_train = X_train[..., None]
    X_test = X_test[..., None]

    return (X_train, y_train), (X_test, y_test)


def build_model():
    model = models.Sequential([
        layers.Input(shape=(28, 28, 1)),

        # Block 1
        layers.Conv2D(32, 3, padding="same", activation="relu"),
        layers.BatchNormalization(),
        layers.Conv2D(32, 3, padding="same", activation="relu"),
        layers.BatchNormalization(),
        layers.MaxPooling2D(),
        layers.Dropout(0.25),

        # Block 2
        layers.Conv2D(64, 3, padding="same", activation="relu"),
        layers.BatchNormalization(),
        layers.Conv2D(64, 3, padding="same", activation="relu"),
        layers.BatchNormalization(),
        layers.MaxPooling2D(),
        layers.Dropout(0.25),

        # Block 3
        layers.Conv2D(128, 3, padding="same", activation="relu"),
        layers.BatchNormalization(),
        layers.Dropout(0.25),

        # Head
        layers.Flatten(),
        layers.Dense(128, activation="relu"),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(9, activation="softmax"),
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model


def plot_history(history):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].plot(history.history["loss"], label="train")
    axes[0].plot(history.history["val_loss"], label="val")
    axes[0].set_title("Loss")
    axes[0].legend()

    axes[1].plot(history.history["accuracy"], label="train")
    axes[1].plot(history.history["val_accuracy"], label="val")
    axes[1].set_title("Accuracy")
    axes[1].legend()

    plt.tight_layout()
    plt.savefig("training_curves.png", dpi=100)
    plt.show()


def main():
    print("📂 لود دیتاست...")
    (X_train, y_train), (X_test, y_test) = load_dataset()
    print(f"   Train: {X_train.shape}, Test: {X_test.shape}")

    model = build_model()
    model.summary()

    cb = [
        callbacks.ModelCheckpoint(
            "digit_model.keras",
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1
        ),
        callbacks.EarlyStopping(
            monitor="val_accuracy",
            patience=5,
            restore_best_weights=True,
            verbose=1
        ),
        callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=3,
            min_lr=1e-6,
            verbose=1
        ),
    ]

    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=30,
        batch_size=128,
        callbacks=cb,
        verbose=1
    )

    test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"\n🎯 دقت نهایی روی تست: {test_acc*100:.2f}%")

    plot_history(history)


if __name__ == "__main__":
    main()