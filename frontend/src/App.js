import React from 'react';
import './App.css';
import CodeEditor from './components/CodeEditor';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Python 代码在线执行系统</h1>
        <p>在编辑器中编写 Python 代码，点击执行按钮运行</p>
      </header>
      <main>
        <CodeEditor />
      </main>
      <footer>
        <p>Python 代码在线执行系统 &copy; {new Date().getFullYear()}</p>
      </footer>
    </div>
  );
}

export default App;
