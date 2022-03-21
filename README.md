# SVG Circuit Drawer

An alternative circuit drawer for Qiskit with better performance and enhanced styling capabilities.

Two of the issues we faced while working on [Qiskit timeline debugger](https://github.com/kdk/qiskit-timeline-debugger) were related to circuit drawer:
-  Its performance degrades rapidly when circuit size increases.
-  Its styling capabilities are very limited.

Qiskit circuit drawer uses Matplotlib to generate circuit plots. Matplotlib is the root cause of this bad performance. Although it makes great publication-quality graphics, Matplotlib's performance is not that good.

SVG is XML-based which means we can easily create SVG images in Python as any text files. And since all modern browsers supports SVG, we can use [IPython.display.HTML](https://ipython.readthedocs.io/en/stable/api/generated/IPython.display.html#IPython.display.HTML) to display it. Moreover, SVG supports interactivity and animation which open the door to advanced features as demonstrated in this project.

SVG circuit drawer is 8 times faster than Matplotlib-based drawer for qubits < 50 and depth < 150. The difference increases with circuit size. We get this performance without compromising the quality of the resulting graphics. The following graphs show how time scales with number of qubits and circuit depth for both drawers:

![Number of Qubits](https://github.com/EgrettaThula/svg_circuit_drawer/blob/main/_static/num-qubits.png?raw=true)

![Depth](https://github.com/EgrettaThula/svg_circuit_drawer/blob/main/_static/depth.png?raw=true)

You can use all capabilities provided by CSS (the standard styling language) to style your circuit. *test.ipynb* notebook in the project's root directory contains some examples on this.

**Note**: This is just a POC. Do not judge the code quality.