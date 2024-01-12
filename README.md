# cisco-ise-ers-api
small python client to Cisco ISE External RESTful Services APIs

Currently only implements

- network-device/get-all
- network-device/get-by-id


# install

```
pip install git+https://github.com/lumean/cisco-ise-ers-api@main
```

specific version (check available tags on github)

```
pip install git+https://github.com/lumean/cisco-ise-ers-api@v1.0.0
```

requirements file:

```
iseersapi @ git+https://github.com/lumean/cisco-ise-ers-api@v1.0.0
```

# Usage

```python
import os
import json
from iseersapi import IseErsApi

ise_user = os.getenv('ISEUSER')
ise_pass = os.getenv('ISEPASSWORD')

ise = IseErsApi('myise.example.org', ise_user, ise_pass, verify=False)

all_devices = ise.export_all_network_elements()
    with open('ise_device_details.json', 'w') as f:
        json.dump(all_devices, f, indent=2)
```

# Author(s)

This project was written and is maintained by the following individuals:

- Manuel Widmer mawidmer@cisco.com
