import './Question.css';

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