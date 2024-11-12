// static/script.js
document.getElementById('solve-button').addEventListener('click', async () => {
    const nInput = document.getElementById('n-input').value;
    const response = await fetch('/solve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ N: nInput })
    });

    const data = await response.json();
    if (data.error) {
        alert(data.error);
    } else {
        displaySolutions(data.solutions, nInput);
    }
});

function displaySolutions(solutions, n) {
    const container = document.getElementById('solution-container');
    container.innerHTML = '';
    solutions.forEach(solution => {
        const board = document.createElement('div');
        board.className = 'chessboard';
        board.style.setProperty('--n', n);
        solution.forEach((col, row) => {
            for (let i = 0; i < n; i++) {
                const cell = document.createElement('div');
                cell.className = `cell ${((row + i) % 2 === 0) ? 'white' : 'black'}`;
                if (i === col) {
                    const queen = document.createElement('span');
                    queen.className = 'queen';
                    queen.textContent = '♛';
                    cell.appendChild(queen);
                }
                board.appendChild(cell);
            }
        });
        container.appendChild(board);
    });
}
