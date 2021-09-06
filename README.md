# mistconnection

Basic Mist connection library for Python.

See [mist-cloud-comm](https://github.com/thinnect/mist-cloud-comm)
for information on the messaging logic used for the connection library.

## Using the package

See [example.py](src/mistconnection/example.py) for a basic example of
connecting, receiving and sending a message.

## Build the package

Make sure you have an up-to-date PyPA build:
`python3 -m pip install --upgrade build`

Build the package:
`python3 -m build`

Install the package:
`python3 -m pip install dist/mistconnection-X.Y.Z-py3-none-any.whl`
