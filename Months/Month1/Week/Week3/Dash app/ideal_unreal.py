import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import time
import threading

# Create the Dash app
app = dash.Dash(__name__)
server = app.server

# Layout of the app
app.layout = html.Div([
    html.Div(id='output_message', style={'fontSize': 24, 'marginBottom': 20}),
    dcc.Interval(id='interval-component', interval=15*1000, n_intervals=0),
    html.Button('Start Long Task', id='start-button'),
    dcc.Store(id='start-time', storage_type='session'),
    dcc.Store(id='task-status', storage_type='session', data='Not started')
])

# Start time store update callback
@app.callback(
    Output('start-time', 'data'),
    Output('task-status', 'data'),
    Input('start-button', 'n_clicks')
)
def update_start_time(n_clicks):
    if n_clicks:
        return time.time(), 'Started'
    return dash.no_update, dash.no_update

# Callback to update the elapsed time and task status every 15 seconds
@app.callback(
    Output('output_message', 'children'),
    Input('interval-component', 'n_intervals'),
    State('start-time', 'data'),
    State('task-status', 'data')
)
def update_output_message(n_intervals, start_time, task_status):
    if start_time is None:
        return 'Click the button to start the long task.'
    
    elapsed_time = int(time.time() - start_time)
    return f'Status: {task_status} | Elapsed Time: {elapsed_time} seconds'

# Function for the long running task
def long_running_task(update_status_callback):
    # Simulate a long task by performing steps with sleep intervals
    update_status_callback("Uploading")
    time.sleep(5)  # Simulate the "Uploading" step

    update_status_callback("Validating")
    time.sleep(5)  # Simulate the "Validating" step

    update_status_callback("Analyzing")
    time.sleep(5)  # Simulate the "Analyzing" step

    update_status_callback("Completed")

# Callback to start the long running task
@app.callback(
    Output('start-button', 'disabled'),
    Input('start-button', 'n_clicks'),
    State('start-time', 'data'),
    prevent_initial_call=True
)
def start_long_task(n_clicks, start_time):
    if n_clicks:
        def update_status(status):
            # Use a clientside callback to update the `task-status` store
            app.server.task_status = status

        thread = threading.Thread(target=long_running_task, args=(update_status,))
        thread.start()
        return True  # Disable the button while the task is running
    return dash.no_update

# Callback to update task status in the store
@app.callback(
    Output('task-status', 'data'),
    Input('interval-component', 'n_intervals')
)
def update_task_status(n_intervals):
    return getattr(app.server, 'task_status', 'Started')

if __name__ == '__main__':
    app.run_server(debug=True)
