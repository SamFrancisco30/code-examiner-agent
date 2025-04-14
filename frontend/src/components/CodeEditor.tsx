import { useState } from 'react';
import Editor from '@monaco-editor/react';
import './CodeEditor.css';

interface CodeEditorProps {
  initialCode?: string;
}

const CodeEditor: React.FC<CodeEditorProps> = ({ initialCode = '# Code here\nprint("Hello, World!")' }) => {
  const [code, setCode] = useState(initialCode);
  const [output, setOutput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleEditorChange = (value: string | undefined) => {
    if (value !== undefined) {
      setCode(value);
    }
  };

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
      setError('无法连接到服务器，请检查后端服务是否运行');
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
        <button 
          className="execute-button" 
          onClick={executeCode}
          disabled={isLoading}
        >
          {isLoading ? '执行中...' : '执行代码'}
        </button>
      </div>
      <div className="output-section">
        <div className="output-container">
          {error ? (
            <div className="error-message">
              <pre>{error}</pre>
            </div>
          ) : (
            <pre>{output || '点击"执行代码"按钮运行您的代码'}</pre>
          )}
        </div>
      </div>
    </div>
  );
};

export default CodeEditor;