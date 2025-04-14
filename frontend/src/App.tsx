import { useState, useRef } from 'react';
import './App.css';
import CodeEditor from './components/CodeEditor';
import Question from './components/Question';

function App() {
  const [questionPanelWidth, setQuestionPanelWidth] = useState(50); // Percentage
  const mainContentRef = useRef<HTMLDivElement>(null);
  const resizeHandleRef = useRef<HTMLDivElement>(null);

  const startResizing = (e: React.MouseEvent) => {
    e.preventDefault();
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', stopResizing);
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (mainContentRef.current) {
      const mainWidth = mainContentRef.current.offsetWidth;
      const newWidth = (e.clientX - mainContentRef.current.offsetLeft) / mainWidth * 100;
      // Constrain width between 20% and 80%
      setQuestionPanelWidth(Math.max(20, Math.min(80, newWidth)));
    }
  };

  const stopResizing = () => {
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', stopResizing);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Python Online Testing Platform</h1>
      </header>
      <main className="main-content" ref={mainContentRef}>
        <div className="questions-panel" style={{ flex: `0 0 ${questionPanelWidth}%` }}>
          <Question />
        </div>
        <div
          className="resize-handle"
          ref={resizeHandleRef}
          onMouseDown={startResizing}
        />
        <div className="editor-panel">
          <CodeEditor />
        </div>
      </main>
      <footer>
        <p>Python Online Testing Platform © {new Date().getFullYear()}</p>
      </footer>
    </div>
  );
}

export default App;