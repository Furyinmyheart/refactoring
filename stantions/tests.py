import datetime
from django.test import TestCase
from django.utils import timezone

from stantions.forms import StantionEditAdminForm
from stantions.models import Stantion, Expert
from stantions.tasks import update_stantions_info
from users.models import MyUser, City


class TestStantionsModel(TestCase):
    def test_is_allow_create_false(self):
        stantion = Stantion(daily_limit=30, requests_created=30)
        self.assertEqual(stantion.is_allow_create(), False)

        stantion = Stantion(daily_limit=30, requests_created=20, available_b=False)
        self.assertEqual(stantion.is_allow_create(category=2), False)

        stantion = Stantion(daily_limit=30, requests_created=20,
                            freeze_date_end=timezone.now()+datetime.timedelta(minutes=5))
        self.assertEqual(stantion.is_allow_create(), False)

    def test_is_allow_create(self):
        stantion = Stantion(daily_limit=30, requests_created=20)
        self.assertEqual(stantion.is_allow_create(), True)

        stantion = Stantion(daily_limit=30, requests_created=20, available_b=True)
        self.assertEqual(stantion.is_allow_create(category=2), True)

    def test_get_point_address(self):
        stantion = Stantion(point_address='Test test test')
        self.assertEqual(stantion.get_point_address(), 'Test test test')

    def test_get_point_address_without_point_address(self):
        city = City.objects.create(name='test1')
        stantion = Stantion(city=city, address='Test, 123')
        self.assertEqual(stantion.get_point_address(), '{}, Test, 123'.format(city))

    def test_get_point_address_without_point_address_and_city(self):
        stantion = Stantion(address='Test, 123')
        self.assertEqual(stantion.get_point_address(), 'Test, 123')

    def test_get_point_address_empty(self):
        stantion = Stantion()
        self.assertEqual(stantion.get_point_address(), '')


