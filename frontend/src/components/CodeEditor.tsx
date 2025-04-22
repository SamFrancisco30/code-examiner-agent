import { useState, useEffect, useRef } from 'react';
import Editor from '@monaco-editor/react';
import './CodeEditor.css';
import * as diff from 'diff';

interface Question {
  id: number;
  title: string;
  description: string;
  example_input: string;
  example_output: string;
}

interface CodeEditorProps {
  initialCode?: string;
  currentQuestion: Question | null;
}

const CodeEditor: React.FC<CodeEditorProps> = ({
  initialCode = '# Code here\nprint("Hello, World!")',
  currentQuestion,
}) => {
  const [code, setCode] = useState(initialCode);
  const [output, setOutput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const previousCodeRef = useRef<string>(initialCode);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const codeRef = useRef<string>(initialCode);

  const handleEditorChange = (value: string | undefined) => {
    if (value !== undefined) {
      setCode(value);
      codeRef.current = value;
    }
  };

  const processCodeDifferences = (previousCode: string, currentCode: string, interval: number) => {
    const differences = diff.diffLines(previousCode, currentCode);
    const elapsedSeconds = interval / 1000;

    return {
      timestamp: new Date().toISOString(),
      elapsedSeconds,
      changes: differences.map((part) => ({
        type: part.added ? 'added' : part.removed ? 'removed' : 'unchanged',
        value: part.value,
        count: part.count,
      })),
    };
  };

  const handleEditorDidMount = (editor: any) => {
    const captureInterval = 30000;
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    intervalRef.current = setInterval(async () => {
      const logMessages = processCodeDifferences(previousCodeRef.current, codeRef.current, captureInterval);
      try {
        const response = await fetch('http://localhost:8000/api/track_event', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: 'test_user',
            question_id: currentQuestion?.id.toString() || 'unknown', // Use currentQuestion.id
            event_type: 'code_edit',
            payload: logMessages,
          }),
        });
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (data.status === 'ok') {
          console.log('Event successfully received, backend message:', data.message);
        } else {
          console.warn('Backend returned non-success status:', data.message);
        }
      } catch (err) {
        console.error('Error sending log to API:', err);
      }
      console.log('Code changes logged:', logMessages);
      previousCodeRef.current = codeRef.current;
    }, captureInterval);
  };

  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  const executeCode = async () => {
    setIsLoading(true);
    setOutput('');
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code }),
      });

      const data = await response.json();

      if (data.error == null) {
        setOutput(data.output);
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError('Unable to connect to the server, please check if the backend service is running');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="code-editor-container">
      <div className="editor-section">
        <Editor
          height="50vh"
          defaultLanguage="python"
          value={code}
          onChange={handleEditorChange}
          onMount={handleEditorDidMount}
          theme="vs-dark"
          options={{
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            fontSize: 14,
            tabSize: 4,
            automaticLayout: true,
          }}
        />
      </div>
      <div className="button-section">
        <button className="execute-button" onClick={executeCode} disabled={isLoading}>
          {isLoading ? 'Executing...' : 'Execute Code'}
        </button>
      </div>
      <div className="output-section">
        <div className="output-container">
          {error ? (
            <div className="error-message">
              <pre>{error}</pre>
            </div>
          ) : (
            <pre>{output || 'Click "Execute Code" to run your code'}</pre>
          )}
        </div>
      </div>
    </div>
  );
};

export default CodeEditor;