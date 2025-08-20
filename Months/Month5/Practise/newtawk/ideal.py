import zmq
import numpy as np
import joblib  # Usato per caricare il modello .pkl

# Carica il modello AI pre-addestrato
model = joblib.load('ai_model.pkl')

# Configura ZeroMQ
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    # Ricevi messaggio da MetaTrader
    message = socket.recv_string()

    # Assumiamo che i dati siano separati da una virgola
    data = np.array([float(x) for x in message.split(',')]).reshape(1, -1)
    
    # Esegui il modello per ottenere segnali
    prediction = model.predict(data)
    
    # Invia risposta a MetaTrader
    socket.send_string(str(prediction[0]))
