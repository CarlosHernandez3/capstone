import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import ApplicantList from './components/ApplicantList';
import ApplicantDashboard from './components/ApplicantDashboard';
import { Applicant } from './types';
import { getApplicants } from './services/apiService';

const App: React.FC = () => {
  const [applicants, setApplicants] = useState<Applicant[]>([]);
  const [selectedApplicant, setSelectedApplicant] = useState<Applicant | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadApplicants();
  }, []);

  const loadApplicants = async () => {
    try {
      setIsLoading(true);
      const data = await getApplicants();
      setApplicants(data);
      setError(null);
    } catch (err) {
      console.error('Failed to load applicants:', err);
      setError('Failed to load applicants from server');
      setApplicants([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectApplicant = (id: string) => {
    const applicant = applicants.find(a => a.id === id);
    if (applicant) {
      setSelectedApplicant(applicant);
    }
  };

  const handleBackToList = () => {
    setSelectedApplicant(null);
  };

  const handleAddApplicant = (newApplicant: Applicant) => {
    setApplicants(prev => [...prev, newApplicant]);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-neutral-100 font-sans text-neutral-800">
        <Header />
        <main className="container mx-auto p-4 md:p-8">
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <svg 
                className="animate-spin h-12 w-12 text-primary mx-auto mb-4" 
                xmlns="http://www.w3.org/2000/svg" 
                fill="none" 
                viewBox="0 0 24 24"
              >
                <circle 
                  className="opacity-25" 
                  cx="12" 
                  cy="12" 
                  r="10" 
                  stroke="currentColor" 
                  strokeWidth="4"
                />
                <path 
                  className="opacity-75" 
                  fill="currentColor" 
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              <p className="text-neutral-600">Loading applicants...</p>
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-100 font-sans text-neutral-800">
      <Header />
      <main className="container mx-auto p-4 md:p-8">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-lg mb-6">
            <p className="font-medium">{error}</p>
            <button 
              onClick={loadApplicants}
              className="mt-2 text-sm underline hover:no-underline"
            >
              Try again
            </button>
          </div>
        )}
        
        {selectedApplicant ? (
          <ApplicantDashboard applicant={selectedApplicant} onBack={handleBackToList} />
        ) : (
          <ApplicantList
            applicants={applicants}
            onSelectApplicant={handleSelectApplicant}
            onAddApplicant={handleAddApplicant}
          />
        )}
      </main>
    </div>
  );
};

export default App;
