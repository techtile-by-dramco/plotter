# Techtile plotter

## Interface

```python
from TechtilePlotter.TechtilePlotter import TechtilePlotter

plt = TechtilePlotter()
plt.antennas()
plt.microphones()
plt.measurements(positions, values)
plt.show()
```


## Installing package

Prior to imnstalling ensure you have the lastest pip version, e.g., `python3 -m pip install --upgrade pip`.

```sh
git clone https://github.com/techtile-by-dramco/plotter.git
cd plotter
pip install --editable .
```

## Update package

```sh
cd plotter
git pull
pip install --upgrade pip
pip install --editable .
```

## Running example
```sh
cd plotter # if not already in this folder
cd examples
python .\example1.py
```