class TestStantionGetAvailable(TestCase):
    def setUp(self):
        city = City.objects.create(name='test1')

        self.user1 = MyUser.objects.create(username='user1', fio='user1', city=city, is_active=True,
                                           use_only_self_stantions=True, stantion_order_type=2)
        self.user2 = MyUser.objects.create(username='user2', fio='user3', city=city, is_active=True,
                                           parent_id=self.user1.pk)
        self.user3 = MyUser.objects.create(username='user3', fio='user3', city=city, is_active=True)
        self.user4 = MyUser.objects.create(username='user4', fio='user4', city=city, is_active=True)
        self.user5 = MyUser.objects.create(username='user5', fio='user5', city=city, is_active=True,
                                           parent_id=self.user4.pk)
        self.user6 = MyUser.objects.create(username='user6', fio='user6', city=city, is_active=True,
                                           use_only_self_stantions=True)

        # available for all, except user[1,2,4,5]
        self.stantion1 = Stantion.objects.create(active=True, order=0, org_title='stantion1', reg_number=1,
                                                 daily_limit=30,
                                                 is_available_for_all_users=True)

        # available only for user1 and user2
        self.stantion2_user_1 = Stantion.objects.create(active=True, order=0, org_title='stantion2_user_1',
                                                        reg_number=2,
                                                        daily_limit=30, is_available_for_child=True)
        self.stantion2_user_1.users.add(self.user1)

        # available only for user4 and user 5
        self.stantion3_user_4 = Stantion.objects.create(active=True, order=0, org_title='stantion3_user_4',
                                                        reg_number=3,
                                                        daily_limit=30, is_available_for_child=True)
        self.stantion3_user_4.users.add(self.user4)

    def test_use_only_self_stantions(self):
        result = Stantion.objects.get_available_for_user(self.user1)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].pk, self.stantion2_user_1.pk)

    def test_use_only_self_stantions_order_type_1(self):
        self.user1.stantion_order_type = 1
        self.user1.save()
        self.stantion2_user_1.requests_created = 1
        self.stantion2_user_1.save()
        self.stantion4_user_1 = Stantion.objects.create(active=True, order=1, org_title='stantion4_user_1',
                                                        reg_number=2, requests_created=0,
                                                        daily_limit=30, is_available_for_child=True)
        self.stantion4_user_1.users.add(self.user1)

        result = Stantion.objects.get_available_for_user(self.user1)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].pk, self.stantion4_user_1.pk)

    def test_use_only_self_stantions_order_type_2(self):
        self.user1.stantion_order_type = 2
        self.user1.save()
        self.stantion2_user_1.order = 1
        self.stantion2_user_1.save()
        self.stantion4_user_1 = Stantion.objects.create(active=True, order=0, org_title='stantion4_user_1',
                                                        reg_number=2,
                                                        daily_limit=30, is_available_for_child=True)
        self.stantion4_user_1.users.add(self.user1)

        result = Stantion.objects.get_available_for_user(self.user1)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].pk, self.stantion4_user_1.pk)

    def test_user_stantions(self):
        result = Stantion.objects.get_available_for_user(self.user4)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].pk, self.stantion3_user_4.pk)

    def test_use_only_self_stantions_child(self):
        result = Stantion.objects.get_available_for_user(self.user2)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].pk, self.stantion2_user_1.pk)

    def test_use_only_self_stantions_child_order_type_1(self):
        self.user1.stantion_order_type = 1
        self.user1.save()
        self.stantion2_user_1.requests_created = 1
        self.stantion2_user_1.save()
        self.stantion4_user_1 = Stantion.objects.create(active=True, order=1, org_title='stantion4_user_1',
                                                        reg_number=2, requests_created=0,
                                                        daily_limit=30, is_available_for_child=True)
        self.stantion4_user_1.users.add(self.user1)

        result = Stantion.objects.get_available_for_user(self.user2)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].pk, self.stantion4_user_1.pk)

    def test_use_only_self_stantions_child_order_type_2(self):
        self.user1.stantion_order_type = 2
        self.user1.save()
        self.stantion2_user_1.order = 1
        self.stantion2_user_1.save()
        self.stantion4_user_1 = Stantion.objects.create(active=True, order=0, org_title='stantion4_user_1',
                                                        reg_number=2,
                                                        daily_limit=30, is_available_for_child=True)
        self.stantion4_user_1.users.add(self.user1)

        result = Stantion.objects.get_available_for_user(self.user2)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].pk, self.stantion4_user_1.pk)

    def test_user_stantions_child(self):
        result = Stantion.objects.get_available_for_user(self.user5)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].pk, self.stantion3_user_4.pk)

    def test_empty_stantion_is_use_only_self_stantions(self):
        result = Stantion.objects.get_available_for_user(self.user6)
        self.assertEqual(len(result), 0)

    def test_get_all_stantions(self):
        result = Stantion.objects.get_available_for_user(self.user3)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].pk, self.stantion1.pk)

    def test_get_all_stantions_unavailable(self):
        self.stantion1.requests_created = 30
        self.stantion1.save()
        result = Stantion.objects.get_available_for_user(self.user3)
        self.assertEqual(len(result), 0)

    def test_get_all_stantions_with_category(self):
        result = Stantion.objects.get_available_for_user(self.user3, category=2)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].pk, self.stantion1.pk)

    def test_get_all_stantions_unavailable_with_category(self):
        self.stantion1.available_b = False
        self.stantion1.save()
        result = Stantion.objects.get_available_for_user(self.user3, category=2)
        self.assertEqual(len(result), 0)

    # 4 test freeze date
    def test_get_all_stantions_with_freeze_date(self):
        self.stantion1.freeze_date_end = timezone.now() + datetime.timedelta(minutes=5)
        self.stantion1.save()

        result = Stantion.objects.get_available_for_user(self.user3)
        self.assertEqual(len(result), 0)

    def test_get_all_stantions_with_freeze_date_expiry(self):
        self.stantion1.freeze_date_end = timezone.now() - datetime.timedelta(minutes=5)
        self.stantion1.save()

        result = Stantion.objects.get_available_for_user(self.user3)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].pk, self.stantion1.pk)

    def test_user_stantions_with_freeze(self):
        self.stantion3_user_4.freeze_date_end = timezone.now() + datetime.timedelta(minutes=5)
        self.stantion3_user_4.save()

        result = Stantion.objects.get_available_for_user(self.user4)

        self.assertEqual(len(result), 0)

    def test_user_stantions_with_freeze_expiry(self):
        self.stantion3_user_4.freeze_date_end = timezone.now() - datetime.timedelta(minutes=5)
        self.stantion3_user_4.save()

        result = Stantion.objects.get_available_for_user(self.user4)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].pk, self.stantion3_user_4.pk)

    def test_user_stantions_child_with_freeze(self):
        self.stantion3_user_4.freeze_date_end = timezone.now() + datetime.timedelta(minutes=5)
        self.stantion3_user_4.save()

        result = Stantion.objects.get_available_for_user(self.user5)

        self.assertEqual(len(result), 0)

    def test_user_stantions_child_with_freeze_expiry(self):
        self.stantion3_user_4.freeze_date_end = timezone.now() - datetime.timedelta(minutes=5)
        self.stantion3_user_4.save()

        result = Stantion.objects.get_available_for_user(self.user5)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].pk, self.stantion3_user_4.pk)

    def test_user_stantions_get_all_if_set_users(self):
        self.stantion2_user_1.is_available_for_all_users = True
        self.stantion2_user_1.save()

        result = Stantion.objects.get_available_for_user(self.user3)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].pk, self.stantion1.pk)
        self.assertEqual(result[1].pk, self.stantion2_user_1.pk)


