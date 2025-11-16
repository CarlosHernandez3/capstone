export interface DocumentFile {
    id: string;
    file: File;
}

export interface ApplicantDocument {
    name: string;
    url: string;
}

export interface Applicant {
    id: string;
    name: string;
    applicationDate: string;
    riskScore: number; // A value between 0 and 1
    summary: string;
    documents: ApplicantDocument[];
}
