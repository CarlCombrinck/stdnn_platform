from stdnn.experiments.results import (
    RunResult, 
    RunResultSet,
    ExperimentResultSet
)
from stdnn.experiments.utils import dictionary_update_deep
from ConfigSpace.util import generate_grid
from tqdm import tqdm

class ExperimentConfig():
    """
    Class to represent and manage the parameters for running
    an experiment (a single pass through the ML pipeline)
    """

    def __init__(self, config, label):
        """
        Constructor for ExperimentConfig

        Parameters
        ----------
        config : dict
            Dictionary of experiment parameters
        label : str
            A label/name for identifying the experiment configuration
        """
        self._config = dict(config)
        self._label = label
    
    @property
    def model_type(self):
        """
        The type of the model to be configured and passed through the pipeline
        """
        return self._config.get("model").get("meta").get("type")

    @property
    def model_manager(self):
        """
        The type of the model manager to manage the configured model
        """
        return self._config.get("model").get("meta").get("manager")

    def get_label(self):
        """
        Experiment label getter

        Returns
        -------
        str
            The experiment label
        """
        return self._label

    def get_model_params(self):
        """
        Getter for model parameters (shallow copy)

        Returns
        -------
        dict
            A dictionary of model parameters 
            (to be passed to constructor)
        """
        return dict(self._config.get("model").get("params"))

    def get_preprocessing_params(self):
        """
        Getter for preprocessing parameters (shallow copy)

        Returns
        -------
        dict
            A dictionary of preprocessing parameters 
            (to be passed to constructor)
        """
        return dict(self._config.get("preprocess").get("params"))

    def get_training_params(self):
        """
        Getter for training parameters (shallow copy)

        Returns
        -------
        dict
            A dictionary of training parameters 
            (to be passed to train method)
        """
        return dict(self._config.get("train").get("params"))

    def get_validation_params(self):
        """
        Getter for validation parameters (shallow copy)

        Returns
        -------
        dict
            A dictionary of validation parameters 
            (to be passed to validate method)
        """
        return dict(self._config.get("validate").get("params"))

    def get_testing_params(self):
        """
        Getter for testing parameters (shallow copy)

        Returns
        -------
        dict
            A dictionary of testing parameters 
            (to be passed to test method)
        """
        return self._config.get("test").get("params")


class ExperimentConfigManager():
    """
    Class for managing the configuration of the experiments to be run
    """

    def __init__(self, raw_pipeline_config, raw_exp_config):
        """
        Constructor for ExperimentConfigManager

        Parameters
        ----------
        raw_pipeline_config : dict
            Dictionary of structured config data for ML pipeline
        raw_exp_config : dict
            Dictionary of structured config data for the experiments
        """
        self._raw_pipeline_config = dict(raw_pipeline_config)
        self.raw_exp_config = dict(raw_exp_config)
        self._config_space = self.raw_exp_config.get("config_space")
        self.grid = self._generate_grid()

    def _generate_grid(self):
        """
        Internal method for generating hyperparameter grid

        Returns
        -------
        list[ConfigSpace.Configuration]
            A list of hyperparameter configurations
        """
        grid_dims = self.raw_exp_config.get("grid")
        return generate_grid(self._config_space, grid_dims)

    def print_info(self):
        total_configs = 1
        hyperparam_str = []
        for param in self._config_space.get_hyperparameters():
            hyperparam_str.append(f"{param.name} (steps={self.raw_exp_config.get('grid').get(param.name)})")
            total_configs *= self.raw_exp_config.get('grid').get(param.name)
        print(
            "\nExperiment Configuration", 
            "-" * 75, 
            "Configured Hyperparameters:\t" + ", ".join(hyperparam_str),
            "Total Configurations      :\t" + str(total_configs),
            "Runs per Configuration    :\t" + str(self.get_runs()),
            "-" * 75,
            sep="\n")

    def get_runs(self):
        """
        Returns the number of repeat runs of the experiment

        Returns
        -------
        int
            The number of repeat runs
        """
        return self.raw_exp_config.get("runs")

    def configurations(self):
        """
        Generator for iterating over each unique configuration of the experiment

        Yields
        -------
        ExperimentConfig
            The next configuration of the experiment
        """
        # Loop over each hyperparameter combination
        for cell in self.grid:
            current_config = dict(self._raw_pipeline_config)
            label = []
            # For each hyperparameter, update (deep) the current configuration with its value
            for param, value in cell.get_dictionary().items():
                key = self._config_space.get_hyperparameter(param).meta.get("config")
                if key is None:
                    raise ValueError(f"No meta config value specified for ConfigSpace hyperparameter")
                if current_config.get(key) is None:
                    raise ValueError(f"No dictionary associated with provided meta config value '{key}'")
                dictionary_update_deep(current_config.get(key), param, value)
                label.append(f"{param}={round(value, 6) if isinstance(value, (int, float)) else value}")
            yield ExperimentConfig(current_config, ",".join(label))

class Experiment():
    """
    Class representing a configured ML pipeline, responsible for executing this pipeline
    with the specified parameters and producing results
    """
    def __init__(self, config):
        """
        Constructor for Experiment

        Parameters
        ----------
        config : ExperimentConfig
            The configuration for the experiment
        """
        self._config = config
        self._results = RunResultSet()

    # TODO Refactor to add explicit validation?
    def run(self, repeat=1):
        """
        Run the ML pipeline repeat times with the given configuration

        Parameters
        ----------
        repeat : int, optional
            The number of times to repeat the experiment, by default 1
        """
        progress_bar = tqdm(total=repeat)
        for run in range(repeat):
            model = self._config.model_type(**self._config.get_model_params())
            model_manager = self._config.model_manager()
            model_manager.set_model(model)
            result = model_manager.run_pipeline(self._config)
            self._results.add_result(result)
            progress_bar.update(1)
        progress_bar.close()

    def get_run_results(self):
        """
        Getter for Run results

        Returns
        -------
        RunResultSet
            A deep copy of the set of RunResults
        """
        return self._results.copy()

class ExperimentManager():
    """
    Class for managing the running of all experiments and collation of results
    """
    def __init__(self, config):
        """
        Constructor for ExperimentManager

        Parameters
        ----------
        config : ExperimentConfigManager
            A config manager for the experiments
        """
        self._config = config
        self._config.print_info()

    # TODO Customize aggregation
    # TODO Generalize (too specific in terms of aggregation)
    def run_experiments(self):
        """
        Runs experiment for each configuration and returns
        collated/aggregated results

        Returns
        -------
        ExperimentResultSet
            Set of results for each experiment configuration
        """
        results = ExperimentResultSet()

        for config in self._config.configurations():
            experiment = Experiment(config)
            print(f"\nRunning Experiment '{config.get_label()}'...")
            experiment.run(repeat=self._config.get_runs())
            results.add_result(experiment.get_run_results().combine(), key=config.get_label())
        return results