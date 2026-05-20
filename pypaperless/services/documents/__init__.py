"""PyPaperless document services.

This package intentionally exposes no re-exports. ``pypaperless.models.documents.document``
imports the per-aspect services (``DocumentNoteService``, ``DocumentHistoryService``,
``DocumentAISuggestionsService``, ``DocumentShareLinkService``, ``DocumentRootService``,
``DocumentVersionService``) at module load time to wire them up as lazy ``Document``
properties. Re-exporting them here would force the subpackage ``__init__`` to load
``document.py`` first, which then imports the model — but the model is itself mid-init
in that scenario, producing a partially-initialised module ``ImportError``.

Consumers reach the per-aspect services either via ``pypaperless.services`` (top-level)
or directly via the corresponding submodule (``pypaperless.services.documents.notes`` …).
"""
