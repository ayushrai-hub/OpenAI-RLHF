import numpy as np
import random
from scipy.fftpack import idct

def dct_to_pixel(dct_coeffs, quantization_table, original_shape):
    # Reshape the DCT coefficients back to 8x8 blocks
    height, width = original_shape
    blocks_height = height // 8
    blocks_width = width // 8
    
    # Reshape to 8x8 blocks
    dct_blocks = dct_coeffs.reshape(blocks_height, 8, blocks_width, 8)
    
    # Dequantize the coefficients
    dequantized_blocks = dct_blocks * quantization_table
    
    # Perform inverse DCT (iDCT) on each block
    def idct_2d(block):
        return idct(idct(block, axis=0, norm='ortho'), axis=1, norm='ortho')
    
    # Apply the iDCT to each 8x8 block
    idct_blocks = np.array([[idct_2d(block) for block in row] for row in dequantized_blocks])
    
    # Rearrange the blocks back into the full image
    idct_image = idct_blocks.transpose(0, 2, 1, 3).reshape(height, width)
    
    return idct_image

def modify_coefficients(X_p, combined_message, chromosome, modify_indices):
    X_p_modified = X_p.copy()
    for i, gene in enumerate(chromosome):
        index = modify_indices[i]
        coefficient = X_p[index]
        secret_bit = int(combined_message[i % len(combined_message)])
        represented_bit = 1 if (coefficient > 0 and coefficient % 2 == 0) or (coefficient < 0 and coefficient % 2 != 0) else 0

        if secret_bit != represented_bit:
            direction = 1 if gene == 1 else -1
            new_coefficient = coefficient + direction
            # Adjust coefficient until it represents the correct bit
            while new_coefficient == 0 or ((new_coefficient > 0 and new_coefficient % 2 == 0) or (new_coefficient < 0 and new_coefficient % 2 != 0)) != secret_bit:
                new_coefficient += direction
            X_p_modified[index] = new_coefficient

    return X_p_modified

def genetic_algorithm(Lc, X_p, combined_message, modify_indices, quantization_table, original_shape):
    population_size = 20
    generations = 100
    mutation_rate = 0.01
    crossover_rate = 0.6

    def initialize_population():
        population = []
        for _ in range(population_size):
            chromosome = []
            for i in range(Lc):
                coefficient = X_p[modify_indices[i]]
                secret_bit = int(combined_message[i % len(combined_message)])
                represented_bit = 1 if (coefficient > 0 and coefficient % 2 == 0) or (coefficient < 0 and coefficient % 2 != 0) else 0

                # Ensure that the chromosome correctly embeds the secret bit
                if secret_bit == represented_bit:
                    gene = 0  # No change needed
                else:
                    gene = 1 if coefficient != 0 else -1  # Increment or decrement based on the required bit
                chromosome.append(gene)
            population.append(chromosome)
        return population

    def calculate_fitness(chromosome):
        # Apply the chromosome modifications to the coefficients
        X_p_modified = modify_coefficients(X_p, combined_message, chromosome, modify_indices)
        
        # Convert DCT coefficients back to pixel values
        original_pixels = dct_to_pixel(X_p, quantization_table, original_shape)
        stego_pixels = dct_to_pixel(X_p_modified, quantization_table, original_shape)
        
        # Calculate blockiness
       # B_original = calculate_blockiness(original_pixels)
        #B_stego = calculate_blockiness(stego_pixels)
        
        # Fitness is the inverse of the Ratio of Blockiness (ROB)
        ROB = B_stego / B_original
        fitness_score = 1 / ROB
        
        return fitness_score

    def select_parents(population, fitness_scores):
        sorted_pop_and_fitness = sorted(zip(fitness_scores, population), key=lambda pair: pair[0], reverse=True)
        sorted_population = [x for _, x in sorted_pop_and_fitness]
        best_individual = sorted_population[0]
        ranks = np.arange(1, len(population) + 1)
        rank_sum = np.sum(ranks)
        probabilities = (len(population) - ranks + 1) / rank_sum
        parents_indices = np.random.choice(np.arange(len(population)), size=len(population)-1, p=probabilities)
        selected_parents = [sorted_population[i] for i in parents_indices]
        return selected_parents, best_individual

    def crossover(parent1, parent2):
        if np.random.rand() < crossover_rate:
            crossover_point = np.random.randint(1, Lc - 1)
            child1 = parent1[:crossover_point] + parent2[crossover_point:]
            child2 = parent2[:crossover_point] + parent1[crossover_point:]
            return child1, child2
        else:
            return parent1, parent2

    def mutate(chromosome):
        for i in range(Lc):
            if np.random.rand() < mutation_rate:
                chromosome[i] *= -1  # Flip the direction
        return chromosome

    population = initialize_population()
    best_overall = None
    best_fitness_overall = float('-inf')

    for generation in range(generations):
        fitness_scores = [calculate_fitness(chromosome) for chromosome in population]

        current_best_index = np.argmax(fitness_scores)
        current_best_chromosome = population[current_best_index]
        current_best_fitness = fitness_scores[current_best_index]

        if current_best_fitness > best_fitness_overall:
            best_overall = current_best_chromosome
            best_fitness_overall = current_best_fitness
            print(f"Generation {generation+1}, Best fitness: {best_fitness_overall:.6f}")

        selected_parents, best_individual = select_parents(population, fitness_scores)
        new_population = [best_individual]  # Start new population with the best individual

        while len(new_population) < population_size:
            parent1, parent2 = random.sample(selected_parents, 2)
            child1, child2 = crossover(parent1, parent2)
            child1 = mutate(child1)
            child2 = mutate(child2)
            new_population.extend([child1, child2])

        new_population = new_population[:population_size]  # Ensure population size remains constant
        population = new_population

    print(f"Done! Best fitness: {best_fitness_overall:.6f}")
    best_chromosome = best_overall
    return best_chromosome
