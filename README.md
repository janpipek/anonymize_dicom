anonymize_dicom
===============

A Python library for anonymizing DICOM files.

Dependencies
------------
pydicom - see https://code.google.com/p/pydicom/

Usage
-----

    import anonymize_dicom

    # Anonymize all files in a dir
    anonymize_dicom.anonymize_dir("mydir", "anonymized")

    # Anonymize a single file
    anonynize_dicom.anonymize_file("input.dcm", "output.dcm", patient_name="Marie Antoinette")

See method documentation for more details.
