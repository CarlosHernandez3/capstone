import { Applicant } from '../types';

export const mockApplicants: Applicant[] = [
  {
    id: '1',
    name: 'John Doe',
    applicationDate: '2024-07-15',
    riskScore: 0.25, // low risk
    summary: 'John Doe is a strong candidate with a stable income and a solid credit history. All provided documents align with the application details. The calculated income from pay stubs and bank statements is consistent with the amount stated on the loan application. No red flags were detected in the financial documents. Low risk profile.',
    documents: [
      { name: 'Loan_Application_JDoe.pdf', url: '#' },
      { name: 'Bank_Statement_May24.pdf', url: '#' },
      { name: 'Paystub_May24.pdf', url: '#' },
    ],
  },
  {
    id: '2',
    name: 'Jane Smith',
    applicationDate: '2024-07-14',
    riskScore: 0.82, // high risk
    summary: 'Jane Smith presents a high-risk profile. There are significant discrepancies between the income stated on the application and the amounts shown on her bank statements. Furthermore, there is evidence of multiple recent credit inquiries and a high debt-to-income ratio. Several unusual, large cash deposits are unexplained. Caution is strongly advised.',
    documents: [
      { name: 'JSmith_Application.pdf', url: '#' },
      { name: 'BankStatement_Q2.pdf', url: '#' },
    ],
  },
  {
    id: '3',
    name: 'Sam Wilson',
    applicationDate: '2024-07-12',
    riskScore: 0.55, // medium risk
    summary: 'Sam Wilson is a moderate-risk applicant. Employment and income are verified, but the applicant has a short credit history and a recent job change. The bank statements show a healthy cash flow but also a few instances of overdrafts in the past six months. Further documentation regarding employment stability might be required.',
    documents: [
      { name: 'SW_LoanApp.pdf', url: '#' },
      { name: 'Bank_Statement_07_2024.pdf', url: '#' },
      { name: 'Paystub_July_First.pdf', url: '#' },
      { name: 'Employment_Offer_Letter.pdf', url: '#' },
    ],
  },
];
