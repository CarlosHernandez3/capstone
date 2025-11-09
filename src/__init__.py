"""
Data loading module for loan applicant documents.

This module provides functions to load and access loan applicant documents from S3.
All documents are cached locally for efficient access.

Usage:
    from src import initialize_applicant_mapping, get_applicant_docs_by_id, get_total_applicants
    
    # Initialize once at startup
    initialize_applicant_mapping()
    
    # Get specific applicant
    applicant = get_applicant_docs_by_id(1)
    
    # Get total count
    total = get_total_applicants()
"""

from .data_loader import (
    extract_from_s3,
    get_applicant_docs,
    initialize_applicant_mapping,
    get_applicant_docs_by_id,
    get_total_applicants,
)

__all__ = [
    'extract_from_s3',
    'get_applicant_docs',
    'initialize_applicant_mapping',
    'get_applicant_docs_by_id',
    'get_total_applicants',
]

__version__ = '0.1.0'