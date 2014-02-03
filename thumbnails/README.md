This directory contains thumbnails of videos/talks, which are used on the main
page to make the talks more attractive. Prefer to host them here rather than
from an external server (predictable page loads, less tracking, avoid broken
links). Aim for thumbnails that are about 75px high.

YouTube thumbnails can be fetched from:
https://img.youtube.com/vi/<video-id>/default.jpg
They may need to be cropped.

To get a vimeo thumbnail, fetch:
http://vimeo.com/api/v2/video/<video-id>.xml
Then look for the URL in the <thumbnail_small> tag and fetch that.

http://vimeo.com/api/v2/video/71635670.xml

