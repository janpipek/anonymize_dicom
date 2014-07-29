import dicom
import glob
import os
import os.path

REMOVE_BY_DEFAULT = (
    'PatientBirthDate',
    'InstitutionAddress',
    'OtherPatientIDs',
    'PerformingPhysicianName',
    'OperatorsName',
    'ReferringPhysicianName',
    'StudyDate',
    'AcquisitionDate',
    'ContentDate',
    'AcquisitionDateTime',
    'StudyTime',
    'ContentTime',
    'SeriesTime',
    'AcquisitionTime',
    'AccessionNumber',
    'StationName',
    'StudyID',
    'RequestingService',
    'RequestedProcedureDescription'
)

SUBSTITUTE_BY_DEFAULT = {
    'PatientName' : 'Patient A. Nonymous',
    'PatientID' : '12345678',
    'InstitutionName' : 'The Hospital',
}

def anonymize_dir(in_path, out_path, **kwargs):
    '''Anonymize all DICOM files in a dir.

    :param kwargs: Arguments that are forwarded to anonymize_file.
    '''
    # Check input directory
    if not os.path.isdir(in_path):
        raise Exception(in_path + ' is not a directory')
    
    # Check output directory
    if os.path.exists(out_path):
        if not os.path.isdir(out_path):
            raise Exception(out_path + ' is not a directory')
    else:
        os.makedirs(out_path)

    in_files = [f for f in os.listdir(in_path) if f.endswith('.dcm')]
    for f in in_files:
        anonymize_file(os.path.join(in_path, f), os.path.join(out_path, f), **kwargs)

def anonymize_file(in_path, out_path, keep=(), remove=(), keep_private_tags=False, overwrite=False, **kwargs):
    '''Anonymize a DICOM file.

    :param in_path: File path to read from.
    :param out_path: File path to write to.
    :param overwrite: If False, trying to save to an existing file will throw exception (default: False)
    :param remove: A list of fields that should be removed in addition to the default ones.
    :param keep: A list of fields that should be kept in the file (takes precedence over all other parameters)
    :param keep_private_tags: If False, all private tags are removed (default: False)

    :param kwargs: Parameters and associated value will be substituted.

    All field names can be given in camel case (like PatientName) or in underlined format (like patient_name)
    to conform with python conventions. 

    There are a few fields that are substituted by default and a lot of fields that are removed by default.
    '''
    if os.path.exists(out_path) and not overwrite:
        raise Exception('Cannot overwrite ' + out_path + '. Use overwrite=True if you want that.')

    f = dicom.read_file(in_path)

    def _camelize(str):
        return ''.join([ frag[0].upper() + frag[1:] for frag in str.split('_') ])

    def _delete_field(field):
        _update_field(field, None)

    def _update_field(field, value):
        if field in keep:
            return
        if not field in f:
            return
        if value is None:
            f.__delattr__(field)
        else:
            f.__setattr__(field, value)

    keep = [_camelize(field) for field in keep]
    substitute = {_camelize(key) : value for key, value in kwargs.items()}
    remove = [_camelize(field) for field in remove]

    # Use defaults but the don't remove what user substitutes and vice versa
    remove = list((field for field in REMOVE_BY_DEFAULT if not field in substitute)) + remove
    for field, value in SUBSTITUTE_BY_DEFAULT.items():
        if field in remove or field in substitute:
            continue
        else:
            substitute[field] = value

    for field in remove:
        _delete_field(field)
    for field, value in substitute.items():
        _update_field(field, value)

    if not keep_private_tags:
        f.remove_private_tags()

    f.save_as(out_path)