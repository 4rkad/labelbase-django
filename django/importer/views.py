import os
import tempfile

from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
from labelbase.models import Labelbase

from .forms import UploadFileForm
from .tasks import process_uploaded_data
from .models import UploadedData


@login_required
def upload_labels(request):
    """
    Used to import labels manually using files.
    """
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            labelbase = get_object_or_404(
                Labelbase,
                id=form.cleaned_data.get("labelbase_id", ""),
                user_id=request.user.id,
            )
            import_type = form.cleaned_data.get("import_type", "")
            passphrase = form.cleaned_data.get("passphrase", None) or ""
            uploaded_file = request.FILES["file"]

            # BIP-329 encrypted archives (.7z, AES-256 + SHA-256(passphrase))
            # are decrypted synchronously so we can surface wrong-passphrase
            # errors in the request response. The decrypted .jsonl is then
            # handed to the normal BIP-0329 importer pipeline.
            if import_type == "BIP-0329-7z-enc":
                from bip329.encryption import decrypt_files
                with tempfile.TemporaryDirectory() as tmpdir:
                    archive_path = os.path.join(
                        tmpdir, uploaded_file.name or "labels.7z"
                    )
                    with open(archive_path, "wb") as fh:
                        for chunk in uploaded_file.chunks():
                            fh.write(chunk)
                    try:
                        decrypt_files(archive_path, tmpdir, passphrase)
                    except Exception:
                        messages.add_message(
                            request,
                            messages.ERROR,
                            "Could not decrypt the archive. Wrong passphrase "
                            "or not a BIP-329 encrypted .7z file.",
                        )
                        return HttpResponseRedirect(labelbase.get_absolute_url())

                    extracted = [
                        os.path.join(tmpdir, name)
                        for name in os.listdir(tmpdir)
                        if os.path.join(tmpdir, name) != archive_path
                        and os.path.isfile(os.path.join(tmpdir, name))
                    ]
                    if not extracted:
                        messages.add_message(
                            request,
                            messages.ERROR,
                            "Encrypted archive contained no label file.",
                        )
                        return HttpResponseRedirect(labelbase.get_absolute_url())

                    with open(extracted[0], "rb") as fh:
                        decrypted_file = ContentFile(fh.read(), name="labels.jsonl")

                    uploaded_data = UploadedData.objects.create(
                        user=request.user,
                        labelbase=labelbase,
                        import_type="BIP-0329",
                        file=decrypted_file,
                    )
            else:
                uploaded_data = UploadedData.objects.create(
                    user=request.user,
                    labelbase=labelbase,
                    import_type=import_type,
                    file=uploaded_file,
                )

            process_uploaded_data(uploaded_data.id, passphrase=passphrase)
            messages.add_message(
                request,
                messages.INFO,
                "Task scheduled successfully.",
#               "Task scheduled successfully. You will be notified upon completion.",
            )
            return HttpResponseRedirect(labelbase.get_absolute_url())
    else:
        form = UploadFileForm()
    return render(request, "upload.html", {"form": form})
