import React, { useState } from 'react';
import { Applicant, DocumentFile } from '../types';
import { ChevronRightIcon } from './Icons';
import FileUpload from './FileUpload';
import { createApplicant } from '../services/apiService';

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
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  const handleCreateApplicant = async () => {
    if (!newApplicantName.trim()) {
      alert('Please enter the applicant name.');
      return;
    }

    if (uploadedFiles.length === 0) {
      alert('Please upload at least one PDF document.');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      // Extract File objects from DocumentFile
      const files = uploadedFiles.map(df => df.file);
      
      // Call API to upload to S3 and analyze
      const newApplicant = await createApplicant(newApplicantName.trim(), files);
      
      // Add the new applicant to the list
      onAddApplicant(newApplicant);

      // Reset form
      setNewApplicantName('');
      setUploadedFiles([]);
      
      // Show success message
      alert(`${newApplicant.name} added successfully!`);
      
    } catch (err) {
      console.error('Error creating applicant:', err);
      setError(err instanceof Error ? err.message : 'Failed to create applicant');
    } finally {
      setIsUploading(false);
    }
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
          paystubs, application forms, etc.). Documents will be uploaded to S3 and sent to your analyzer.
        </p>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
            <p className="text-sm font-medium">Error: {error}</p>
          </div>
        )}

        <div className="flex flex-col gap-4 md:flex-row md:items-start">
          <div className="flex-1">
            <label className="block text-sm font-medium text-neutral-700 mb-1">
              Applicant name
            </label>
            <input
              type="text"
              value={newApplicantName}
              onChange={e => setNewApplicantName(e.target.value)}
              disabled={isUploading}
              className="w-full rounded-md border border-neutral-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary disabled:bg-neutral-100 disabled:cursor-not-allowed"
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
          disabled={isUploading}
          className="mt-2 inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-semibold text-white hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:bg-neutral-400 disabled:cursor-not-allowed"
        >
          {isUploading ? (
            <>
              <svg 
                className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" 
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
              Uploading & Analyzing...
            </>
          ) : (
            'Add to dashboard'
          )}
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
