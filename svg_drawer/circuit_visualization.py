from qiskit.visualization import utils
from .image_drawer import ImageDrawer

def _matplotlib_circuit_drawer(
    circuit,
    scale=None,
    filename=None,
    defs=None,
    style=None,
    rich_snips=False,
    plot_barriers=True,
    reverse_bits=False,
    justify=None,
    idle_wires=True,
    with_layout=True,
    fold=None,
    initial_state=False,
    cregbundle=True,
):

    qubits, clbits, nodes = utils._get_layered_instructions(
        circuit, reverse_bits=reverse_bits, justify=justify, idle_wires=idle_wires
    )
    if with_layout:
        layout = circuit._layout
    else:
        layout = None

    if fold is None:
        fold = 25

    global_phase = circuit.global_phase if hasattr(circuit, "global_phase") else None
    
    qcd = ImageDrawer(
        qubits,
        clbits,
        nodes,
        scale=scale,
        defs=defs,
        style=style,
        rich_snips=rich_snips,
        reverse_bits=reverse_bits,
        plot_barriers=plot_barriers,
        layout=layout,
        fold=fold,
        initial_state=initial_state,
        cregbundle=cregbundle,
        global_phase=global_phase,
        qregs=circuit.qregs,
        cregs=circuit.cregs,
        calibrations=circuit.calibrations,
    )
    return qcd.draw(filename)

def circuit_drawer(
    circuit,
    scale=None,
    filename=None,
    defs=None,
    style=None,
    rich_snips=False,
    interactive=False,
    plot_barriers=True,
    reverse_bits=False,
    justify=None,
    idle_wires=True,
    with_layout=True,
    fold=None,
    initial_state=False,
    cregbundle=True,
):

    image = _matplotlib_circuit_drawer(
        circuit,
        scale=scale,
        filename=filename,
        defs=defs,
        style=style,
        rich_snips=rich_snips,
        plot_barriers=plot_barriers,
        reverse_bits=reverse_bits,
        justify=justify,
        idle_wires=idle_wires,
        with_layout=with_layout,
        fold=fold,
        initial_state=initial_state,
        cregbundle=cregbundle,
    )

    if image and interactive:
        image.show()
    return image