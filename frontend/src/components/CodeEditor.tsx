import { useState, useEffect, useRef } from 'react';
import Editor from '@monaco-editor/react';
import './CodeEditor.css';
import * as diff from 'diff';

// 定义全局变量 captureInterval，用于控制代码捕获的时间间隔（单位：毫秒）
const captureInterval = 30000;

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
  const lastEditTimeRef = useRef<number>(Date.now());

  const handleEditorChange = (value: string | undefined) => {
    if (value !== undefined) {
      setCode(value);
      codeRef.current = value;
    }
  };

  // 获取代码变化情况并处理为日志格式
  const processCodeDifferences = (previousCode: string, currentCode: string, elapsedTime: number) => {
    const differences = diff.diffLines(previousCode, currentCode);
    return {
      timestamp: new Date().toISOString(),
      elapsedTime,
      changes: differences.map((part) => ({
        type: part.added ? 'added' : part.removed ? 'removed' : 'unchanged',
        value: part.value,
        count: part.count,
      })),
    };
  };

  // 捕获代码变化并发送日志
  const captureCodeChanges = async () => {
    const currentTime = Date.now();
    const timeDifference = currentTime - lastEditTimeRef.current; // 用户编辑所用时间（单位：毫秒）
    const logMessages = processCodeDifferences(previousCodeRef.current, codeRef.current, timeDifference);
    try {
      const response = await fetch('http://localhost:8000/api/track_event', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 'test_user',
          question_id: currentQuestion?.id.toString() || 'unknown',
          event_type: 'edit',
          payload: logMessages,
          question_name: currentQuestion?.title || 'unknown',
          question_desc: currentQuestion?.description || 'unknown',
          example_input: currentQuestion?.example_input || 'unknown',
          example_output: currentQuestion?.example_output || 'unknown',
          elapsed_time: logMessages.elapsedTime,
          code_diff: logMessages.changes
        }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log('Received edit data from track_event API:', data);
    } catch (err) {
      console.error('Error sending log to API:', err);
    }
    console.log('Code changes logged:', logMessages);
    previousCodeRef.current = codeRef.current;
    lastEditTimeRef.current = currentTime; // 更新上一次编辑时间
  };

  // 当编辑器挂载时，开始使用定时器捕获代码变化
  const handleEditorDidMount = (editor: any) => {
    // 使用全局变量 captureInterval
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    intervalRef.current = setInterval(captureCodeChanges, captureInterval);
  };


  // 提交代码并停止捕获
  const submitCode = async () => {
    // 立刻提交代码，并停止捕获
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    captureCodeChanges();
    console.log({
      user_id: 'test_user',
      question_id: currentQuestion?.id.toString() || 'unknown',
      event_type: 'submit',
    })

    try {
      const response = await fetch('http://localhost:8000/api/track_event', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 'test_user',
          question_id: currentQuestion?.id.toString() || 'unknown',
          event_type: 'submit',
          payload: {},
          question_name: currentQuestion?.title || 'unknown',
          question_desc: currentQuestion?.description || 'unknown',
          example_input: currentQuestion?.example_input || 'unknown',
          example_output: currentQuestion?.example_output || 'unknown',
          elapsed_time: 0,
          code_diff: []
        }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log('Event received:', data);
    } catch (err) {
      console.error('Error sending log to API:', err);
    }
  }

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
        <button className="submit-button" onClick={submitCode} disabled={isLoading}>
          {isLoading ? 'Submitting...' : 'Submit Code'}
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