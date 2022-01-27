# USAGE

This Python package uses PyPi packages [requests](https://pypi.org/project/requests/) and [zeep](https://pypi.org/project/zeep/]) to interact with the Planon SOAP API.

## SETUP

The SOAP methods available are heavily based on what the Planon BO supports, some BOMs are not supported in SOAP out of the box.  The SOAP API must be configured, the Java code generated and compiled, and then the results jar deployed to the Planon Axis2 service.  For more information on configuring web services see Planon's [web services](https://webhelp.planoncloud.com/en/index.html#page/Web%20Services/c_Introduction.html#) documentation.

```sh
python -m venv venv
source venv/bin/activate
pip install ./libplanon
```

## INITIALIZATION

```python

soap_url = "{{PLANON_FQDN}}/nyx/services"
user = "USER"
pwd = "PWD"

get_token = libplanon.TokenManager(url=soap_url, username=user, password=pwd, reference_date=None).get_token

pln_client = libplanon.APIManager(url=soap_url, services=['AccountGroup', 'Account', 'Person'])
pln_account_client = pln_client['Account']
pln_group_client = pln_client['AccountGroup']
pln_person_client = pln_client['Person']

```

## QUERY

```python
code = "ABC123"

# Find by filter
group_ids = pln_group_client.find(get_token(), {
        'fieldFilters': [{
            'fieldName': 'Code',
            'filterValue': code,
            'operator': 'equals'
            }]
    })

# Find all
group_ids = pln_group_client.find(get_token(), {})
```

## READ

```python

groups = []
for group_id in group_ids:
     groups.append(pln_group_client.read(get_token(), group_id))

```

## UPDATE

```python

group = groups[0]

group['Name'] = "Hello World!"
pln_group_client.save(get_token(), group))

```
