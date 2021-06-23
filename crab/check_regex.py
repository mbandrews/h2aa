import re

#test_str = '/store/user/mandrews/2016/Era2016_06Sep2020_AODslim-ecal_v1/DoubleEG/crab_DoubleEG_2016B_Era2016_06Sep2020_AODslim-ecal_v1/200906_231343/0001/step_aodsim_slim-ecal_10000.root'
#test_str = '/store/user/mandrews/Era2016_06Sep2020_AODslim-ecal_v1/DoubleEG/crab_DoubleEG_2016B_Era2016_06Sep2020_AODslim-ecal_v1/200906_231343/0001/step_aodsim_slim-ecal_10000.root'
test_str = '/store/user/mandrews/Era2016/Era2016_06Sep2020_AODslim-ecal_v1/DoubleEG/crab_DoubleEG_2016B_Era2016_06Sep2020_AODslim-ecal_v1/200906_231343/0001/step_aodsim_slim-ecal_10000.root'
pattern_strs = [
'/store/(temp/)*(user|group)/(([a-zA-Z0-9\.]+)|([a-zA-Z0-9\-_]+))/([a-zA-Z][a-zA-Z0-9\-_]*)/([a-zA-Z0-9\-_]+)/([a-zA-Z0-9\-_]+)/([0-9]+)/([a-zA-Z0-9\-_]+).root',
'/store/(temp/)*(user|group)/(([a-zA-Z0-9\.]+)|([a-zA-Z0-9\-_]+))/([a-zA-Z][a-zA-Z0-9\-_]*)/(([a-zA-Z0-9\-_]+)/)+([a-zA-Z0-9\-_]+).root'
]

for p in pattern_strs:
    matched = re.match(p, test_str)
    is_match = bool(matched)
    print(is_match)
