from string import ascii_letters
from matplotlib import widgets
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mt
import os


class Plotter:
    """
    Plotter is a class with static methods that allow a user to create plots and have these plots be saved to the reporting/images directory
    """

    @staticmethod
    def plot_correlation_matrix(dataframe, seaborn_theme='white', figure_name="correlation_matrix", save_figure_format='png', cmap_diverging_palette_husl_colours=[150, 275]):
        """
        Plots a correlation matrix from the given dataframe

        Parameters
        ----------
        dataframe : pandas.dataframe
            A pandas dataframe containing the raw data
        seaborn_theme : str, optional
            Input for the seaborn.set_theme() method, by default 'white'
        figure_name : str, optional
            The filename for the figure created by this method, by default "correlation_matrix"
        save_figure_format : str, optional
            the file format (PNG, JPEG, etc) for the plot that will be saved to an external directory, by default 'png'
        cmap_diverging_palette_husl_colours : list, optional
            a float array containing the HUSL colours [h_neg, h_pos] for the extents of the heatmap of the correlation matrix, by default [240, 10]
        """
        sns.set_theme(style=seaborn_theme)
        corr_matrix = dataframe.corr()
        cmap = sns.diverging_palette(
            cmap_diverging_palette_husl_colours[0], cmap_diverging_palette_husl_colours[1], as_cmap=True)
        fig, ax = plt.subplots()
        sns.heatmap(corr_matrix, cmap=cmap, center=0).set(
            title="Correlation Matrix")
        plt.tight_layout()
        plt.savefig(f"{figure_name}.{save_figure_format}")
        plt.clf()

    @staticmethod
    def _setup_plot(title, xlabel, ylabel, figsize):
        plt.figure(figsize=figsize)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.tight_layout()

    @staticmethod
    def plot_lines(figure_name, x, y, dataframes_dict, std_error=None, save_figure_format='png', xlabel=None, ylabel=None, title=None, perconfig=True, figsize=(6,4), save_dir=None, **kwargs):
        """
        Plots lines on the same set of axes

        Parameters
        ----------
        figure_name : string
            The filename for the figure created by this method
        x : string
            The column name for the x column in the dataframe  
        y : list[str]
            An array of strings of the y-axis column names for each dataframe 
        dataframes_dict : dictionary 
            Dictionary with key-value pairs for each config: dataframe 
        std_error: list[str], optional
            The std error columns corresponding to each y value, by default None
        save_figure_format : str, optional
            The file format (PNG, JPEG, etc) for the plot that will be saved to an external directory, by default 'png'
        """
        if save_dir is not None:
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
        with plt.style.context(['science', 'std-colors']):
            Plotter._setup_plot(title, xlabel, ylabel, figsize)
            for config, frame_dict in dataframes_dict.items():
                if perconfig:
                    Plotter._setup_plot(f"{title} ({config})", xlabel, ylabel, figsize)
                if std_error is None:
                    for y_value in y:
                        for frame_name, frame in frame_dict.items():
                            plt.plot(x, y_value, data=frame, 
                                label=(frame_name if perconfig else f"{frame_name} - {config}"), 
                                **kwargs
                            )
                elif len(y) == len(std_error):
                    for y_value, y_std_dev in zip(y, std_error):
                        for frame_name, frame in frame_dict.items():
                            plt.errorbar(x, y_value, yerr=y_std_dev, data=frame, 
                                label=(frame_name if perconfig else f"{frame_name} - {config}"), 
                                **kwargs
                            )
                else: 
                    raise ValueError("Expected y and std_error to be the same length")
                if perconfig:
                    plt.legend(loc="best", title="Legend")
                    plt.savefig(os.path.join(save_dir, f"{config.replace('.', 'pt')}-{figure_name}.{save_figure_format}"))
                    plt.clf()
            if not perconfig:
                plt.legend(bbox_to_anchor=(1.05, 1.0), loc="upper left", title="Legend")
                plt.savefig(os.path.join(save_dir, f"{figure_name}.{save_figure_format}"))
                plt.clf()
        
        
