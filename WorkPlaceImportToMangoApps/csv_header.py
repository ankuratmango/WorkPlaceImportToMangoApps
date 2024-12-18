# Copyright 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
#user creation header columns(lowercase it all)
NAME_HEADER = 'name'
EMAIL_HEADER = 'email'
FIRST_NAME_HEADER = 'firstname'
LAST_NAME_HEADER = 'lastname'
JOB_HEADER = 'title'
DEPARTMENT_HEADER = 'department'
PHONE_HEADER = 'phone'
MOBILE_HEADER = 'mobile'
LOCATION_HEADER = 'Office Locations'
LOCALE_HEADER = 'locale'
MANAGER_HEADER = 'manager'
TIMEZONE_HEADER = 'timezone'
EXTERNALID_HEADER = 'external id'
ORGANIZATION_HEADER = 'organization'
STARTDATE_HEADER = 'date of joining'
DOB_HEADER = 'dob'
ALSOKNOWNAS_HEADER = 'also known as'


CREATE_UPDATE_REQUIRED_HEADERS = [NAME_HEADER, FIRST_NAME_HEADER, LAST_NAME_HEADER, EMAIL_HEADER, DOB_HEADER, JOB_HEADER, ORGANIZATION_HEADER, PHONE_HEADER, MOBILE_HEADER, MANAGER_HEADER, LOCALE_HEADER, LOCATION_HEADER, ALSOKNOWNAS_HEADER]
DELETION_HEADERS = [EMAIL_HEADER]
CREATE_UPDATE_EXPECTED_HEADERS = [NAME_HEADER, FIRST_NAME_HEADER, LAST_NAME_HEADER, EMAIL_HEADER, DOB_HEADER, JOB_HEADER, ORGANIZATION_HEADER, PHONE_HEADER, MOBILE_HEADER, MANAGER_HEADER, LOCALE_HEADER, LOCATION_HEADER, ALSOKNOWNAS_HEADER, STARTDATE_HEADER]