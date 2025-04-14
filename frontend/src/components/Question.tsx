import { useState, useEffect } from 'react';
import { supabase } from './Supabase';
import './Question.css';


interface Question {
  id: number;
  title: string;
  description: string;
  example_input: string;
  example_output: string;
}

const Questions = () => {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        const { data, error } = await supabase.from('questions').select('*');
        if (error) {
          throw new Error(error.message);
        }
        console.log('Fetched questions:', data); // Log the fetched questions
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

  if (loading) return <div className="loading">Loading questions...</div>;
  if (error) return <div className="error">Error: {error}</div>;

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
                console.log('Selected question:', question); // Log the selected question
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