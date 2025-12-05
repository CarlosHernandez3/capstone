import React, { useState } from 'react';
import Header from './components/Header';
import ApplicantList from './components/ApplicantList';
import ApplicantDashboard from './components/ApplicantDashboard';
import { mockApplicants } from './data/mockData';
import { Applicant } from './types';

const App: React.FC = () => {
  const [selectedApplicant, setSelectedApplicant] = useState<Applicant | null>(null);

  const handleSelectApplicant = (id: string) => {
    const applicant = mockApplicants.find(a => a.id === id);
    if (applicant) {
      setSelectedApplicant(applicant);
    }
  };

  const handleBackToList = () => {
    setSelectedApplicant(null);
  };

  return (
    <div className="min-h-screen bg-neutral-100 font-sans text-neutral-800">
      <Header />
      <main className="container mx-auto p-4 md:p-8">
        {selectedApplicant ? (
          <ApplicantDashboard applicant={selectedApplicant} onBack={handleBackToList} />
        ) : (
          <ApplicantList applicants={mockApplicants} onSelectApplicant={handleSelectApplicant} />
        )}
      </main>
    </div>
  );
};

export default App;
