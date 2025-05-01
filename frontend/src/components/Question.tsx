import './Question.css';
import { useNavigate } from 'react-router-dom';

interface Question {
  id: number;
  title: string;
  description: string;
  example_input: string;
  example_output: string;
}

interface QuestionsProps {
  questions: Question[];
  currentQuestion: Question | null;
  setCurrentQuestion: (question: Question) => void;
}

const Questions: React.FC<QuestionsProps> = ({ questions, currentQuestion, setCurrentQuestion }) => {
  const navigate = useNavigate();

  const clearDatabase = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/track_event', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 'test_user',
          question_id: currentQuestion?.id.toString() || 'unknown',
          event_type: 'start',
          payload: {},
          question_name: currentQuestion?.title || 'unknown',
          question_desc: currentQuestion?.description || 'unknown',
          example_input: currentQuestion?.example_input || 'unknown',
          example_output: currentQuestion?.example_output || 'unknown',
          elapsed_time: 0,
          code_diff: [],
        }),
      });
      const data = await response.json();
      console.log('Received edit data from track_event API:', data);
    } catch (err) {
      console.error('Error sending log to API:', err);
    }
  }

  return (
    <div className="questions-container">
      <div className="questions-list">
        <h3>Problems</h3>
        <ul>
          {questions.map((question) => (
            <li
              key={question.id}
              className={currentQuestion?.id === question.id ? 'active' : ''}
              onClick={() => {
                console.log('Selected question:', question);
                setCurrentQuestion(question);
                // 导航到根路径
                navigate('/'); 
                // clearDatabase();
              }}
            >
              {question.title}
            </li>
          ))}
        </ul>
      </div>
      {currentQuestion && (
        <div className="question-detail">
          <h2>{currentQuestion.title}</h2>
          <div className="description" dangerouslySetInnerHTML={{ __html: currentQuestion.description }} />
          <h3>Example:</h3>
          <div className="example">
            <p>Input:</p>
            <pre>{currentQuestion.example_input}</pre>
            <p>Output:</p>
            <pre>{currentQuestion.example_output}</pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default Questions;