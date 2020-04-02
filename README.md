# covid-19-dashboard

1 - Clone Repo:
```
git clone https://github.com/sdc50/covid-19-dashboard.git
cd covid-19-dashboard
```

2 - Create Conda Environment:

```
conda env create -f environment.yml
conda activate covid-19
jupyter labextension install @pyviz/jupyterlab_pyviz
```

3 - Get Data:

```
git clone https://github.com/CSSEGISandData/COVID-19.git
```
Note the `COVID-19` directory should be in the `covid-19-dashboard` directory (i.e. parallel to the `notebooks` directory)

4 - Run Jupyter and Launch Dashboard from `Dashboard.ipynb`

```
jupyter lab
```

