import { useLocation } from 'react-router-dom';

interface ResultPageProps {}

const ResultPage: React.FC<ResultPageProps> = () => {
  const location = useLocation();
  const data = location.state?.data;

  return (
    <div>
      <h1>LLMFeedBack</h1>
      {data ? (
        <div>
          {data.summary && (
            <div>
              <h2>Summary</h2>
              <p>{data.summary}</p>
            </div>
          )}
          {data.suggestions && data.suggestions.length > 0 && (
            <div>
              <h2>Suggestions</h2>
              <ul>
{data.suggestions.map((suggestion: string, index: number) => (
                  <li key={index}>{suggestion}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ) : (
        <p>No date</p>
      )}
    </div>
  );
};

export default ResultPage;