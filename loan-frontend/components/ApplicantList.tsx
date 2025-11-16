import React from 'react';
import { Applicant } from '../types';
import { ChevronRightIcon } from './Icons';

interface ApplicantListProps {
    applicants: Applicant[];
    onSelectApplicant: (id: string) => void;
}

const RiskIndicator: React.FC<{ score: number }> = ({ score }) => {
    let bgColor = 'bg-accent';
    let text = 'Low Risk';
    if (score >= 0.75) {
        bgColor = 'bg-danger';
        text = 'High Risk';
    } else if (score >= 0.4) {
        bgColor = 'bg-secondary';
        text = 'Medium Risk';
    }

    return (
        <div className="flex items-center gap-2">
            <span className={`h-3 w-3 rounded-full ${bgColor}`}></span>
            <span className="text-sm font-semibold text-neutral-700 hidden sm:block">{text}</span>
        </div>
    );
};

const ApplicantList: React.FC<ApplicantListProps> = ({ applicants, onSelectApplicant }) => {
    return (
        <div className="bg-white p-4 sm:p-6 rounded-lg shadow-lg">
            <h2 className="text-2xl font-bold text-neutral-900 mb-4 border-b pb-2">All Applicants</h2>
            <div className="space-y-3">
                {applicants.map(applicant => (
                    <button 
                        key={applicant.id}
                        onClick={() => onSelectApplicant(applicant.id)}
                        className="w-full flex items-center justify-between p-4 bg-white border border-neutral-200 rounded-lg hover:bg-neutral-100 hover:border-primary-light transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                        <div>
                            <p className="font-bold text-lg text-primary-dark text-left">{applicant.name}</p>
                            <p className="text-sm text-neutral-500 text-left">Applied on: {applicant.applicationDate}</p>
                        </div>
                        <div className="flex items-center gap-4 sm:gap-6">
                            <RiskIndicator score={applicant.riskScore} />
                            <ChevronRightIcon className="h-6 w-6 text-neutral-400" />
                        </div>
                    </button>
                ))}
            </div>
        </div>
    )
};

export default ApplicantList;
