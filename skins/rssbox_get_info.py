## Script (Python) "rssbox_get_info"
##parameters=channel_id

# $Id$

channel = getattr(context.portal_rss, channel_id, None)

if channel is None:
    return {'title': "Broken RSS Channel",
            'description': "This RSS Feed is badly configured (unknown URL).",
            'url': ".",
            'lines': [],
            'newWindow': 0,
            }

return channel.getData()
