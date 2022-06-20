"""Backend supported: tensorflow.compat.v1, tensorflow, pytorch"""
import deepxde as dde
import numpy as np

# General parameters
n = 2
precision_train = 10
precision_test = 10
hard_constraint = True
weights = 100  # if hard_constraint == False
epochs = 5000
parameters = [1e-3, 3, 150, "sin"]

# Define sine function
if dde.backend.backend_name == "pytorch":
    cos = dde.backend.pytorch.cos
else:
    from deepxde.backend import tf

    cos = tf.cos

learning_rate, num_dense_layers, num_dense_nodes, activation = parameters


def pde(x, y):
    dy_xx = dde.grad.hessian(y, x, i=0, j=0)
    dy_yy = dde.grad.hessian(y, x, i=1, j=1)

    f = k0**2 * cos(k0 * x[:, 0:1]) * cos(k0 * x[:, 1:2])
    return -dy_xx - dy_yy - k0**2 * y - f


# WORK / TODO /WORKING ON TRAVIS WHY
def func(x):
    return np.cos(k0 * x[:, 0:1]) * np.cos(k0 * x[:, 1:2])


def boundary(_, on_boundary):
    return on_boundary


geom = dde.geometry.Rectangle([0, 0], [1, 1])
k0 = 2 * np.pi * n
wave_len = 1 / n

hx_train = wave_len / precision_train
nx_train = int(1 / hx_train)

hx_test = wave_len / precision_test
nx_test = int(1 / hx_test)

bc = dde.icbc.NeumannBC(geom, lambda x: 0, boundary)


data = dde.data.PDE(
    geom,
    pde,
    bc,
    num_domain=nx_train**2,
    num_boundary=4 * nx_train,
    solution=func,
    num_test=nx_test**2,
)

net = dde.nn.FNN(
    [2] + [num_dense_nodes] * num_dense_layers + [1], activation, "Glorot uniform"
)

model = dde.Model(data, net)
loss_weights = [1, weights]
model.compile(
    "adam",
    lr=learning_rate,
    metrics=["l2 relative error"],
    loss_weights=loss_weights,
)


losshistory, train_state = model.train(epochs=epochs)
dde.saveplot(losshistory, train_state, issave=True, isplot=True)
