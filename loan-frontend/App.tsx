import React, { useState } from 'react';
import Header from './components/Header';
import ApplicantList from './components/ApplicantList';
import ApplicantDashboard from './components/ApplicantDashboard';
import { mockApplicants } from './data/mockData';
import { Applicant } from './types';

const App: React.FC = () => {
  const [applicants, setApplicants] = useState<Applicant[]>(mockApplicants);
  const [selectedApplicant, setSelectedApplicant] = useState<Applicant | null>(null);

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

  return (
    <div className="min-h-screen bg-neutral-100 font-sans text-neutral-800">
      <Header />
      <main className="container mx-auto p-4 md:p-8">
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
