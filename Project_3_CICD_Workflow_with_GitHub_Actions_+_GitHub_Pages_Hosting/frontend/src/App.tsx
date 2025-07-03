import { useState, useEffect } from 'react';
import './App.css';

interface Todo {
  id: number;
  text: string;
  completed: boolean;
}

interface DeploymentInfo {
  version: string;
  buildTime: string;
  commitHash: string;
}

function App() {
  const [deploymentInfo] = useState<DeploymentInfo>({
    version: '1.0.0',
    buildTime: new Date().toISOString(),
    commitHash: process.env.REACT_APP_COMMIT_HASH || 'local-dev'
  });

  const [counter, setCounter] = useState<number>(0);
  const [todos, setTodos] = useState<Todo[]>([]);
  const [newTodo, setNewTodo] = useState<string>('');

  useEffect(() => {
    // Simulate loading saved todos
    const savedTodos = localStorage.getItem('todos');
    if (savedTodos) {
      setTodos(JSON.parse(savedTodos));
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('todos', JSON.stringify(todos));
  }, [todos]);

  const addTodo = () => {
    if (newTodo.trim()) {
      setTodos([...todos, { 
        id: Date.now(), 
        text: newTodo, 
        completed: false 
      }]);
      setNewTodo('');
    }
  };

  const toggleTodo = (id: number) => {
    setTodos(todos.map(todo =>
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ));
  };

  const deleteTodo = (id: number) => {
    setTodos(todos.filter(todo => todo.id !== id));
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🚀 CI/CD Demo Application</h1>
        <p>This app demonstrates automated deployment with GitHub Actions</p>
        
        <div className="deployment-info">
          <h3>Deployment Information</h3>
          <div className="info-grid">
            <span>Version:</span> <code>{deploymentInfo.version}</code>
            <span>Build Time:</span> <code>{deploymentInfo.buildTime}</code>
            <span>Commit:</span> <code>{deploymentInfo.commitHash}</code>
          </div>
        </div>
      </header>

      <main className="App-main">
        <section className="counter-section">
          <h2>Interactive Counter</h2>
          <div className="counter">
            <button onClick={() => setCounter(counter - 1)}>-</button>
            <span className="count">{counter}</span>
            <button onClick={() => setCounter(counter + 1)}>+</button>
          </div>
          <button 
            className="reset-btn" 
            onClick={() => setCounter(0)}
          >
            Reset
          </button>
        </section>

        <section className="todo-section">
          <h2>Todo List</h2>
          <div className="todo-input">
            <input
              type="text"
              value={newTodo}
              onChange={(e) => setNewTodo(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addTodo()}
              placeholder="Enter a new todo..."
            />
            <button onClick={addTodo}>Add</button>
          </div>
          
          <ul className="todo-list">
            {todos.map(todo => (
              <li key={todo.id} className={todo.completed ? 'completed' : ''}>
                <span onClick={() => toggleTodo(todo.id)}>
                  {todo.text}
                </span>
                <button 
                  className="delete-btn"
                  onClick={() => deleteTodo(todo.id)}
                >
                  ×
                </button>
              </li>
            ))}
          </ul>
          
          {todos.length === 0 && (
            <p className="empty-state">No todos yet. Add one above!</p>
          )}
        </section>

        <section className="pipeline-status">
          <h2>Pipeline Features Demonstrated</h2>
          <ul className="feature-list">
            <li>✅ Code linting with ESLint</li>
            <li>✅ Code formatting with Prettier</li>
            <li>✅ Automated testing with Jest</li>
            <li>✅ Security scanning</li>
            <li>✅ Automated deployment to GitHub Pages</li>
            <li>✅ Environment-specific builds</li>
          </ul>
        </section>
      </main>

      <footer className="App-footer">
        <p>🔄 Deployed automatically via GitHub Actions</p>
        <p>Last updated: {new Date().toLocaleString()}</p>
      </footer>
    </div>
  );
}

export default App;
