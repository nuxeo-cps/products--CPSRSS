##parameters=**kw
#
# $Id$
"""The script that returns RSS items according to the portlet parameters.
"""

from copy import deepcopy
from logging import getLogger

import operator

from Products.CPSUtil.text import summarize

LOG_KEY = 'CPSPortlets.getRSSItems'

DEFAULT_RSS_ITEM_DISPLAY = 'cpsportlet_rssitem_display'

#logger = getLogger(LOG_KEY)

rsstool = getattr(context, 'portal_rss', None)
if rsstool is None:
    return []

first_item = int(kw.get('first_item', 1))
max_items = int(kw.get('max_items', 0))
max_words = int(kw.get('max_words', 0))

data_items = []
channels_ids = kw.get('channels')
for channel_id in channels_ids:
    channel = getattr(rsstool.aq_inner.aq_explicit, channel_id, None)
    if channel is None:
        continue
    data = channel.getData(max_items + first_item - 1)
    lines = deepcopy(data['lines']) # RSSChan did a simple copy
    for line in lines:
        # lines will be shuffled around (timely sort), so channel dependent
        # display options have to be copied
        line['newWindow'] = data['newWindow']
    data_items += lines
    if first_item > 1:
        data_items = data_items[first_item - 1:]

# If there is more than 1 channel we need to sort the rss items to only keep the
# more recent ones, up to max_items.
if len(channels_ids) > 1:
    # NOTE: One should replace "modified" with "updated" if switching to a newer
    # version of Feed Parser http://feedparser.org/docs/date-parsing.html
    # Relying on the 'modified_parsed' item for the sorting.
    data_items.sort(key=operator.itemgetter('modified_parsed'), reverse=True)
    data_items = data_items[:max_items]

render_method = kw.get('render_method') or DEFAULT_RSS_ITEM_DISPLAY
render_method = getattr(context, render_method, None)

order = 0
for item in data_items:
    description = item['description']
    modified = item['modified']
    author = item['author']
    if not author:
        author = 'unknown'

    # Item rendering and display
    rendered = ''

    # render the item using a custom display method (.zpt, .py, .dtml)
    if render_method is not None:
        item['summary'] = summarize(description, max_words)
        kw.update({'item': item,
                   'order': order,
                  })
        rendered = apply(render_method, (), kw)

    # this information is used by custom templates that call getRSSItems()
    # directly.
    data_items[order].update(
        {'description': description,
         'rendered': rendered,
         'metadata':
            {'creator': author,
             'contributor': author,
             'date': modified,
             'issued': modified,
             'created': modified,
            },
        })
    order += 1

return data_items
