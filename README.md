# Paperless API

Simple stupid Python wrapper for the paperless-ngx REST API endpoint. Find out more here: https://paperless-ngx.readthedocs.io/en/latest/api.html

## Examples

### Request a specific document and update it.

```python
from pypaperless import *

# do not ever do that... but it would work
paperless = Paperless("http://paperless.url:8000", username="test", password="test")

# create a token via admin panel instead
paperless = Paperless("http://paperless.url:8000", "super_secret_api_token")

secret_document = paperless.get_document(1337)
secret_document.title = "TOP SECRET!"

paperless.save(secret_document)
```

### Same is possible for every other entity provided by the API, excepting logs.

```python
user = paperless.get_user(3)
correspondent = paperless.get_correspondent(1)
document_type = paperless.get_document_type(1)
tag = paperless.get_tag(1)
saved_view = paperless.get_saved_view(1)
storage_path = paperless.get_storage_path(1)
group = paperless.get_group(1)
mail_account = paperless.get_mail_account(1)
mail_rule = paperless.get_mail_rule(1)
```

### Request all entitys from paperless.

```python
users = paperless.get_users()
correspondents = paperless.get_correspondents()
document_types = paperless.get_document_types()
tags = paperless.get_tags()
saved_views = paperless.get_saved_views()
storage_paths = paperless.get_storage_paths()
groups = paperless.get_groups()
mail_accounts = paperless.get_mail_accounts()
mail_rules = paperless.get_mail_rules()

# could take some time
documents = paperless.get_documents()
```

### Post a document to paperless.

```python
# will return soon
```

### Create a new correspondent:

```python
new_correspondent = PaperlessCorrespondent(name="Salty Correspondent")

paperless.create(new_correspondent)
```

### Search for a document and receive a list of results.

Search syntax is the same as in Paperless: https://docs.paperless-ngx.com/usage/#basic-usage_searching.

```python
# will return soon
```