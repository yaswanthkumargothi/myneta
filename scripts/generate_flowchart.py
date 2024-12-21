import langgraph

def generate_flowchart():
    # Create a new flowchart
    flowchart = langgraph.Flowchart()

    # Add nodes and edges
    flowchart.add_node("Start")
    flowchart.add_node("Process 1")
    flowchart.add_node("Decision")
    flowchart.add_node("Process 2")
    flowchart.add_node("End")

    flowchart.add_edge("Start", "Process 1")
    flowchart.add_edge("Process 1", "Decision")
    flowchart.add_edge("Decision", "Process 2", label="Yes")
    flowchart.add_edge("Decision", "End", label="No")
    flowchart.add_edge("Process 2", "End")

    # Render the flowchart
    flowchart.render("flowchart.png")

if __name__ == "__main__":
    generate_flowchart()
