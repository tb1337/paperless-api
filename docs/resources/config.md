# Config

The `config` resource exposes the Paperless-ngx application configuration. It is a single-item resource — the instance is always fetched with primary key `1`.

## Model

| Field                    | Description                         |
| ------------------------ | ----------------------------------- |
| `id`                     | Always `1`                          |
| `user_args`              | Extra arguments passed to Tesseract |
| `output_type`            | OCR output format (e.g. `"pdf"`)    |
| `pages`                  | Number of pages to OCR (0 = all)    |
| `language`               | OCR language code                   |
| `mode`                   | OCR mode                            |
| `skip_archive_file`      | Archive-skip policy                 |
| `image_dpi`              | DPI for rasterized images           |
| `deskew`                 | Enable deskew                       |
| `rotate_pages`           | Enable automatic page rotation      |
| `rotate_pages_threshold` | Rotation confidence threshold       |
| `max_image_pixels`       | Maximum image size in pixels        |
| `app_title`              | Paperless web UI title              |
| `app_logo`               | Paperless web UI logo path          |
| `barcodes_enabled`       | Enable barcode processing           |
| `barcode_string`         | Custom barcode separator string     |
| `barcode_enable_asn`     | Detect ASN from barcodes            |
| `barcode_asn_prefix`     | Expected ASN barcode prefix         |

## Fetch

Config is a singleton — always request it with pk `1`:

```python
config = await paperless.config(1)

print(config.language)          # e.g. "deu"
print(config.barcodes_enabled)  # True / False
print(config.app_title)         # e.g. "Paperless-ngx"
```
