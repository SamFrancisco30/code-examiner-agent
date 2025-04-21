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
    intervalRef.current = setInterval(async () => {
      if (previousCodeRef.current !== codeRef.current) {
        const logMessages = processCodeDifferences(previousCodeRef.current, codeRef.current, captureInterval);
        try {
          // 发送日志数组到指定接口
          const response = await fetch('http://localhost:8000/api/track_event', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              user_id: 'test_user', // 替换为实际的 user_id
              question_id: 'test_question', // 替换为实际的 question_id
              event_type: 'code_edit', // 替换为实际的 event_type
              payload: logMessages
            }),
          });
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }

          const data = await response.json();
          if (data.status === 'ok') {
            console.log('事件已成功接收，后端消息:', data.message);
          } else {
            console.warn('后端返回非成功状态:', data.message);
          }
        } catch (err) {
          console.error('发送日志到 API 时出错:', err);
        }
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