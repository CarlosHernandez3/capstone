
import React, { useRef, useCallback } from 'react';
import { DocumentFile } from '../types';
import { FileIcon, TrashIcon, UploadIcon } from './Icons';

interface FileUploadProps {
  title: string;
  description: string;
  onFilesChange: (files: File[]) => void;
  files: DocumentFile[];
  onRemoveFile: (id: string) => void;
  multiple: boolean;
  accept: string;
}

const FileUpload: React.FC<FileUploadProps> = ({ title, description, onFilesChange, files, onRemoveFile, multiple, accept }) => {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      onFilesChange(Array.from(event.target.files));
      // Reset the input value to allow re-uploading the same file
      event.target.value = '';
    }
  };

  const onDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
  };

  const onDrop = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    if (event.dataTransfer.files) {
        let fileList = Array.from(event.dataTransfer.files);
        if(!multiple) {
            fileList = fileList.slice(0,1);
        }
        onFilesChange(fileList);
    }
  }, [multiple, onFilesChange]);


  const openFileDialog = () => {
    inputRef.current?.click();
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <h3 className="text-xl font-bold text-neutral-900">{title}</h3>
      <p className="text-neutral-600 mt-1 mb-4">{description}</p>
      
      <div 
        className="border-2 border-dashed border-neutral-300 rounded-lg p-6 text-center cursor-pointer hover:border-primary transition-colors"
        onClick={openFileDialog}
        onDragOver={onDragOver}
        onDrop={onDrop}
      >
        <UploadIcon className="mx-auto h-12 w-12 text-neutral-400" />
        <p className="mt-2 text-sm text-neutral-600">
          <span className="font-semibold text-primary">Click to upload</span> or drag and drop
        </p>
        <p className="text-xs text-neutral-500 mt-1">
          {multiple ? "Multiple files" : "A single file"} are accepted
        </p>
        <input
          type="file"
          ref={inputRef}
          onChange={handleFileChange}
          className="hidden"
          multiple={multiple}
          accept={accept}
        />
      </div>

      {files.length > 0 && (
        <div className="mt-4">
          <h4 className="font-semibold text-neutral-700">Selected files:</h4>
          <ul className="mt-2 space-y-2">
            {files.map((docFile) => (
              <li key={docFile.id} className="flex items-center justify-between bg-neutral-100 p-2 rounded-md">
                <div className="flex items-center gap-2 overflow-hidden">
                  <FileIcon className="h-5 w-5 text-primary flex-shrink-0" />
                  <span className="truncate text-sm text-neutral-800" title={docFile.file.name}>{docFile.file.name}</span>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onRemoveFile(docFile.id);
                  }}
                  className="p-1 text-neutral-500 hover:text-danger rounded-full transition-colors"
                  aria-label="Remove file"
                >
                  <TrashIcon className="h-5 w-5" />
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
