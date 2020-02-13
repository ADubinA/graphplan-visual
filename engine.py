import pddlpy
from aima3.planning import *
import matplotlib.pyplot as plt
import networkx as nx


class MyGraphPlan:
    """
    Class for formulation GraphPlan algorithm
    Constructs a graph of state and action space
    Returns solution for the planning problem
    """

    def __init__(self, pddl, negkb):
        self.graph = Graph(pddl, negkb)
        self.nogoods = []
        self.solution = []

    def check_leveloff(self):
        first_check = (set(self.graph.levels[-1].current_state_pos) ==
                       set(self.graph.levels[-2].current_state_pos))
        second_check = (set(self.graph.levels[-1].current_state_neg) ==
                        set(self.graph.levels[-2].current_state_neg))

        if first_check and second_check:
            return True

    def extract_solution(self, goals_pos, goals_neg, index):
        level = self.graph.levels[index]
        if not self.graph.non_mutex_goals(goals_pos+goals_neg, index):
            self.nogoods.append((level, goals_pos, goals_neg))
            return False

        level = self.graph.levels[index-1]

        # Create all combinations of actions that satisfy the goal
        actions = []
        for goal in goals_pos:
            actions.append(level.next_state_links_pos[goal])

        for goal in goals_neg:
            actions.append(level.next_state_links_neg[goal])

        all_actions = list(itertools.product(*actions))

        # Filter out the action combinations which contain mutexes
        non_mutex_actions = []
        for action_tuple in all_actions:
            action_pairs = itertools.combinations(list(set(action_tuple)), 2)
            non_mutex_actions.append(list(set(action_tuple)))
            for pair in action_pairs:
                if set(pair) in level.mutex:
                    non_mutex_actions.pop(-1)
                    break

        if not non_mutex_actions:
            return False

        # Recursion
        for action_list in non_mutex_actions:
            if [action_list, index] not in self.solution:
                self.solution.append([action_list, index])

                new_goals_pos = []
                new_goals_neg = []
                for act in set(action_list):
                    if act in level.current_action_links_pos:
                        new_goals_pos = new_goals_pos + level.current_action_links_pos[act]

                for act in set(action_list):
                    if act in level.current_action_links_neg:
                        new_goals_neg = new_goals_neg + level.current_action_links_neg[act]

                if abs(index)+1 == len(self.graph.levels):
                    if all(goal in self.graph.levels[0].current_state_pos for goal in new_goals_pos):
                        return True
                    else:
                        return False
                elif (level, new_goals_pos, new_goals_neg) in self.nogoods:
                    return False
                else:
                    success = self.extract_solution(new_goals_pos, new_goals_neg, index-1)
                    if success and index == -1:
                        break
                    elif success and index != -1:
                        return True
                    else:
                        self.solution.pop()



        if index == -1:
            # Level-Order multiple solutions
            solution = []
            for item in self.solution:
                if item[1] == -1:
                    solution.append([])
                    solution[-1].append(item[0])
                else:
                    solution[-1].append(item[0])

            for num, item in enumerate(solution):
                item.reverse()
                solution[num] = item

            return solution
        return False

