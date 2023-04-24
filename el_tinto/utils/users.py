import random
import string

from django.db import connection

from el_tinto.users.models import User


def calculate_referred_users(user):
    """
    Calculate referred users invited by current user.
    Referred users are those who have been referred by someone and have opened at least
    one email. They can be active or inactive

    :params:
    user: User object

    :return:
    referred_users_count: int
    """
    referred_users = User.objects.filter(referred_by=user)

    referred_users_count = 0

    for referred_user in referred_users:
        if referred_user.sentemails_set.exclude(opened_date=None).count() > 0:
            referred_users_count += 1

    return referred_users_count


def create_user_referral_code(user):
    """
    Create a unique user referral code base on its email name without punctuation marks
    and two random alphanumeric values

    :params:
    user: User object

    :return:
    referral_code: str
    """
    user_email_name = user.email.split('@')[0]
    user_email_name_no_marks = user_email_name.translate(str.maketrans('', '', string.punctuation))

    base = user_email_name_no_marks[0:4]

    complement = ''.join(random.choices(string.ascii_letters + string.digits, k=6-len(base)))

    referral_code_exists = False

    while not referral_code_exists:
        referral_code = base + complement

        if User.objects.filter(referral_code=referral_code).exists():
            complement = ''.join(random.choices(string.ascii_letters + string.digits, k=6-len(base)))
        else:
            referral_code_exists = True

    return referral_code.upper()


def calculate_referral_race_parameters(user):
    """
    Calculates in what percentage of the total users the current user is
    based on the amount of users he/she has referred. Also, calculates
    what is the position in the referral race.

    :params:
    user: User object

    :return:
    referred_users_percentage: float
    user_referral_race_position: int
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            select numer_referrals, count(distinct referred_by_id) as numer_users
            from (
              select referred_by_id,
                     count(0) as numer_referrals
              from public.users_user
              where referred_by_id is not null
              group by 1
            ) t0
            group by 1
            order by numer_referrals
        """)

        referred_users_count_list = cursor.fetchall()

    user_referral_count = user.referred_users.count()

    total_users = User.objects.filter(is_active=True).count()

    if user_referral_count > 0:
        users_gte_current_user = 0
        user_referral_race_position = 1

        for referred_users_count in referred_users_count_list:

            if referred_users_count[0] >= user_referral_count:
                users_gte_current_user += referred_users_count[1]

            if referred_users_count[0] > user_referral_count:
                user_referral_race_position += 1

    else:
        users_gte_current_user = total_users
        user_referral_race_position = total_users

    # calculate percentile
    percentile = (users_gte_current_user / total_users) * 100

    return round(percentile), user_referral_race_position

