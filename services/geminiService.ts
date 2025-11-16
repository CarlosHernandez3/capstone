
import { GoogleGenAI } from "@google/genai";

const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => {
            const result = reader.result as string;
            // remove "data:mime/type;base64," prefix
            resolve(result.split(',')[1]);
        };
        reader.onerror = error => reject(error);
    });
};

const PROMPT = `
You are an expert loan underwriting assistant. Your task is to analyze a set of financial documents and compare them against a loan application.

The provided files include one loan application and several supporting documents (such as bank statements, pay stubs, or tax forms).

First, identify which document is the loan application based on its content.

Then, perform the following analysis:

1.  **Applicant Information Verification:**
    *   Extract the applicant's full name, address, and employer from the loan application.
    *   Cross-reference this information with the details found in the supporting documents. Note any discrepancies.

2.  **Income Verification:**
    *   Identify the income stated on the loan application.
    *   Analyze the pay stubs and bank statements to calculate the average monthly income.
    *   Compare the stated income with the calculated income. Highlight if the stated income is supported by the documents.

3.  **Employment Verification:**
    *   Verify the employer's name on the pay stubs matches the one on the loan application.
    *   Note the employment duration if available.

4.  **Financial Health Summary:**
    *   Briefly summarize the applicant's financial health based on the bank statements. Note any large, unusual deposits or consistent negative balances.

5.  **Summary Report:**
    *   Provide a clear, concise summary of your findings. Use the following Markdown format. Do not add any text before the first '###'.

    ### Loan Application Analysis Report

    **Applicant:** [Applicant's Name]

    ---

    **Verification Summary:**
    *   **Full Name:** [✅ Verified / ❌ Discrepancy / ⚠️ Not Found] - *Details if not verified.*
    *   **Address:** [✅ Verified / ❌ Discrepancy / ⚠️ Not Found] - *Details if not verified.*
    *   **Employer:** [✅ Verified / ❌ Discrepancy / ⚠️ Not Found] - *Details if not verified.*
    *   **Income:** [✅ Verified / ❌ Discrepancy / ⚠️ Not Found] - *Details: Stated $[Amount], Calculated Average $[Amount].*

    ---

    **Detailed Findings:**
    *   [Bulleted list of detailed observations, both positive and negative.]
    *   [Example: Pay stubs from 'Tech Corp Inc.' confirm the employer.]
    *   [Example: Average monthly deposits of ~$5,200 support the stated income of $60,000/year.]
    *   [Example: The address on the bank statement is different from the application.]

    ---

    **Recommendation:**
    *   [Brief recommendation: "Proceed with caution", "Information verified", or "Significant discrepancies found".]
`;


export const analyzeDocuments = async (loanApplication: File, supportingDocs: File[]): Promise<string> => {
    if (!process.env.API_KEY) {
        throw new Error("API key is missing. Please set the API_KEY environment variable.");
    }
    const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
    
    const allFiles = [loanApplication, ...supportingDocs];

    const fileParts = await Promise.all(
        allFiles.map(async (file) => {
            const base64Data = await fileToBase64(file);
            return {
                inlineData: {
                    data: base64Data,
                    mimeType: file.type,
                },
            };
        })
    );
    
    const contents = [{
        parts: [
            { text: PROMPT },
            ...fileParts
        ]
    }];

    try {
        const response = await ai.models.generateContent({
            model: 'gemini-2.5-flash',
            contents,
        });
        return response.text;
    } catch (error) {
        console.error("Gemini API call failed:", error);
        throw new Error("Failed to get a response from the AI model.");
    }
};
