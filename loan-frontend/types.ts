export interface DocumentFile {
    id: string;
    file: File;
}

export interface ApplicantDocument {
    name: string;
    url: string;
    confidenceScore: number; // 0-1 score indicating confidence the document is authentic (not tampered)
}

export interface FraudCheck {
    label: string;
    status: 'pass' | 'fail' | 'warning';
    details?: string;
}

export interface Applicant {
    id: string;
    name: string;
    applicationDate: string;
    riskScore: number; // A value between 0 and 1
    summary: string;
    documents: ApplicantDocument[];
    fraudChecks?: FraudCheck[];
}
