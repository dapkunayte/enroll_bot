from vedis import Vedis


monday = Vedis(':mem:')
monday['14:00'] = '30'
monday['16:00'] = '30'
monday['18:00'] = '30'

wednesday = Vedis(':mem:')
wednesday['14:00'] = '30'
wednesday['16:00'] = '1'
wednesday['18:00'] = '30'

friday = Vedis(':mem:')
friday['14:00'] = '0'
friday['16:00'] = '30'
friday['18:00'] = '30'

enrolls = Vedis(':mem:')
enrolls['users'] = ''

