from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import random
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

class NQueensGenetic:
    def __init__(self, N, population_size=100, mutation_rate=0.1):
        self.N = N
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.population = [self.random_board() for _ in range(population_size)]
        self.solution = None

    def random_board(self):
        
        return [random.randint(0, self.N - 1) for _ in range(self.N)]

    def fitness(self, board):
        
        non_attacking_pairs = 0
        for i in range(self.N):
            for j in range(i + 1, self.N):
                if board[i] != board[j] and abs(board[i] - board[j]) != abs(i - j):
                    non_attacking_pairs += 1
        return non_attacking_pairs

    def select_parents(self):
        
        weights = [self.fitness(board) for board in self.population]
        return random.choices(self.population, weights=weights, k=2)

    def crossover(self, parent1, parent2):
        
        crossover_point = random.randint(1, self.N - 1)
        child = parent1[:crossover_point] + parent2[crossover_point:]
        return child

    def mutate(self, board):
        
        if random.random() < self.mutation_rate:
            board[random.randint(0, self.N - 1)] = random.randint(0, self.N - 1)
        return board

    def run(self, max_generations=1000):
        for generation in range(max_generations):
            new_population = []
            for _ in range(self.population_size):
                parent1, parent2 = self.select_parents()
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                new_population.append(child)
                
                socketio.emit('update', {'board': child, 'generation': generation})
                time.sleep(0.05)  

                
                if self.fitness(child) == (self.N * (self.N - 1)) // 2:
                    self.solution = child
                    return

            self.population = new_population

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('solve')
def handle_solve(data):
    N = int(data.get('N', 8))
    nqueens = NQueensGenetic(N)
    nqueens.run()
    if nqueens.solution:
        emit('solution', {'board': nqueens.solution})
    emit('complete', {'solution_found': bool(nqueens.solution)})

if __name__ == '__main__':
    socketio.run(app, debug=True)
