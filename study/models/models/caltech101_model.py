import keras
from functools import partial

from ..layers import ResidualConvBlock, MinMaxNormalization, get_augmentation_layer

from util.trial_detail import TrialDetail


DefaultConv2D = partial(
    keras.layers.Conv2D,
    kernel_size=3,
    strides=1,
    padding="same",
    kernel_initializer="he_normal",
    use_bias=False,
)


def get_caltech101_model(trial_detail: TrialDetail):
    """
    Geron, A. (2019). Hands-on machine learning with Scikit-Learn,
    Keras and TensorFlow: concepts, tools, and techniques to build
    intelligent systems (2nd ed.). O’Reilly.
    """
    num_classes = 102
    augmentation_layer = get_augmentation_layer(
        augmentation_method=trial_detail.augmentation_method,
        energy_factor=trial_detail.energy_factor,
    )

    inputs = keras.Input(shape=(180, 180, 3))
    x = augmentation_layer(inputs)
    x = MinMaxNormalization()(x)
    x = keras.layers.Conv2D(64, kernel_size=7, strides=2, padding="valid")(x)
    x = keras.layers.BatchNormalization()(x)
    x = keras.layers.Activation("relu")(x)
    x = keras.layers.MaxPooling2D(pool_size=3, strides=2, padding="same")(x)

    prev_filters = 64
    for filters in [64] * 3 + [128] * 4 + [256] * 6 + [512] * 3:
        strides = 1 if filters == prev_filters else 2
        x = ResidualConvBlock(filters, strides=strides)(x)
        prev_filters = filters

    x = keras.layers.GlobalAveragePooling2D()(x)
    x = keras.layers.Flatten()(x)
    x = keras.layers.Dropout(0.5)(x)
    outputs = keras.layers.Dense(num_classes, activation="softmax")(x)

    model = keras.Model(inputs=inputs, outputs=outputs)

    optimizer = keras.optimizers.RMSprop(momentum=0.9)
    model.compile(
        loss="sparse_categorical_crossentropy",
        optimizer=optimizer,
        metrics=["accuracy"],
    )

    return model
