import React, { useState } from 'react';
import { ApplicantDocument } from '../types';
import { FolderIcon, FilePdfIcon, ChevronRightIcon } from './Icons';

interface DocumentViewerProps {
    documents: ApplicantDocument[];
}

const DocumentViewer: React.FC<DocumentViewerProps> = ({ documents }) => {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <div>
            <button 
                onClick={() => setIsOpen(!isOpen)}
                className="w-full flex items-center justify-between p-4 bg-neutral-100 hover:bg-neutral-200 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
                aria-expanded={isOpen}
                aria-controls="document-list"
            >
                <div className="flex items-center gap-3">
                    <FolderIcon className="h-8 w-8 text-primary" />
                    <div>
                        <h4 className="font-bold text-lg text-neutral-800 text-left">Applicant Documents</h4>
                        <p className="text-sm text-neutral-600 text-left">{documents.length} file(s)</p>
                    </div>
                </div>
                <ChevronRightIcon className={`h-6 w-6 text-neutral-500 transform transition-transform ${isOpen ? 'rotate-90' : ''}`} />
            </button>
            
            {isOpen && (
                 <div id="document-list" className="mt-4 pl-4 border-l-2 border-neutral-200">
                    <ul className="space-y-2">
                        {documents.map((doc, index) => (
                            <li key={index}>
                                <a 
                                    href={doc.url} 
                                    target="_blank" 
                                    rel="noopener noreferrer" 
                                    className="flex items-center gap-3 p-2 rounded-md hover:bg-primary/10 transition-colors group"
                                >
                                    <FilePdfIcon className="h-6 w-6 text-danger/80" />
                                    <span className="text-neutral-700 group-hover:text-primary-dark font-medium">{doc.name}</span>
                                </a>
                            </li>
                        ))}
                    </ul>
                 </div>
            )}
        </div>
    );
};

export default DocumentViewer;
