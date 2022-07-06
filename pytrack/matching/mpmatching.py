from collections import deque

from . import mpmatching_utils


def viterbi_search(G, trellis, start="start", target="target", beta=mpmatching_utils.BETA,
                   sigma=mpmatching_utils.SIGMA_Z):
    """ Function to compute viterbi search and perform Hidden-Markov Model map-matching.

    Parameters
    ----------
    G: networkx.MultiDiGraph
        Street network graph.
    trellis:
    start: str, optional, default: "start"
        Starting node.
    target: str, optional, default: "target"
        Target node.
    beta: float
        This describes the difference between route distances and great circle distances. See https://www.ismll.uni-hildesheim.de/lehre/semSpatial-10s/script/6.pdf
        for a more detailed description of its calculation.

    sigma: float
        It is an estimate of the magnitude of the GPS error. See https://www.ismll.uni-hildesheim.de/lehre/semSpatial-10s/script/6.pdf
        for a more detailed description of its calculation.

    Returns
    -------
    joint_prob: dict
        Joint probability for each node.
    predecessor: dict
        Predecessor for each node.

    Notes
    -----
    See https://www.ismll.uni-hildesheim.de/lehre/semSpatial-10s/script/6.pdf for a more detailed description of this
    method.
    """

    # Initialize joint probability for each node
    joint_prob = {}
    for u_name in trellis.nodes():
        joint_prob[u_name] = 0
    predecessor = {}
    queue = deque()

    queue.append(start)
    joint_prob[start] = mpmatching_utils.emission_prob(trellis.nodes[start]["candidate"], sigma)
    predecessor[start] = None

    while queue:
        # Extract node u
        u_name = queue.popleft()
        u = trellis.nodes[u_name]["candidate"]

        if u_name == target:
            break
        for v_name in trellis.successors(u_name):
            v = trellis.nodes[v_name]["candidate"]

            new_prob = joint_prob[u_name] * mpmatching_utils.transition_prob(G, u, v, beta) * \
                mpmatching_utils.emission_prob(v, sigma)

            if joint_prob[v_name] < new_prob:
                joint_prob[v_name] = new_prob
                predecessor[v_name.split("_")[0]] = u_name
            if v_name not in queue:
                queue.append(v_name)

    return joint_prob[target], predecessor
