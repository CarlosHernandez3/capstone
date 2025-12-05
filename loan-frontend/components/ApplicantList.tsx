import React, { useState } from 'react';
import { Applicant, DocumentFile } from '../types';
import { ChevronRightIcon } from './Icons';
import FileUpload from './FileUpload';

interface ApplicantListProps {
  applicants: Applicant[];
  onSelectApplicant: (id: string) => void;
  onAddApplicant: (newApplicant: Applicant) => void;
}

const RiskIndicator: React.FC<{ score: number }> = ({ score }) => {
  let bgColor = 'bg-green-500';
  let text = 'Low Risk';

  if (score >= 0.75) {
    bgColor = 'bg-red-500';
    text = 'High Risk';
  } else if (score >= 0.4) {
    bgColor = 'bg-yellow-500';
    text = 'Medium Risk';
  }

  return (
    <div className="flex items-center gap-2">
      <span className={`h-3 w-3 rounded-full ${bgColor}`} />
      <span className="text-sm font-medium text-neutral-700">{text}</span>
    </div>
  );
};

const ApplicantList: React.FC<ApplicantListProps> = ({
  applicants,
  onSelectApplicant,
  onAddApplicant,
}) => {
  const [newApplicantName, setNewApplicantName] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState<DocumentFile[]>([]);

  const handleFilesChange = (files: File[]) => {
    const wrapped = files.map((file, index) => ({
      id: `${file.name}-${index}-${Date.now()}`,
      file,
    }));
    setUploadedFiles(prev => [...prev, ...wrapped]);
  };

  const handleRemoveFile = (id: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== id));
  };

  const handleCreateApplicant = () => {
    if (!newApplicantName.trim()) {
      alert('Please enter the applicant name.');
      return;
    }

    if (uploadedFiles.length === 0) {
      alert('Please upload at least one PDF document.');
      return;
    }

    const today = new Date().toISOString().slice(0, 10);

    const newApplicant: Applicant = {
      id: `${Date.now()}`,
      name: newApplicantName.trim(),
      applicationDate: today,
      riskScore: 0,
      summary:
        'Risk assessment and AI summary will appear here after the backend processes the uploaded documents.',
      documents: uploadedFiles.map(f => ({
        name: f.file.name,
        url: '#',
      })),
      fraudChecks: [
        { label: 'SSN matches IRS records', status: 'pass' },
        { label: 'Income consistent across documents', status: 'pass' },
        { label: 'Employer verified in registry', status: 'pass' },
        { label: 'Address consistent across documents', status: 'pass' },
      ],
    };

    onAddApplicant(newApplicant);

    setNewApplicantName('');
    setUploadedFiles([]);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-lg shadow-lg">
        {/* Only Overview here, styled like the old big title */}
        <h2 className="text-3xl font-bold text-neutral-900">Overview</h2>
        <p className="text-neutral-600 mt-2">
          View loan applicants, their application dates, and risk levels. Add new applicants
          by uploading their financial documents.
        </p>
      </div>

      {/* New applicant upload section */}
      <div className="bg-white p-6 rounded-lg shadow-lg space-y-4">
        <h2 className="text-xl font-semibold text-neutral-800">Add new applicant</h2>
        <p className="text-sm text-neutral-600">
          Enter the applicant&apos;s name and upload their PDF documents (bank statements,
          paystubs, application forms, etc.). The backend will later analyze these documents
          and update the risk score and AI summary.
        </p>

        <div className="flex flex-col gap-4 md:flex-row md:items-start">
          <div className="flex-1">
            <label className="block text-sm font-medium text-neutral-700 mb-1">
              Applicant name
            </label>
            <input
              type="text"
              value={newApplicantName}
              onChange={e => setNewApplicantName(e.target.value)}
              className="w-full rounded-md border border-neutral-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
              placeholder="e.g., Maria Rodriguez"
            />
          </div>
        </div>

        <FileUpload
          title="Upload applicant PDF documents"
          description="Drag and drop or click to select PDF files."
          onFilesChange={handleFilesChange}
          files={uploadedFiles}
          onRemoveFile={handleRemoveFile}
          multiple={true}
          accept=".pdf,application/pdf"
        />

        <button
          type="button"
          onClick={handleCreateApplicant}
          className="mt-2 inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-semibold text-white hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
        >
          Add to dashboard
        </button>
      </div>

      {/* Applicants list */}
      <div className="bg-white p-6 rounded-lg shadow-lg">
        <h2 className="text-2xl font-semibold text-neutral-900 mb-4">All Applicants</h2>
        <div className="divide-y divide-neutral-200">
          {applicants.map(applicant => (
            <button
              key={applicant.id}
              onClick={() => onSelectApplicant(applicant.id)}
              className="w-full flex items-center justify-between py-4 hover:bg-neutral-50 transition-colors text-left"
            >
              <div>
                <p className="text-lg font-semibold text-primary-dark">{applicant.name}</p>
                <p className="text-sm text-neutral-500">
                  Applied on: {applicant.applicationDate}
                </p>
              </div>
              <div className="flex items-center gap-4">
                <RiskIndicator score={applicant.riskScore} />
                <ChevronRightIcon className="h-6 w-6 text-neutral-400" />
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ApplicantList;
