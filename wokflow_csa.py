import parsl
from parsl import python_app , bash_app

from parsl.config import Config

# PBSPro is the right provider for Polaris:
from parsl.providers import PBSProProvider
# The high throughput executor is for scaling to HPC systems:
from parsl.executors import HighThroughputExecutor
# You can use the MPI launcher, but may want the Gnu Parallel launcher, see below
from parsl.launchers import MpiExecLauncher # USE the MPIExecLauncher
# address_by_interface is needed for the HighThroughputExecutor:
from parsl.addresses import address_by_interface
# For checkpointing:
from parsl.utils import get_all_checkpoints

from parsl.providers import LocalProvider
from parsl.channels import LocalChannel
from parsl.executors import HighThroughputExecutor


from IMPROVE.Workflows import workflow_csa
from IMPROVE.CLI import CLI

from IMPROVE.Config.Parsl import Config as Parsl
import IMPROVE.Config.CSA as CSA
from IMPROVE.Config.Common import Config as Common_config

import os
from pathlib import Path
import logging
import sys



# Import the module from the file, e.g. import_module("path/to/file.py")
# This function is needed to import for example a custom Parsl Config from the file
def import_module(filepath):

     # get the parent directory of the package
     pkg_parent = os.path.dirname(filepath)
     # get the package name removing the .py extension
     pkg = os.path.basename(filepath).replace(".py", "")

     spec = importlib.machinery.PathFinder().find_spec(pkg, [pkg_parent])
     print(spec, pkg, pkg_parent)
     mod = importlib.util.module_from_spec(spec)
     sys.modules[pkg] = mod  # needed for exec_module to work
     spec.loader.exec_module(mod)
     sys.modules[pkg] = importlib.import_module(pkg)
     return mod


# Adjust your user-specific options here:
run_dir="~/tmp"


print(parsl.__version__)

user_opts = {
    "worker_init":      f"source ~/.venv/parsl/bin/activate; cd {run_dir}", # load the environment where parsl is installed
    "scheduler_options":"#PBS -l filesystems=home:eagle:grand -l singularity_fakeroot=true" , # specify any PBS options here, like filesystems
    "account":          "IMPROVE",
    "queue":            "R1819593",
    "walltime":         "1:00:00",
    "nodes_per_block":  10, # think of a block as one job on polaris, so to run on the main queues, set this >= 10
}

additional_definitions = CSA.additional_definitions


""" additional_definitions = {
    "model" : {
        "type" : str,
        "default" : None,
        "help" : "Singulritiy image for the model",
        "choices" : None,
        "nargs" : None
    },
    "data_set" : {  
        "type" : str,
        "default" : None,
        "help" : "Data set",
        "choices" : None,
        "nargs" : None
    },
} """
#Load CLI parameters
cli = CLI()
cli.set_command_line_options(options=additional_definitions)
cli.get_command_line_options()
params_cli = cli.params
print(params_cli)
#Load parsl parameters
pcfg = Parsl()
common_cfg  = Common_config()
common_cfg.load_config(cli.params['parsl_config_file']) ## USE parsl_config_file as a CLI
parsl_config = {}
for k in common_cfg.option.keys():
    parsl_config.update(common_cfg.option[k])

#Load CSA Parameters
common_cfg  = Common_config()
common_cfg.load_config(cli.params['csa_config_file'])
csa_config = common_cfg.option
params_csa = {}
for k in csa_config.keys():
    params_csa.update(csa_config[k])


# We want CLI options to take precendence, Followed by the CSA config file, followed by the default options ????

#csa = CSA()
#csa = csa.load_config(cli.params['csa_config_file'])

###

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
fdir = Path(__file__).resolve().parent
y_col_name = "auc"

# Check that environment variable "IMPROVE_DATA_DIR" has been specified
if os.getenv("IMPROVE_DATA_DIR") is None:
    raise Exception("ERROR ! Required system variable not specified.  \
                    You must define IMPROVE_DATA_DIR ... Exiting.\n")
os.environ["CANDLE_DATA_DIR"] = os.environ["IMPROVE_DATA_DIR"]

maindir = Path(os.environ['IMPROVE_DATA_DIR'])
CSA_DATA_DIR = Path(f"./{maindir}/csa_data")
INPUT_DIR = Path(f"./{maindir}/input")
OUTPUT_DIR = Path(f"./{maindir}/output")

""" params = CSA.initialize_parameters(
    filepath=fdir, # CHANGE PATH IF NEEDED TO THE DIRECTORY CONTAINING THE CONFIG FILE
    default_model="Paccmann_MCA_default_model_csa.txt"  ### HARD CODING CONFIG FILE ********** CHECK THIS - Add Argparse for config file
) """



logger = logging.getLogger(f"{params_csa['model_name']}")

raw_datadir = CSA_DATA_DIR/ params_cli["raw_data_dir"] #### HARD CODING. Add a candle parameter for csa_data ??
x_datadir = raw_datadir / params_cli["x_data_dir"]
y_datadir = raw_datadir / params_cli["y_data_dir"]
splits_dir = raw_datadir / params_cli["splits_dir"]


def build_split_fname(source_data_name, split, phase):
    """ Build split file name. If file does not exist continue """
    if split=='all':
        return f"{source_data_name}_{split}.txt"
    return f"{source_data_name}_split_{split}_{phase}.txt"


config = Config(
        executors=[
            HighThroughputExecutor(
                label=parsl_config['label'],
                worker_debug=bool(parsl_config['worker_debug']),
                cores_per_worker=int(parsl_config['cores_per_worker']),
                provider=LocalProvider(
                    channel=LocalChannel(),
                    init_blocks=int(parsl_config['init_blocks']),
                    max_blocks=int(parsl_config['max_blocks'])
                )
                #,max_workers_per_node=parsl_config['max_workers_per_node'],
            )
        ],
        strategy=None,
    )

#Run preprocess first
workflow_csa.preprocess(params)

futures = {}
parsl.clear()
# checkpoints = get_all_checkpoints(run_dir)
# print("Found the following checkpoints: ", checkpoints)
parsl.load(config)



preprocess_futures = [workflow_csa.preprocess(splits_dir/build_split_fname(source_data_name, split), output_data_dir, params_csa) 
                      for source_data_name in params_csa['source_data_name'] for split in params_csa['split']]

results=workflow_csa.preprocess(params_csa)
#results = Demo.run(config={},debug=True)

for key in results.keys():
    print(f"{key} : {results[key]}")


parsl.clear()