import React, { useState } from 'react';
import Editor from '@monaco-editor/react';
import './CodeEditor.css';

const CodeEditor = () => {
  const [code, setCode] = useState('# Code here\nprint("Hello, World!")');
  const [output, setOutput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleEditorChange = (value) => {
    setCode(value);
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

      console.log('Raw response:', response); // 调试日志

      const data = await response.json();
      console.log('Response data:', data);

      if (data.error == null) {
        setOutput(data.output);
      } else {
        setError(data.error);
        console.log('data.error:', data.error);
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
        <h2>Python 代码编辑器</h2>
        <Editor
          height="400px"
          defaultLanguage="python"
          defaultValue={code}
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
        <button 
          className="execute-button" 
          onClick={executeCode}
          disabled={isLoading}
        >
          {isLoading ? '执行中...' : '执行代码'}
        </button>
      </div>
      <div className="output-section">
        <h2>执行结果</h2>
        <div className="output-container">
          {error ? (
            <div className="error-message">
              <h3>错误信息:</h3>
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
