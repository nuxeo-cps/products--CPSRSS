## Script (Python) "getCustomBoxTypes"
##parameters=
# $Id$
"""Return custom  box types."""

items = [{'category': 'rssbox',
          'title': 'portal_type_RssBox_title',
          'desc':'portal_type_RssBox_description',
          'types': [{'provider': 'rss',
                     'id': 'default',
                     'desc': 'description_rss_rssbox_default'},
                    ]
          },
         ]

return items
