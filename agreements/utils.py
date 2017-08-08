from agreements.models import Agreement
from dc.num2t4ru import num2text


def prepare_values(agreement: Agreement):
    return {
        'pk': agreement.agreement_number,
        'agreement_date': agreement.agreement_date.strftime('%d.%m.%Y'),
        'city': agreement.city,
        'seller_user': "{} {} {}".format(agreement.seller_user_last_name, agreement.seller_user_first_name,
                                         agreement.seller_user_middle_name).strip(),
        'seller_user_last_name': agreement.seller_user_last_name,
        'seller_user_first_name_f': agreement.seller_user_first_name[0],
        'seller_user_middle_name_f': agreement.seller_user_middle_name[0],
        'seller_birthday': agreement.seller_birthday.strftime('%d.%m.%Y'),

        'seller_passport_seria': agreement.seller_passport_seria,
        'seller_passport_number': agreement.seller_passport_number,
        'seller_passport_date': agreement.seller_passport_date.strftime('%d.%m.%Y'),
        'seller_passport_org': agreement.seller_passport_org,

        'seller_address_fact': agreement.seller_address_fact,
        'seller_address_reg': agreement.seller_address_reg,

        # repr
        'repr_user': "{} {} {}".format(agreement.repr_user_last_name, agreement.repr_user_first_name,
                                        agreement.repr_user_middle_name).strip(),
        'repr_user_last_name': agreement.repr_user_last_name,
        'repr_user_first_name_f': agreement.repr_user_first_name[0] if agreement.repr_user_first_name else '',
        'repr_user_middle_name_f': agreement.repr_user_middle_name[0] if agreement.repr_user_middle_name else '',
        'repr_birthday': agreement.repr_birthday.strftime('%d.%m.%Y') if agreement.repr_birthday else '',

        'repr_document_number': agreement.repr_document_number,
        'repr_document_issued_date': agreement.repr_document_issued_date.strftime('%d.%m.%Y') \
            if agreement.repr_document_issued_date else '',
        'repr_document_verified_by': agreement.repr_document_verified_by,
        'repr_passport_seria': agreement.repr_passport_seria,
        'repr_passport_number': agreement.repr_passport_number,
        'repr_passport_date': agreement.repr_passport_date.strftime('%d.%m.%Y') if agreement.repr_passport_date else '',
        'repr_passport_org': agreement.repr_passport_org,

        'repr_address_reg': agreement.repr_address_reg,
        'repr_address_fact': agreement.repr_address_fact,

        # buyer
        'buyer_user': "{} {} {}".format(agreement.buyer_user_last_name, agreement.buyer_user_first_name,
                                         agreement.buyer_user_middle_name).strip(),
        'buyer_user_last_name': agreement.buyer_user_last_name,
        'buyer_user_first_name_f': agreement.buyer_user_first_name[0],
        'buyer_user_middle_name_f': agreement.buyer_user_middle_name[0],
        'buyer_birthday': agreement.buyer_birthday.strftime('%d.%m.%Y'),

        'buyer_passport_seria': agreement.buyer_passport_seria,
        'buyer_passport_number': agreement.buyer_passport_number,
        'buyer_passport_date': agreement.buyer_passport_date.strftime('%d.%m.%Y'),
        'buyer_passport_org': agreement.buyer_passport_org,

        'buyer_address_fact': agreement.buyer_address_fact,
        'buyer_address_reg': agreement.buyer_address_reg,

        # ts
        'ts_vin': agreement.ts_vin,
        'ts_body_num': agreement.ts_body_num,
        'ts_frame_num': agreement.ts_frame_num,
        'ts_mark': agreement.ts_mark,
        'ts_model': agreement.ts_model,
        'ts_year': agreement.ts_year,
        'ts_color': agreement.ts_color,
        'ts_reg_num': agreement.ts_reg_num,
        'ts_engine_num': agreement.ts_engine_num,

        # pts
        'pts_serial': agreement.pts_serial,
        'pts_num': agreement.pts_num,
        'pts_issued_date': agreement.pts_issued_date.strftime('%d.%m.%Y'),
        'pts_issued_by': agreement.pts_issued_by,
        # srts
        'srts_row': '- свидетельство о регистрации транспортного средства: серии {} № {}, '
                    'выданный {}, дата выдачи {} г.'.format(agreement.srts_serial, agreement.srts_num,
                                                            agreement.srts_issued_date.strftime('%d.%m.%Y'),
                                                            agreement.srts_issued_by) if agreement.srts_serial and agreement.srts_num else '',

        'price': str(agreement.price),
        'price_str': num2text(int(agreement.price)),

    }