class GraphPlanVis:
    def __init__(self):
        self.domprob = None
        self.pddl = None
        self.negkb = FolKB([])
        self.graphplan = None
        self.nx_graph = nx.DiGraph()
        self.is_ready = False

    def visualize(self, ax=None, for_qt=True):

        self.nx_graph = nx.DiGraph()
        self._create_nx_graph()
        self.draw_graph(len(self.graphplan.graph.levels), ax=ax)
        if for_qt:
            return ax
        else:
            plt.show()

    def create_problem(self, domain_file_path, problem_file_path):

        self.domprob = pddlpy.DomainProblem(domain_file_path, problem_file_path)

        self.pddl = to_pddl_aima_obj(self.domprob)
        # self.pddl = three_block_tower()
        self.negkb = FolKB([])
        self.graphplan = MyGraphPlan(self.pddl, self.negkb)
        self.nx_graph = nx.DiGraph()
        self.is_ready = True


    def expand_level(self):
        self.graphplan.graph.expand_graph()

    def solve(self, with_expanding=True):

        # TODO address this
        # [expr('On(A, B)'), expr('On(B, C)')]
        goals_pos = [parse_pddl2expr(i) for i in list(self.domprob.goals())]
        goals_neg = []

        while True:
            self.graphplan.solution = []
            if (self.pddl.goal_test_func(self.graphplan.graph.levels[-1].poskb)and
                    self.graphplan.graph.non_mutex_goals(goals_pos + goals_neg, -1)):
                solution = self.graphplan.extract_solution(goals_pos, goals_neg, -1)
                if solution:
                    break


            if not with_expanding:
                return []

            self.graphplan.graph.expand_graph()
            if len(self.graphplan.graph.levels) >= 2 and self.graphplan.check_leveloff():
                solution = []
                break


        return solution

    def _create_nx_graph(self):
        """
        create a networkx graph for visualization
        :param graphplan: an aima3 graphplan object
        :return: networkx graph
        """
        self.nx_graph = nx.DiGraph()
        levels = self.graphplan.graph.levels

        for i in range(len(levels)):
            self._add_level_to_nx_graph(levels[i], i + 1)

    def _add_level_to_nx_graph(self, level, level_num):
        """

        :type level: Level
        :param level: Layer object
        :param nx_graph:
        :return:
        """
        # add current state nodes if they dont exist
        if level_num == 1:
            for state in level.current_state_pos:
                self._add_node("pos_state", state, 0)
            for state in level.current_state_neg:
                self._add_node("neg_state", state, 0)

        # add action nodes
        for action, links in level.current_action_links_pos.items():
            self._create_nx_graph_links(action, "action", links, "pos_state", level_num)

        for action, links in level.current_action_links_neg.items():
            self._create_nx_graph_links(action, "action", links, "neg_state", level_num)

        # add next state nodes
        for state, links in level.current_state_links_pos.items():
            self._create_nx_graph_links(state, "pos_state", links, "action", level_num)
        for state, links in level.current_state_links_neg.items():
            self._create_nx_graph_links(state, "neg_state", links, "action", level_num)

        # add next state nodes
        for state, links in level.next_state_links_pos.items():
            self._create_nx_graph_links(state, "pos_state", links, "action", level_num)
        for state, links in level.next_state_links_neg.items():
            self._create_nx_graph_links(state, "neg_state", links, "action", level_num)

    def _create_nx_graph_links(self, node_name, node_type, links, links_type, level_num, **kwargs):
        """
        Helper function to create the nx graph. Is used for transforming
        level.()_links_() to the nx_graph
        :param node_name: name of the method for the node
        :param node_type: type of the node ("action", "pos_state", "neg_state")
        :param links: an array of links from the function
        :param links_type: their type
        :param level_num: the index of the level currently working on
        :param kwargs: ?
        """
        action_node_name = self._add_node(node_type, node_name, level_num)
        if node_type == "action":
            level_num -= 1

        for link in links:
            link_node_name = self._create_node_name(links_type, link, level_num)
            # TODO check why there is here non created nodes
            if link_node_name not in self.nx_graph.nodes:
                self._add_node(links_type, link, level_num)
            self._add_edge(link_node_name, action_node_name, level_num)

    def _add_node(self, node_type, state_name, level_num, **kwargs):
        """
        :param node_type:
        :param state_name:
        :param kwargs:
        :return: the hash name of the node
        """
        node_name = self._create_node_name(node_type, state_name, level_num)
        self.nx_graph.add_node(node_name, name=state_name, node_type=node_type,
                          level_num=level_num)
        return node_name

    def _add_edge(self, node1, node2, level_num, **kwargs):
        self.nx_graph.add_edge(node1, node2)

    def _create_node_name(self, node_type, name, level_num):
        if name.op == 'Persistence':
            name.op = "P-"
        return f"{level_num}_{name}_{node_type}"

    def draw_graph(self, max_level, ax=None):

        nodes_to_draw = [node for node in self.nx_graph.nodes if self.is_to_draw(node)]
        edges_to_draw = [edge for edge in self.nx_graph.edges if edge[0] in nodes_to_draw and edge[1] in nodes_to_draw]
        labels_to_draw = {node: self.nx_graph.nodes[node]["name"] for node in self.nx_graph.nodes if node in nodes_to_draw}
        # iterate over nodes
        nodes_array = []
        for node in self.nx_graph.nodes:
            node_level = self.nx_graph.nodes[node]["level_num"]

            # add new level when discovered
            if len(nodes_array) <= node_level:
                nodes_array.append({"action": [], "state": []})

            # if node is to draw append it to the array
            if node in nodes_to_draw:
                if self.nx_graph.nodes[node]["node_type"] == "action":
                    nodes_array[node_level]["action"].append(node)
                else:
                    nodes_array[node_level]["state"].append(node)

        pos = self.graphplan_layout(nodes_array, max_level)

        # nx.draw_networkx_nodes(self.nx_graph, pos, nodes_to_draw)
        self._draw_nx_nodes(nodes_array,pos, ax=ax)
        nx.draw_networkx_edges(self.nx_graph, pos, edges_to_draw, ax=ax)
        nx.draw_networkx_labels(self.nx_graph, pos, labels=labels_to_draw,ax=ax)
        # nx.draw(self.nx_graph, pos, node_size=300, node_color='#ffaaaa', with_labels=True)
        # plt.show()

    def _draw_nx_nodes(self, nodes_array, pos, ax=None):
        for node_array in nodes_array:

            pos_state_nodes = [node for node in node_array["state"]
                               if self.nx_graph.nodes[node]["node_type"] == "pos_state"]
            neg_state_nodes = [node for node in node_array["state"]
                               if self.nx_graph.nodes[node]["node_type"] == "neg_state"]

            nx.draw_networkx_nodes(self.nx_graph, pos, pos_state_nodes,node_color="green",ax=ax)
            nx.draw_networkx_nodes(self.nx_graph, pos, neg_state_nodes, node_color="red",ax=ax)

            # draw action nodes
            nx.draw_networkx_nodes(self.nx_graph, pos, node_array["action"],node_shape="s",ax=ax)
    @staticmethod
    def graphplan_layout(nodes_array, max_level):
        """
        create a graphplan positioning for the nodes
        :param nodes_array: an array of the form
        [
        {
        "action":["node1", "node2", ...],
        "state":["node5", "node6", ...]
        },...
        ]
        :param max_level the number of level in the graph
        :return: position dictionary like any networkx layout functions
        """
        pos = {}
        # create positions
        for level_index in range(len(nodes_array)):
            for node_type, nodes in nodes_array[level_index].items():
                for node_index in range(len(nodes)):
                    node = nodes[node_index]

                    if node_type == "action":
                        pos[node] = ((level_index-0.5)/max_level, node_index/len(nodes_array[level_index][node_type]))
                    else:
                        pos[node] = ((level_index)/max_level, node_index/len(nodes_array[level_index][node_type]))

        return pos

    @staticmethod
    def format_solution(solution_array):
        if not solution_array:
            return "No solution found!"
        solution_string = "Solution found and is of the following:\n"
        level = 1
        solution_array = solution_array[0]
        for solution_level in solution_array:
            solution_string += f"{level}:"
            for action in solution_level:
                if "P-" in str(action):
                    continue

                solution_string += str(action)
                solution_string += ", "
            solution_string = solution_string[:-2]
            solution_string += "\n"

            level += 1

        return solution_string

    def is_to_draw(self, node):
        """
        determines if to draw a node or not
        :param node:
        :return:
        """
        # if "Persistence" in node:
        #     return False
        return True

