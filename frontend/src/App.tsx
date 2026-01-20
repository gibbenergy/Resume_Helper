import { MainLayout } from './components/layout/MainLayout';
import './App.css';

function App() {
  try {
    return <MainLayout />;
  } catch (error) {
    console.error('Error in App component:', error);
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Error Loading App</h1>
          <p className="text-gray-700">{error instanceof Error ? error.message : 'Unknown error'}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded"
          >
            Reload
          </button>
        </div>
      </div>
    );
  }
}

export default App;

 
