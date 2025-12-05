import { Applicant } from '../types';

export const mockApplicants: Applicant[] = [
  {
    id: '1',
    name: 'John Doe',
    applicationDate: '2024-07-15',
    riskScore: 0.25, // low risk
    summary:
      'John Doe is a strong candidate with a stable income and consistent documentation. No major risk factors were detected across the uploaded documents.',
    documents: [
      { name: 'Loan_Application_JDoe.pdf', url: '#' },
      { name: 'Bank_Statement_May24.pdf', url: '#' },
      { name: 'Paystub_May24.pdf', url: '#' },
    ],
    fraudChecks: [
      { label: 'SSN matches IRS records', status: 'pass' },
      { label: 'Income consistent across documents', status: 'pass' },
      { label: 'Employer verified in business registry', status: 'pass' },
      { label: 'Address consistent across documents', status: 'pass' },
    ],
  },
  {
    id: '2',
    name: 'Jane Smith',
    applicationDate: '2024-07-12',
    riskScore: 0.82, // high risk
    summary:
      'Multiple inconsistencies were found between the stated income and the values observed in bank statements and paystubs. Applicant is considered high risk and requires manual review.',
    documents: [
      { name: 'Loan_Application_JaneSmith.pdf', url: '#' },
      { name: 'Bank_Statement_May24.pdf', url: '#' },
      { name: 'Paystub_May15.pdf', url: '#' },
    ],
    fraudChecks: [
      { label: 'SSN matches IRS records', status: 'pass' },
      {
        label: 'Income consistent across documents',
        status: 'fail',
        details: 'Reported monthly income is significantly higher than average deposits.',
      },
      {
        label: 'Employer verified in business registry',
        status: 'warning',
        details: 'Employer has limited public records; flagged for additional verification.',
      },
      {
        label: 'Address consistent across documents',
        status: 'fail',
        details: 'Bank statement address does not match the loan application address.',
      },
    ],
  },
  {
    id: '3',
    name: 'Sam Wilson',
    applicationDate: '2024-07-10',
    riskScore: 0.55, // medium risk
    summary:
      'Sam Wilson shows moderate risk. Most information is consistent but there are minor anomalies that should be reviewed before final approval.',
    documents: [
      { name: 'SW_LoanApp.pdf', url: '#' },
      { name: 'Bank_Statement_07_2024.pdf', url: '#' },
      { name: 'Paystub_July_First.pdf', url: '#' },
      { name: 'Employment_Offer_Letter.pdf', url: '#' },
    ],
    fraudChecks: [
      { label: 'SSN matches IRS records', status: 'pass' },
      {
        label: 'Income consistent across documents',
        status: 'warning',
        details: 'One recent paystub shows a lower amount than the stated monthly income.',
      },
      { label: 'Employer verified in business registry', status: 'pass' },
      { label: 'Address consistent across documents', status: 'pass' },
    ],
  },
];
