from aima3.planning import *

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
        return all([kb.ask(q) is not False for q in required])

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


