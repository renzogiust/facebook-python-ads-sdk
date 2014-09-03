# Copyright 2014 Facebook, Inc.

# You are hereby granted a non-exclusive, worldwide, royalty-free license to
# use, copy, modify, and distribute this software in source code or binary
# form for use in connection with the web services and APIs provided by
# Facebook.

# As with any software that integrates with the Facebook platform, your use
# of this software is subject to the Facebook Developer Principles and
# Policies [http://developers.facebook.com/policy/]. This copyright notice
# shall be included in all copies or substantial portions of the software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

"""
Creates ad through a standard creation workflow.
"""

from facebookads import FacebookSession
from facebookads import FacebookAdsApi
from facebookads.objects import (
    AdUser,
    AdCampaign,
    AdSet,
    AdImage,
    AdCreative,
    AdGroup,
    TargetingSpecsField,
)

import configparser
import os
import time
import pprint

pp = pprint.PrettyPrinter(indent=4)
config = configparser.RawConfigParser()
this_dir = os.path.dirname(__file__)
config_filename = os.path.join(this_dir, 'my_app_session.cfg')

with open(config_filename) as config_file:
    config.readfp(config_file)

### Setup session and api objects
session = FacebookSession(
    config.get('Authentication', 'app_id'),
    config.get('Authentication', 'app_secret'),
    config.get('Authentication', 'access_token'),
)
api = FacebookAdsApi(session)

if __name__ == '__main__':
    FacebookAdsApi.set_default_api(api)

    print('\n\n\n********** Ad Creation example. **********\n')

    ### Setup user and read the object from the server
    me = AdUser(fbid='me')

    ### Get first account connected to the user
    my_account = me.get_ad_account()

    ### Create a Campaign
    campaign = my_account.child(AdCampaign)
    campaign.update({
        AdCampaign.Field.name: 'Seattle Ad Campaign',
        AdCampaign.Field.objective: AdCampaign.Objective.website_clicks,
        AdCampaign.Field.status: AdCampaign.Status.paused,
    })
    campaign.remote_create()
    print("**** DONE: Campaign created:")
    pp.pprint(campaign)

    ### Create an Ad Set
    ad_set = my_account.child(AdSet)
    ad_set.update({
        AdSet.Field.name: 'Puget Sound AdSet',
        AdSet.Field.status: AdSet.Status.paused,
        AdSet.Field.bid_type: AdSet.BidType.cpm,  # Bidding for impressions
        AdSet.Field.bid_info: {
            AdSet.Field.BidInfo.impressions: 500,   # $5 per 1000 impression
        },
        AdSet.Field.daily_budget: 3600,  # $36.00
        AdSet.Field.start_time: int(time.time()) + 15,  # 15 seconds from now
        AdSet.Field.campaign_group_id: campaign.get_id_assured(),
        AdSet.Field.targeting: {
            TargetingSpecsField.geo_locations: {
                'countries': [
                    'US',
                ],
            },
        },
    })
    ad_set.remote_create()
    print("**** DONE: Ad Set created:")
    pp.pprint(ad_set)

    ### Upload an image to an account.
    img = my_account.child(AdImage)
    img.remote_create_from_filename(os.path.join(this_dir, 'puget_sound.jpg'))
    print("**** DONE: Image uploaded:")
    pp.pprint(img)  # The image hash can be found using img[AdImage.Field.hash]

    ### Create a creative.
    creative = my_account.child(AdCreative)
    creative.update({
        AdCreative.Field.title: 'Visit Seattle',
        AdCreative.Field.body: 'Beautiful Puget Sound!',
        AdCreative.Field.object_url: 'http://www.seattle.gov/visiting/',
        AdCreative.Field.image_hash: img.get_hash(),
    })
    creative.remote_create()
    print("**** DONE: Creative created:")
    pp.pprint(creative)

    ### Get excited, we are finally creating an ad!!!
    ad = my_account.child(AdGroup)
    ad.update({
        AdGroup.Field.name: 'Puget Sound impression ad',
        AdGroup.Field.campaign_id: ad_set.get_id_assured(),
        AdGroup.Field.creative: {
            AdGroup.Field.Creative.creative_id: creative.get_id_assured(),
        },
    })
    ad.remote_create()
    print("**** DONE: Ad created:")
    pp.pprint(ad)
