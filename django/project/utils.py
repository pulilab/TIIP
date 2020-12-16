from typing import Dict, List, Tuple, Union


def remove_keys(data_dict: Dict, keys: Union[List, Tuple]) -> Dict:
    for key in keys:
        if key in data_dict:
            data_dict.pop(key, None)
    return data_dict


def _migrate_phases_to_stages(data: Dict, modified: datetime):
    if 'phase' in data and not data.get('stages'):
        if str(data['phase']) in ID_MAP.keys():
            data["stages"] = [{
                "id": ID_MAP[str(data['phase'])],
                "date": modified.isoformat().replace("+00:00", "Z"),
            }]
        data.pop('phase')
        return True
