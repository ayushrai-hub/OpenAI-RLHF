// ideal_completion.js
function addTask(newTask) {
    return { type: 'ADD_TASK', payload: newTask };
}

function updateTask(updatedTask) {
    return { type: 'UPDATE_TASK', payload: updatedTask };
}

function deleteTask(id) {
    return { type: 'DELETE_TASK', payload: id };
}

function reducer(state, action) {
    switch (action.type) {
        case 'ADD_TASK':
            return [...state, action.payload];
        case 'UPDATE_TASK':
            return state.map(task =>
                task.id === action.payload.id ? action.payload : task
            );
        case 'DELETE_TASK':
            return state.filter(task => task.id !== action.payload);
        default:
            return state;
    }
}