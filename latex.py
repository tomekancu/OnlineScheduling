from typing import List, Any, Optional

from data import Parameters, Variable
from metrics import MetricType, make_mean_metrics
from data import MetricsDatabase
from schedulers.abstract import AbstractScheduler


def tkiz_plot(metrics_database: MetricsDatabase,
              default: Parameters, testing_type: Variable, testing_values: List[Any],
              schedulers: List[AbstractScheduler], metric_type: MetricType, legend_to: Optional[str] = None):
    plots = []
    for i, scheduler in enumerate(schedulers):
        alg_name = scheduler.get_name()
        alg_title = scheduler.get_title_latex()
        coordinates = ""
        for val in testing_values:
            params = default.make_instance_for(testing_type, val)
            metrics_list = metrics_database.get_metrics(params, alg_name)
            metric_value = make_mean_metrics(metrics_list).get(metric_type)
            if metric_value < 0.000000001:
                metric_value = 0.000000001
            coordinates += f"({val}, {metric_value:.9f}) "
        plots.append(f"\\addplot+[sp{i}]\n"
                     f"coordinates {{\n"
                     f"    {coordinates}\n"
                     f"}};\n"
                     f"\\addlegendentry{{{alg_title}}}\n")
    xmode = "normal"
    if testing_type == Variable.COV:
        xmode = "log"
    ymode = "log"  # log
    if metric_type == MetricType.RESOURCE_USAGE \
            or metric_type == MetricType.ACTUAL_RESOURCE_LOAD \
            or metric_type == MetricType.DELAY_TIME_TO_RESPONSE_TIME \
            or metric_type == MetricType.DELAY_PROCESSING_TIME_TO_RESPONSE_TIME \
            or metric_type == MetricType.IDEAL_DELAY_TIME_TO_RESPONSE_TIME:
        ymode = "normal"
    additional_axis_config = [f"    legend style = {{at={{(0.5,-0.15)}}, anchor=north}},\n"]
    if legend_to is not None:
        additional_axis_config.append(f"    legend to name={legend_to},\n")
    if metric_type == MetricType.MEAN_DELAY_TIME or metric_type == MetricType.MEAN_DELAY_PROCESSING_TIME:
        additional_axis_config.append(f"    ymin=0.00005,\n")
    join_additional_axis_config = "".join(additional_axis_config)
    join_plots = "\n".join(plots)
    all_plots = (f"\\begin{{tikzpicture}}[]\n"
                 f"\n"
                 f"\\begin{{axis}}[\n"
                 f"    xlabel = {{{testing_type.value}}}, ylabel = {{{metric_type.value}}},\n"
                 f"    axis lines = left,\n"
                 f"    grid style = dashed,\n"
                 f"    ymode = {ymode}, xmode = {xmode},\n"
                 f"    log basis y = 2, log basis x = 2,\n"
                 f"    legend columns=3,\n"
                 f"{join_additional_axis_config}"
                 f"]\n"
                 f"\n"
                 f"{join_plots}"
                 f"\n"
                 f"\\end{{axis}}\n"
                 f"\n"
                 f"\\end{{tikzpicture}}\n")
    return all_plots


def print_latex_plots_for_data(metrics_database: MetricsDatabase,
                               default: Parameters, testing_type: Variable, testing_values: List[Any],
                               schedulers: List[AbstractScheduler],
                               file="temp/metrics-latex-plot.tex"):
    tikz = []
    for i, metric_type in enumerate([MetricType.MEAN_RESPONSE_TIME,
                                     MetricType.MEAN_DELAY_TIME,
                                     MetricType.MEAN_DELAY_PROCESSING_TIME,
                                     MetricType.MEAN_IDEAL_DELAY_TIME,
                                     # MetricType.DELAY_TIME_TO_RESPONSE_TIME,
                                     # MetricType.DELAY_PROCESSING_TIME_TO_RESPONSE_TIME,
                                     # MetricType.IDEAL_DELAY_TIME_TO_RESPONSE_TIME,
                                     MetricType.RESOURCE_USAGE]):
        tikz.append(tkiz_plot(metrics_database,
                              default, testing_type, testing_values, schedulers, metric_type,
                              f"plot{i}"))

    join_tikz = "%\n".join(tikz)
    all_plots = (f"% {testing_type.name}\n"
                 f"% {default.latex()}\n"
                 f"\n"
                 f"\\pgfplotsset{{width=7cm, compat=1.9}}\n"
                 f"\n"
                 "\\tikzstyle{sp0}=[blue,every mark/.append style={fill=blue!80!black},mark=*]\n"
                 "\\tikzstyle{sp1}=[red,every mark/.append style={fill=red!80!black},mark=square*]\n"
                 "\\tikzstyle{sp2}=[brown!60!black,every mark/.append style={fill=brown!80!black},mark=otimes*]\n"
                 "\\tikzstyle{sp3}=[black,mark=star]\n"
                 "\\tikzstyle{sp4}=[blue,every mark/.append style={fill=blue!80!black},mark=diamond*]\n"
                 "\\tikzstyle{sp5}=[red,densely dashed,every mark/.append style={solid,fill=red!80!black},mark=*]\n"
                 "\\tikzstyle{sp6}=[brown!60!black,densely dashed,every mark/.append style={"
                 "solid,fill=brown!80!black},mark=square*]\n"
                 "\\tikzstyle{sp7}=[mark = *, dashed,black,densely dashed,every mark/.append "
                 "style={solid,fill=gray},mark=otimes*]\n"
                 "\\tikzstyle{sp8}=[blue,densely dashed,mark=star,every mark/.append style=solid]\n"
                 f"\n"
                 f"{join_tikz}"
                 f"\n"
                 f"\\pgfplotslegendfromname{{plot0}}")

    with open(f'output/{file}', 'w', encoding='utf-8') as file:
        file.write(all_plots)
    print(default.latex())


def print_latex_plot_for_data(metrics_database: MetricsDatabase,
                              default: Parameters, testing_type: Variable, testing_values: List[Any],
                              schedulers: List[AbstractScheduler], metric_type: MetricType):
    all_plots = tkiz_plot(metrics_database, default, testing_type, testing_values, schedulers, metric_type)
    with open('output/temp/metrics-latex-plot.tex', 'w', encoding='utf-8') as file:
        file.write(all_plots)
    print(default.latex())
