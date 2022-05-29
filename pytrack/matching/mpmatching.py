from collections import deque

from . import mpmatching_utils


def viterbi_search(G, trellis, start, target):
    # Initialize joint probability for each node
    joint_prob = {}
    for u_name in trellis.nodes():
        joint_prob[u_name] = 0
    predecessor = {}
    queue = deque()

    queue.append(start)
    joint_prob[start] = mpmatching_utils.emission_prob(trellis.nodes[start]["candidate"])
    predecessor[start] = None

    while queue:
        # Extract node u
        u_name = queue.popleft()
        u = trellis.nodes[u_name]["candidate"]

        if u_name == target:
            break
        for v_name in trellis.successors(u_name):
            v = trellis.nodes[v_name]["candidate"]

            new_prob = joint_prob[u_name] * mpmatching_utils.transition_prob(G, u, v) * mpmatching_utils.emission_prob(
                v)
            if joint_prob[v_name] < new_prob:
                joint_prob[v_name] = new_prob
                predecessor[v_name.split("_")[0]] = u_name
            if v_name not in queue:
                queue.append(v_name)

    return joint_prob[target], predecessor
