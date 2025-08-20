# ideal_completion.py

import numpy as np
import heapq

def produce_vocab(L):
    return [f't{i+1}' for i in range(L)]

def construct_sentence_iddfs(vocab, transition_matrix, depth_limit):
    nodes_traversed = 0
    best_sequence = []
    best_score = -np.inf

    # Map words to indices
    word_to_index = {word: idx for idx, word in enumerate(vocab)}
    
    def dfs(current_word, depth, sequence, score):
        nonlocal nodes_traversed, best_sequence, best_score
        nodes_traversed += 1

        if depth == depth_limit:
            # Add <End>
            idx = word_to_index[current_word]
            end_prob = transition_matrix[idx, -1]  # From current word to <End>
            total_score = score * end_prob
            if total_score > best_score:
                best_sequence = sequence + ['<End>']
                best_score = total_score
            return

        idx = word_to_index[current_word]

        for next_idx, next_word in enumerate(vocab):
            trans_prob = transition_matrix[idx, next_idx]
            if trans_prob > 0:
                dfs(next_word, depth + 1, sequence + [next_word], score * trans_prob)

    # Start from <Start>
    start_probs = transition_matrix[-2, :-1]  # From <Start> to vocab words
    for depth in range(1, depth_limit + 1):
        for idx, prob in enumerate(start_probs):
            if prob > 0:
                word = vocab[idx]
                dfs(word, 1, ['<Start>', word], prob)

    if best_sequence:
        return (best_sequence, best_score), nodes_traversed
    else:
        return ([], 0.0), nodes_traversed

def construct_sentence_ucs(vocab, transition_matrix, n):
    nodes_traversed = 0    
    pq = []
    # Start from <Start>
    start_probs = transition_matrix[-2, :-1]  # From <Start> to vocab words
    for idx, prob in enumerate(start_probs):
        if prob > 0:
            cost = -np.log(prob)
            heapq.heappush(pq, (cost, ['<Start>', vocab[idx]], idx))

    while pq:
        nodes_traversed += 1
        cost, sequence, idx = heapq.heappop(pq)
        depth = len(sequence) - 1  # Exclude <Start>
        if depth == n:
            end_prob = transition_matrix[idx, -1]  # From current word to <End>
            if end_prob > 0:
                total_cost = cost - np.log(end_prob)
                total_score = np.exp(-total_cost)
                return sequence + ['<End>'], total_score, nodes_traversed
        for next_idx, next_word in enumerate(vocab):
            trans_prob = transition_matrix[idx, next_idx]
            if trans_prob > 0:
                new_cost = cost - np.log(trans_prob)
                heapq.heappush(pq, (new_cost, sequence + [next_word], next_idx))

    return [], 0.0, nodes_traversed

def construct_sentence_greedy(vocab, transition_matrix, n):
    nodes_encountered = 0
    sequence = ['<Start>']
    total_score = 1.0
    idx = -2  # Start from <Start>
    for _ in range(n):
        nodes_encountered += 1
        probs = transition_matrix[idx, :-1]  # Exclude <End>
        if np.all(probs == 0):
            break
        next_idx = np.argmax(probs)
        next_word = vocab[next_idx]
        trans_prob = probs[next_idx]
        sequence.append(next_word)
        total_score *= trans_prob
        idx = next_idx
    # Add <End>
    end_prob = transition_matrix[idx, -1]
    total_score *= end_prob
    sequence.append('<End>')
    return sequence, total_score, nodes_encountered

def construct_sentence_astar(vocab, transition_matrix, n):
    nodes_tally = 0

    def heuristic(depth):
        return 0  # Heuristic can be zero

    pq = []
    # Start from <Start>
    start_probs = transition_matrix[-2, :-1]  # From <Start> to vocab words
    for idx, prob in enumerate(start_probs):
        if prob > 0:
            cost = -np.log(prob)
            est_total_cost = cost + heuristic(1)
            heapq.heappush(pq, (est_total_cost, cost, ['<Start>', vocab[idx]], idx))

    while pq:
        nodes_tally += 1
        est_total_cost, cost_so_far, sequence, idx = heapq.heappop(pq)
        depth = len(sequence) - 1  # Exclude <Start>
        if depth == n:
            end_prob = transition_matrix[idx, -1]  # From current word to <End>
            if end_prob > 0:
                total_cost = cost_so_far - np.log(end_prob)
                total_score = np.exp(-total_cost)
                return sequence + ['<End>'], total_score, nodes_tally
        for next_idx, next_word in enumerate(vocab):
            trans_prob = transition_matrix[idx, next_idx]
            if trans_prob > 0:
                new_cost = cost_so_far - np.log(trans_prob)
                est_total_cost = new_cost + heuristic(depth + 1)
                heapq.heappush(pq, (est_total_cost, new_cost, sequence + [next_word], next_idx))

    return [], 0.0, nodes_tally