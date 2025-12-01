import React, { useState } from 'react';
import { Applicant, DocumentFile } from '../types';
import { ArrowLeftIcon } from './Icons';
import PieChart from './PieChart';
import DocumentViewer from './DocumentViewer';
import FileUpload from './FileUpload';

interface ApplicantDashboardProps {
    applicant: Applicant;
    onBack: () => void;
}

const ApplicantDashboard: React.FC<ApplicantDashboardProps> = ({ applicant, onBack }) => {
    const [uploadedFiles, setUploadedFiles] = useState<DocumentFile[]>([]);

    const handleFilesChange = (files: File[]) => {
        const wrapped = files.map((file, index) => ({
            id: `${file.name}-${index}-${Date.now()}`,
            file,
        }));
        // append new files to any existing ones
        setUploadedFiles(prev => [...prev, ...wrapped]);
    };

    const handleRemoveFile = (id: string) => {
        setUploadedFiles(prev => prev.filter(f => f.id !== id));
    };

    return (
        <div className="animate-fade-in">
            <button
                onClick={onBack}
                className="flex items-center gap-2 text-primary-dark font-semibold mb-6 hover:underline"
            >
                <ArrowLeftIcon className="h-5 w-5" />
                Back to all applicants
            </button>

            <div className="space-y-6">
                {/* Header */}
                <div className="bg-white p-6 rounded-lg shadow-lg">
                    <h2 className="text-3xl font-bold text-neutral-900">{applicant.name}</h2>
                    <p className="text-neutral-500 mt-1">
                        Application Date: {applicant.applicationDate}
                    </p>
                </div>

                {/* Main Content Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Risk Assessment */}
                    <div className="lg:col-span-1 bg-white p-6 rounded-lg shadow-lg flex flex-col items-center">
                        <h3 className="text-xl font-bold text-neutral-800 mb-4">Risk Assessment</h3>
                        <PieChart score={applicant.riskScore} size={200} />
                        <p className="text-center text-neutral-600 mt-4">
                            Based on the provided documents, the applicant has a
                            <span className="font-bold">
                                {' '}{Math.round(applicant.riskScore * 100)}%
                            </span>{' '}
                            risk score.
                        </p>
                    </div>

                    {/* AI Summary */}
                    <div className="lg:col-span-2 bg-white p-6 rounded-lg shadow-lg">
                        <h3 className="text-xl font-bold text-neutral-800 mb-4">AI Summary</h3>
                        <p className="text-neutral-700 leading-relaxed">{applicant.summary}</p>
                    </div>
                </div>

                {/* Upload Documents */}
                <div className="bg-white p-6 rounded-lg shadow-lg">
                    <h3 className="text-xl font-bold text-neutral-800 mb-2">
                        Upload applicant documents
                    </h3>
                    <p className="text-sm text-neutral-600 mb-4">
                        Select one or more PDF files (bank statements, paystubs, forms) to attach
                        for this applicant. In the future these files will be sent to the backend
                        for OCR and fraud analysis.
                    </p>
                    <FileUpload
                        title="Upload PDF documents"
                        description="Drag and drop or click to select PDF files."
                        onFilesChange={handleFilesChange}
                        files={uploadedFiles}
                        onRemoveFile={handleRemoveFile}
                        multiple={true}
                        accept=".pdf,application/pdf"
                    />
                </div>

                {/* Documents */}
                <div className="bg-white p-6 rounded-lg shadow-lg">
                    <DocumentViewer documents={applicant.documents} />
                </div>
            </div>
        </div>
    );
};

export default ApplicantDashboard;