class TestUpdateUpdateStantionInfo(TestCase):
    def setUp(self):
        self.stantion = Stantion.objects.create(active=False, auto_update=True, order=0, org_title='stantion1',
                                                reg_number=101, daily_limit=30, is_available_for_all_users=True)
        self.expert = Expert.objects.create(last_name='1', first_name='2', stantion_id=self.stantion.pk)

        self.stantion_without_expert = Stantion.objects.create(active=False, auto_update=True, order=0,
                                                               org_title='stantion1', reg_number=101, daily_limit=30,
                                                               is_available_for_all_users=True)

    def test_update_stantion(self):
        update_stantions_info.apply()

        self.assertNotEqual(self.stantion.org_title, Stantion.objects.get(pk=self.stantion.pk).org_title)
        self.assertNotEqual(self.stantion.point_address, Stantion.objects.get(pk=self.stantion.pk).point_address)

        self.assertNotEqual(self.expert.last_name, Expert.objects.get(pk=self.expert.pk).last_name)
        self.assertNotEqual(self.expert.first_name, Expert.objects.get(pk=self.expert.pk).first_name)

        self.assertNotEqual(self.stantion.org_title, Stantion.objects.get(pk=self.stantion_without_expert.pk).org_title)
        self.assertEqual(len(self.stantion_without_expert.expert_set.all()), 1)


class TestStantionForms(TestCase):
    def setUp(self):
        self.user = MyUser.objects.create(username='user', fio='user', is_active=True)

    def test_form_success(self):
        form = StantionEditAdminForm({
            'active': True,
            'address': '634040, Томская обл, г Томск, ул Высоцкого Владимира, д. 6Г',
            'available_a': True,
            'available_b': True,
            'available_c': True,
            'available_d': True,
            'available_trailer': True,
            'city': '',
            'daily_limit': 80,
            'eaisto_login': 'alexspb',
            'eaisto_password': 'test',
            'interface_url': 'http://procard24.ru/ws/arm_operator_wsdl.php',
            'is_available_for_child': True,
            'order': 0,
            'org_title': 'ООО "ТЕХСЕРВИС"',
            'point_address': '',
            'post_index': '',
            'reg_number': '08155',
            'users': [self.user.pk],
        })
        self.assertTrue(form.is_valid())
        stantion = form.save()
        self.assertEqual(stantion.org_title, 'ООО "ТЕХСЕРВИС"')
        self.assertEqual(stantion.eaisto_login, "alexspb")
        self.assertEqual(stantion.eaisto_password, "test")
        self.assertEqual(stantion.interface_url, "http://procard24.ru/ws/arm_operator_wsdl.php")
        self.assertEqual(stantion.users.first(), self.user)

    def test_update_stantion(self):
        self.stantion = Stantion.objects.create(active=False, auto_update=True, order=0, org_title='stantion1',
                                                reg_number=101, daily_limit=30, is_available_for_all_users=True)

        form = StantionEditAdminForm({
            'active': True,
            'address': '634040, Томская обл, г Томск, ул Высоцкого Владимира, д. 6Г',
            'available_a': True,
            'available_b': True,
            'available_c': True,
            'available_d': True,
            'available_trailer': True,
            'city': '',
            'daily_limit': 80,
            'eaisto_login': 'alexspb',
            'eaisto_password': 'test',
            'interface_url': 'http://procard24.ru/ws/arm_operator_wsdl.php',
            'is_available_for_child': True,
            'order': 0,
            'org_title': 'ООО "ТЕХСЕРВИС"',
            'point_address': '',
            'post_index': '',
            'reg_number': '08155',
            'users': [self.user.pk],
        }, instance=self.stantion)

        self.assertTrue(form.is_valid())
        stantion = form.save()

        self.assertEqual(stantion.org_title, 'ООО "ТЕХСЕРВИС"')
        self.assertEqual(stantion.eaisto_login, "alexspb")
        self.assertEqual(stantion.eaisto_password, "test")
        self.assertEqual(stantion.interface_url, "http://procard24.ru/ws/arm_operator_wsdl.php")
        self.assertEqual(stantion.users.first(), self.user)