# ideal_completion.py

def run_streamlit_graph():
    from streamlit_react_flow import react_flow
    import streamlit as st

    st.title("React-Flow Testing")

    st.subheader("Acquaintances Graph")

    a = 1

    elements = [
        { "id": '1', "data": { "label": 'Alex'  }, "type":"input","style": { "background": '#ffcc50', "width": 100 },
            "position": { "x": 100, "y": 100 } },
        { "id": '2', "data": { "label": 'John Doe' },"position": { "x": 300, "y": 100 }},
        { "id": '3', "source": '1', "target": '2', "animated": True },
    ]

    # Use `extend` to add items to the list instead of appending a sublist
    elements.extend([{"id": str(x+4), "data": { "label": title }, "type": "output", "position": { "x": 170*x, "y": 300+x }} for x, title in enumerate(["John Doe", "John Doe", "John Doe", "John Doe"])])
    elements.extend([{"id":f"e{a}-{j}","source":str(a),"target":str(j)} for j in range(a+3, a+7) for i in range(4)])
    flowStyles = { "height": 500, "width": 1100 }

    # Create the react flow component instance
    react_flow("acquaintances", elements=elements, flow_styles=flowStyles)