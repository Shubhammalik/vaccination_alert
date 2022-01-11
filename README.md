# Vaccination Alert
The program serves the need to get vaccine slot information from Indian Government API, the smtp protocol will send email to the provided email ID with slot availability.


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
