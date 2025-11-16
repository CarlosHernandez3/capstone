import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="bg-primary-dark shadow-md">
      <div className="container mx-auto px-4 py-4 md:px-8">
        <h1 className="text-2xl md:text-3xl font-bold text-white tracking-wide">
          Loan Applicant Dashboard
        </h1>
      </div>
    </header>
  );
};

export default Header;
