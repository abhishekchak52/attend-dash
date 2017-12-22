# attend-dash

An dashboard for attendance data visualization for students of St. Stephen's College. 


We recommend [pipenv][ref1] for package management. 

**Only** python 3 is supported. 

## Usage

### Installing Dependencies

Have python 3 installed with jupyter notebook installed in your root environment.
From the command line, run `pipenv install --dev`.

### Installing the jupyter kernel 

The project uses a kernel which can be run without activating the environment. Open the command line and `cd` into this repo. Run `python -m ipykernel install --user --name attend-dash --display-name "Python3 (attend-dash)"`
The kernel should now be accesible from your root jupyter notebook. 


## TODO

1. Scrape, clean and generate plots for data in a jupyter notebook.
2. Implement the same functionality in scripts and finalize storage format for data.
3. Create a dashboard using a web framework (maybe [Dash][ref2]?)
4. Add to the compsoc [website][ref3].





[ref1]: http://pipenv.readthedocs.io/en/latest/
[ref2]: https://plot.ly/products/dash/
[ref3]: http://compsocssc.pythonanywhere.com/	