import { useState, useEffect, useRef } from 'react';
import Editor from '@monaco-editor/react';
import './CodeEditor.css';
// 导入 diff 库
import * as diff from 'diff';

interface CodeEditorProps {
  initialCode?: string;
}

const CodeEditor: React.FC<CodeEditorProps> = ({ initialCode = '# Code here\nprint("Hello, World!")' }) => {
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

  /**
   * 处理代码差异并生成规范化输出
   * @param previousCode - 之前的代码
   * @param currentCode - 当前的代码
   * @param interval - 代码捕捉间隔，单位为毫秒
   * @returns 包含标准化差异信息的对象
   */
  const processCodeDifferences = (previousCode: string, currentCode: string, interval: number) => {
    const differences = diff.diffLines(previousCode, currentCode);
    const elapsedSeconds = interval / 1000;

    return {
      timestamp: new Date().toISOString(),
      elapsedSeconds,
      changes: differences.map(part => ({
        type: part.added ? 'added' : part.removed ? 'removed' : 'unchanged',
        value: part.value,
        count: part.count
      }))
    };
  };

  const handleEditorDidMount = (editor: any) => {
    const captureInterval = 30000; 
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    intervalRef.current = setInterval(() => {
      if (previousCodeRef.current !== codeRef.current) {
        const logMessages = processCodeDifferences(previousCodeRef.current, codeRef.current, captureInterval);
        // 修改日志输出方式
        console.log('代码变化记录：', logMessages);
        previousCodeRef.current = codeRef.current;
      } else {
        console.log('代码未发生变化');
      }
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