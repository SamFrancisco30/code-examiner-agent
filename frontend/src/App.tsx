import './App.css';
import CodeEditor from './components/CodeEditor';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Python Online Testing Platform</h1>
      </header>
      <main>
        <CodeEditor />
      </main>
      <footer>
        <p>Python Online Testing Platform &copy; {new Date().getFullYear()}</p>
      </footer>
    </div>
  );
}

export default App;
