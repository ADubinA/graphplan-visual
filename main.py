import engine
gp = engine.GraphPlanVis()
gp.create_problem("examples/block-world/domain.pddl",
                    "examples/block-world/p03.pddl")
# gp.expand_level()
# gp.expand_level()

# gp.expand_level()
print(gp.solve())
# gp.visualize()
print(len(gp.graphplan.graph.levels))
# for i in range(100):
#     gp.expand_level()
#
# print(gp.solve())

# gp.visualize()
# print(engine.spare_tire_graphplan())

# Features
# ______________________
# button to expand level
# button to solve solution
# log console
# show no-ops
# load domain file
# load problem file
# show mutexes