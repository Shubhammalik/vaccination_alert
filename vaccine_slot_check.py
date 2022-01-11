import requests
import datetime
import smtplib
import schedule


class ApiError(Exception):
    """An API Error Exception"""

    def __init__(self, status):
        self.status = status

    def __str__(self):
        return "APIError: status={}".format(self.status)


def _url(path_component, path):
    scheme = 'https://'
    host = 'cdn-api.co-vin.in/api/v2'
    url = scheme + host + path_component + path
    return url


def get_json_data(path_component, path):
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    resp = requests.get(_url(path_component, path), headers=headers)
    if resp.status_code != 200:
        # This means request is wrong
        raise ApiError('GET {}'.format(resp.status_code))
    data = resp.json()
    return data


def request_state_data():
    path_component = '/admin/location'
    path = '/states'
    return get_json_data(path_component, path)


def request_districts_data(state_id):
    path_component = '/admin/location'
    path = '/districts/' + str(state_id)
    return get_json_data(path_component, path)


def request_center_data(district_id, today_date):
    path_component = '/appointment/sessions/public'
    endpoint = '/calendarByDistrict'
    query = '?district_id=' + str(district_id) + '&date=' + str(today_date)
    path = endpoint + query
    return get_json_data(path_component, path)


def get_stateId(state_name, state_id=0):
    if state_id == 0:
        data = request_state_data()
        for item in data['states']:
            if item['state_name'] == state_name:
                return item['state_id']
        print('Incorrect state name, use format: "Jammu and Kashmir"')
        return 0
    else:
        return state_id


def get_districtsId(state_name, district_name, state_id=0, district_id=0):
    if state_id == 0:
        state_id = get_stateId(state_name, state_id)
    if district_id == 0:
        data = request_districts_data(state_id)
        for item in data['districts']:
            if item['district_name'] == district_name:
                return item['district_id']
        print('Incorrect district name, use format: "Central Delhi"')
        return 0
    else:
        return district_id


def get_vaccine_centers(district_id, today_date, min_dose_available, dose, min_age_limit, vaccine, receiver_email_id, mail_receiver):
    data = request_center_data(district_id, today_date)
    center_list = list()
    district = data['centers'][0]['district_name']
    available_capacity = 'available_capacity_dose' + str(dose)
    for item in data['centers']:
        center_dict = {}
        for session_item in item['sessions']:
            if session_item[available_capacity] >= min_dose_available and session_item['min_age_limit'] == min_age_limit \
                    and session_item['vaccine'] == vaccine:
                center_dict['name'] = item['name']
                center_dict['center_id'] = item['center_id']
                center_dict['address'] = item['address']
                center_dict['block_name'] = item['block_name']
                center_dict['date'] = session_item['date']
                center_dict['available_capacity'] = session_item['available_capacity']
                if len(center_dict) > 0:
                    center_list.append(str(center_dict))

    if len(center_list):
        text1 = "{} Center(s) For {} Available in {}".format(len(center_list), vaccine, district)
        text2 = '\n\n'.join(center_list)
        text3 = text1 + '\n' + '\n' + text2
        print(text1)
        if mail_receiver == "yes" or  mail_receiver == "y":
            send_email(text3, receiver_email_id)
        for item in center_list:
            print(item)
    else:
        today = datetime.datetime.now() + datetime.timedelta(hours=12, minutes=30)
        today_time = today.strftime("%d-%m-%Y, %H:%M:%S")
        print(str(today_time) + " - No Vaccine Center found for " + district)


def send_email(TEXT, receiver_email_id):
    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    sender_email_id = 'newerrorfound404@gmail.com'
    sender_email_id_password = 'ofaheaajzivarvjk'
    s.login(sender_email_id, sender_email_id_password)

    # message to be sent
    SUBJECT = 'Vaccine Status'
    message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)

    # sending the mail
    s.sendmail(sender_email_id, receiver_email_id, message)

    # terminating the session
    s.quit()
    print('Email sent')


def check_availability():
    """
    Required PARAMETERS-
    state: name of state to check (format follow camel case with space)
    district: name of district (format follow camel case with space)
    today_date: today's date (converted from Canada time)
    min_dose_available: minimum dose to return true for availability (takes 0 to any numbers)
    min_age_limit: age limit for which it should be available (takes 18, 45)
    vaccine: name of the vaccine

    Optional PARAMETERS:
    state_id: coded, if not provided then will fetch all state (goes in get_districtId else 0)
    district_id: coded, if not provided then will fetch all district (goes in get_districtId else 0)

    :return: Total Vaccine Centers
    """
    today = datetime.datetime.now() + datetime.timedelta( hours=12, minutes=30)
    today_date = today.strftime("%d-%m-%Y")


    """
    ********************************************************************************************************
    DO NOT CHANGE ANYTHING ABOVE THIS LINE
    ********************************************************************************************************
    FILL THE DETAILS BELOW TO GET VACCINE INFORMATION
    """
    receiver_email_id = 'malikshubham74@gmail.com'
    state = "Haryana"
    district = "Rohtak"
    state_id = 12
    district_id = 192
    min_dose_available = 1
    dose = 2
    min_age_limit = 18
    vaccine = 'COVISHIELD'
    mail_receiver = "yes"

    get_vaccine_centers(get_districtsId(state, district, state_id, district_id), today_date, min_dose_available, dose,
                        min_age_limit, vaccine, receiver_email_id, mail_receiver.lower())


"""
SET THE TIME IN SECOND IN 3rd LINE BELOW TO SCHEDULE THE CHECK
CURRENTLY ITS SET TO 10 SECONDS 
"""
check_availability()
schedule.every(20).seconds.do(check_availability)

while 1:
    schedule.run_pending()
