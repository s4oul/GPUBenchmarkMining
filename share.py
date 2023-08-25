import logging
import os
import logging

import datetime

linestyle_str = {
    'solid': 'solid',  # Same as (0, ()) or '-'
    'dotted': 'dotted',  # Same as (0, (1, 1)) or ':'
    'dashed': 'dashed',  # Same as '--'
    'dashdot': 'dashdot',  # Same as '-.'

    'loosely dotted': (0, (1, 10)),
    'dotted': (0, (1, 1)),
    'densely dotted': (0, (1, 1)),
    'long dash with offset': (5, (10, 3)),
    'loosely dashed': (0, (5, 10)),
    'dashed': (0, (5, 5)),
    'densely dashed': (0, (5, 1)),

    'loosely dashdotted': (0, (3, 10, 1, 10)),
    'dashdotted': (0, (3, 5, 1, 5)),
    'densely dashdotted': (0, (3, 1, 1, 1)),

    'dashdotdotted': (0, (3, 5, 1, 5, 1, 5)),
    'loosely dashdotdotted': (0, (3, 10, 1, 10, 1, 10)),
    'densely dashdotdotted': (0, (3, 1, 1, 1, 1, 1)),

    'empty': ''
}


class CanvasPlot:

    def __init__(self):
        self.axe_x = []
        self.axe_y = []


class Share:

    def __init__(self):
        self.results = {}

    def add_miner(self, miner_name: str):
        self.results[miner_name] = {
            'shares': [],
        }

    def add_share(self, miner_name: str, seconds: float, nonce: str):
        self.results[miner_name]['shares'].append({
            'nonce': str(nonce),
            'seconds': seconds
        })

    def draw_graph(self):
        for miner_name, result in self.results.items():
            canvas = CanvasPlot()
            x = 0
            for share in result['shares']:
                canvas.axe_x.append(x)
                canvas.axe_y.append(share['seconds'])
                x += 1
            self.__draw_plot(miner_name,
                             'Number of shares found',
                             'Time taken to find the share',
                             'solid',
                             canvas)

    @staticmethod
    def __draw_plot(title: str, x_label: str, y_label: str, style: str, canvas: CanvasPlot):
        import matplotlib.pyplot as graph
        graph.plot(
            canvas.axe_x,
            canvas.axe_y,
            label=f'{title}',
            color='green',
            marker='*',
            markersize=1,
            linestyle=linestyle_str[style],
            linewidth=1
        )
        graph.xlabel(x_label)
        graph.ylabel(y_label)

        base_folder = os.path.join('results')
        if os.path.exists(base_folder) is False:
            os.makedirs(base_folder)
        filename = os.path.join(base_folder, f'{title}.png')
        logging.info(f'Wiring Graph ===> {filename}')
        if os.path.exists(filename):
            os.remove(filename)
        graph.savefig(filename)
        graph.close()