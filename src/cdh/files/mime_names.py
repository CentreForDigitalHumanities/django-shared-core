from django.utils.text import gettext_lazy as _
from typing import Optional, Union

_names = {
    # Application
    'application/octet-stream': _('Unspecified binary data'),
    'application/json': _('JSON data'),
    'application/pgp-encrypted': _('PGP encrypted file'),
    'application/pgp-signature': _('PGP signature'),
    'application/rss+xml': _('RSS feed'),
    'application/rtf': _('Rich text file'),
    'application/x-msaccess': _('Microsoft Access file'),
    'application/csv': _('Character-Separated Values (CSV) file'),  # Yes we're
    # aware it's 'Comma-Separated', but there are enough CSV files that use a
    # different character...

    # Start MS BS
    # Word BS
    'application/msword':
        _('Microsoft Word document'),
    'application/vnd.ms-word.document.macroenabled.12':
        _('Microsoft Word document'),
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        _('Microsoft Word document'),
    'application/vnd.ms-word.template.macroenabled.12':
        _('Microsoft Word template'),
    'application/vnd.openxmlformats-officedocument.wordprocessingml.template':
        _('Microsoft Word template'),
    # Excel BS
    'application/vnd.openxmlformats-officedocument.spreadsheetml.template':
        _('Microsoft Excel template'),
    'application/vnd.ms-excel.template.macroenabled.12l':
        _('Microsoft Excel template'),
    'application/vnd.ms-excel':
        _('Microsoft Excel spreadsheet'),
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        _('Microsoft Excel spreadsheet'),
    'application/vnd.ms-excel.macroenabled.12':
        _('Microsoft Excel spreadsheet'),
    # Powerpoint BS
    'application/vnd.ms-powerpoint':
        _('Powerpoint presentation'),
    'application/vnd.ms-powerpoint.presentation.macroenabled.12':
        _('Powerpoint presentation'),
    'application/vnd.ms-powerpoint.slideshow.macroenabled.12':
        _('Powerpoint presentation'),
    'application/vnd.openxmlformats-officedocument.presentationml.presentation':
        _('Powerpoint presentation'),
    'application/vnd.openxmlformats-officedocument.presentationml.slidedown':
        _('Powerpoint presentation'),
    'application/vnd.openxmlformats-officedocument.presentationml.slide':
        _('Powerpoint slide'),
    'application/vnd.ms-powerpoint.slide.macroenabled.12':
        _('Powerpoint slide'),
    'application/vnd.openxmlformats-officedocument.presentationml.template':
        _('Powerpoint template'),
    # Misc MS office
    'application/onenote': _('Microsoft OneNote'),
    'application/x-mswrite':
        _('Microsoft Wordpad document'),
    # End MS BS
    # Begin OpenDocument/OpenOffice
    'application/vnd.oasis.opendocument.database':
        _('OpenDocument Database'),
    'application/vnd.oasis.opendocument.formula':
        _('OpenDocument formula'),
    'application/vnd.sun.xml.math':
        _('OpenDocument formula'),
    'application/vnd.oasis.opendocument.formula-template':
        _('OpenDocument formula template'),
    'application/vnd.oasis.opendocument.graphics':
        _('OpenDocument graphic'),
    'application/vnd.sun.xml.draw':
        _('OpenDocument graphic'),
    'application/vnd.oasis.opendocument.graphics-template':
        _('OpenDocument graphic template'),
    'application/vnd.sun.xml.draw.template':
        _('OpenDocument graphic template'),
    'application/vnd.oasis.opendocument.image':
        _('OpenDocument image'),
    'application/vnd.oasis.opendocument.image-template':
        _('OpenDocument image template'),
    'application/vnd.oasis.opendocument.presentation':
        _('OpenDocument presentation'),
    'application/vnd.sun.xml.impress':
        _('OpenDocument presentation'),
    'application/vnd.oasis.opendocument.presentation-template':
        _('OpenDocument presentation template'),
    'application/vnd.sun.xml.impress.template':
        _('OpenDocument presentation template'),
    'application/vnd.oasis.opendocument.spreadsheet':
        _('OpenDocument spreadsheet'),
    'application/vnd.sun.xml.calc':
        _('OpenDocument spreadsheet'),
    'application/vnd.oasis.opendocument.spreadsheet-template':
        _('OpenDocument spreadsheet template'),
    'application/vnd.sun.xml.calc.template':
        _('OpenDocument spreadsheet template'),
    'application/vnd.oasis.opendocument.text':
        _('OpenDocument document'),
    'application/vnd.sun.xml.writer':
        _('OpenDocument document'),
    'application/vnd.oasis.opendocument.text-template':
        _('OpenDocument document template'),
    'application/vnd.sun.xml.writer.template':
        _('OpenDocument document template'),
    # End OpenDocument/OpenOffice
    'application/x-debian-package': _('Debian package'),
    'application/x-font-otf': _('OTF font'),
    'application/x-font-ttf': _('TTF font'),
    'application/x-font-woff': _('WOFF font'),
    'application/x-bzip': _('BZip file archive'),
    'application/x-bzip2': _('BZip2 file archive'),
    'application/x-gtar': _('GNU Tar file'),
    'application/x-latex': _('LaTeX file'),
    'application/x-tex': _('TeX file'),
    'application/x-shar': _('Shell archive'),
    'application/x-rar-compressed': _('RAR file archive'),
    'application/x-7z-compressed': _('7-Zip file archive'),
    'application/zip': _('Zip file archive'),
    'application/x-vcalendar': _('vCalendar'),
    'application/x-vcard': _('vCard'),
    'application/xml': _('XML file'),

    # Audio
    'audio/mp3': _('MP3 audio'),
    'audio/mp4': _('MP4 audio'),
    'audio/ogg': _('OGG audio'),

    # Images
    'image/bmp': _('Bitmap image'),
    'image/jpeg': _('JPEG image'),
    'image/psr.btf': _('BTIF image'),
    'image/png': _('PNG image'),
    'image/svg+xml': _('SVG image'),
    'image/webp': _('WebP image'),
    'image/vnd.xiff': _('eXtended Image File Format (XIFF)'),
    'image/x-icon': _('Icon image'),
    'image/vnd.adobe.photoshop': _('Photoshop image'),

    # Text based
    'text/plain': _('Text file'),
    'text/calendar': _('iCalender file'),
    'text/x-c': _('C source file'),
    'text/x-python': _('Python source file'),
    'text/css': _('Cascading Style Sheets (CSS) file'),
    'text/csv': _('Character-Separated Values (CSV) file'),  # Yes we're
    # aware it's 'Comma-Separated', but there are enough CSV files that use a
    # different character...
    'text/richtext': _('Richt text file'),

    # Video
    'video/h261': _('H.261 video'),
    'video/h263': _('H.263 video'),
    'video/h264': _('H.264 video'),
    'video/mpeg': _('MPEG video'),
    'video/mp4': _('MP4 video'),
    'video/ogg': _('OGG video'),
    'video/x-m4v': _('M4V video'),
}


def get_name_from_mime(
        mime: str,
        default: Optional[Union[str, callable]] = None
) -> str:
    """Returns a human friendly name for a given MIME type.
    Note: the DB of mime-types is a VERY small subset of all possible types. If
    a MIME isn't in the DB, this function will return the MIME (or a
    different default if supplied)

    :param mime: a MIME which needs a human friendly name
    :param default: either a string or a callable which is used to provide a
                    value if the MIME is not known. A callable must accept 1
                    parameter (which will be the MIME as supplied).
    """
    if mime is None or not isinstance(mime, str):
        raise ValueError(f"Unsupported type {type(mime)} for parameter 'mime'")
    if default is not None and not isinstance(default, str) and not callable(
        default
    ):
        raise ValueError(
            f"Unsupported type {type(default)} for parameter 'default'"
        )

    if default is None:
        default = mime

    name = _names.get(mime)

    if not name:
        if callable(default):
            name = default(mime)
        else:
            name = default

    return name
