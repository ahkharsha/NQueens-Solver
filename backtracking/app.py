from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

class NQueens:
    def __init__(self, N):
        self.N = N
        self.board = [-1] * N
        self.solution_count = 0
        self.tree = {'name': 'Start', 'children': []}  
        self.current_path = [self.tree]  

    def is_safe(self, row, col):
        
        for i in range(row):
            if self.board[i] == col or abs(self.board[i] - col) == abs(i - row):
                return False
        return True

    def solve_recursive(self, row=0, level=0):
        if row == self.N:
            
            self.solution_count += 1
            solution_node = {'name': f'Solution-{self.solution_count}', 'children': [], 'isSolution': True}
            self.current_path[-1]['children'].append(solution_node)  

            socketio.emit('solution', {'board': self.board, 'solution_count': self.solution_count})
            socketio.emit('update', {
                'board': self.board, 
                'row': row, 
                'col': -1,  
                'level': level,
                'isPruned': False,
                'tree': self.tree
            })
            time.sleep(1)  
            return

        
        for col in range(self.N):
            if self.is_safe(row, col):
                
                self.board[row] = col
                node = {'name': f'R{row}C{col}', 'children': []}  
                self.current_path[-1]['children'].append(node)  
                self.current_path.append(node)  

                
                socketio.emit('update', {
                    'board': self.board, 
                    'row': row, 
                    'col': col, 
                    'level': level, 
                    'isPruned': False,
                    'tree': self.tree  
                })
                time.sleep(0.01)

                
                self.solve_recursive(row + 1, level + 1)

                
                self.board[row] = -1
                self.current_path.pop()  
                socketio.emit('update', {
                    'board': self.board, 
                    'row': row, 
                    'col': col, 
                    'level': level, 
                    'isPruned': False,
                    'tree': self.tree  
                })
                time.sleep(0.01)
            else:
                
                pruned_node = {'name': f'R{row}C{col}', 'children': [], 'isPruned': True}
                self.current_path[-1]['children'].append(pruned_node)  

                
                socketio.emit('update', {
                    'board': self.board, 
                    'row': row, 
                    'col': col, 
                    'level': level, 
                    'isPruned': True,
                    'tree': self.tree  
                })
                time.sleep(0.01)

    def get_tree(self):
        
        return self.tree

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('solve')
def handle_solve(data):
    N = int(data.get('N', 8))
    nqueens = NQueens(N)
    nqueens.solve_recursive()
    
    emit('complete', {
        'solution_count': nqueens.solution_count,
        'tree': nqueens.get_tree()
    })

if __name__ == '__main__':
    socketio.run(app, debug=True)
