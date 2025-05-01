import { useState, useRef, useEffect } from 'react';
import './App.css';
import CodeEditor from './components/CodeEditor';
import Question from './components/Question';
import { supabase } from './components/Supabase';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ResultPage from './components/ResultPage';

interface Question {
  id: number;
  title: string;
  description: string;
  example_input: string;
  example_output: string;
}

function App() {
  const [questionPanelWidth, setQuestionPanelWidth] = useState(50); // Percentage
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const mainContentRef = useRef<HTMLDivElement>(null);
  const resizeHandleRef = useRef<HTMLDivElement>(null);

  // Fetch questions from Supabase
  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        const { data, error } = await supabase.from('questions').select('*');
        if (error) {
          throw new Error(error.message);
        }
        setQuestions(data);
        if (data.length > 0) {
          setCurrentQuestion(data[0]);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchQuestions();
  }, []);

  const startResizing = (e: React.MouseEvent) => {
    e.preventDefault();
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', stopResizing);
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (mainContentRef.current) {
      const mainWidth = mainContentRef.current.offsetWidth;
      const newWidth = (e.clientX - mainContentRef.current.offsetLeft) / mainWidth * 100;
      setQuestionPanelWidth(Math.max(20, Math.min(80, newWidth)));
    }
  };

  const stopResizing = () => {
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', stopResizing);
  };

  if (loading) return <div>Loading questions...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>Python Online Testing Platform</h1>
        </header>
        <Routes>
          <Route path="/" element={
            <main className="main-content" ref={mainContentRef}>
              <div className="questions-panel" style={{ flex: `0 0 ${questionPanelWidth}%` }}>
                <Question
                  questions={questions}
                  currentQuestion={currentQuestion}
                  setCurrentQuestion={setCurrentQuestion}
                />
              </div>
              <div
                className="resize-handle"
                ref={resizeHandleRef}
                onMouseDown={startResizing}
              />
              <div className="editor-panel">
                <CodeEditor currentQuestion={currentQuestion} />
              </div>
            </main>
          } />
          <Route path="/result" element={
            <main className="main-content" ref={mainContentRef}>
              <div className="questions-panel" style={{ flex: `0 0 ${questionPanelWidth}%` }}>
                <Question
                  questions={questions}
                  currentQuestion={currentQuestion}
                  setCurrentQuestion={setCurrentQuestion}
                />
              </div>
              <div
                className="resize-handle"
                ref={resizeHandleRef}
                onMouseDown={startResizing}
              />
              <div className="editor-panel">
                <ResultPage />
              </div>
            </main>
          } />
        </Routes>
        <footer>
          <p>Python Online Testing Platform © {new Date().getFullYear()}</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;