# ------parser-----------------------------------------------------------------------------------
def to_pddl_aima_obj(domprob):
    """
    create a PDDL object to insert to the GraphPlan object.
    :param domprob:  pddlpy object outputted from DomainProblem
    :return: PDDL object
    """
    # Creat init of plan
    inits = []
    for init in list(domprob.initialstate()):
        inits.append(parse_pddl2expr(init))

    def goal_test(kb):
        required = [expr(i) for i in list(domprob.goals())]
        # required = [expr('on(a, b)'), expr('on(b, c)')]
        return all([parse_pddl2expr(q) in kb.clauses for q in required])

    return PDDL(inits, parse_pddl2actions(domprob), goal_test)
    # Create the actions

def parse_pddl2actions(domprob):
    """
    from pddlpy object return a list of Action classes from aima3
    :param domprob:
    :return:
    """
    action_list = []
    for operator_name, operator in domprob.domain.operators.items():

        precond_pos = [parse_pddl2expr(i) for i in operator.precondition_pos]
        precond_neg = [parse_pddl2expr(i) for i in operator.precondition_neg]
        effect_add = [parse_pddl2expr(i) for i in operator.effect_pos]
        effect_rem = [parse_pddl2expr(i) for i in operator.effect_neg]
        action_list.append(Action(parse_action_name(operator),
                                  [precond_pos, precond_neg],
                                  [effect_add, effect_rem]))

    return action_list


def parse_pddl2expr(pddl_atom):
    """

    :param pddl_tuple: given a tuple of the form ("name", "value","value2)
                       will return aima3 expr() of the tuple
    :return:
    """
    pddl_list = list(eval(string_handler(pddl_atom)))
    expresion = str(pddl_list.pop(0))
    expresion += parse_list(pddl_list)
    return expr(expresion)

def parse_action_name(operator):


    expresion = string_handler(operator.operator_name)
    expresion += parse_list(list(operator.variable_list.keys()))
    return expr(expresion)

def parse_list(value_list):
    expresion = "("
    for word in value_list:
        expresion += string_handler(word)
        expresion += ", " if word != value_list[-1] else ""

    expresion += ")"
    return expresion

def string_handler(string_type_object):
    string_type_object = str(string_type_object)
    string_type_object = string_type_object.replace("-", "")
    string_type_object = string_type_object.replace("?", "")
    string_type_object = string_type_object.lower()
    return string_type_object
