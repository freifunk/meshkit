# coding: utf8
# This table defines customizable texts you may use on your meshkit
# installation

db.define_table(
    'content_en',
    Field(
        'startpage',
        type='text',
        requires=IS_EMPTY_OR(
            IS_LENGTH(
                8192, 0,
                error_message=T(
                    '%(name)s can only be up to %(len)s characters long'
                ) % dict(name=T('Startpage'), len='8192')
            )
        )
    )
)

db.define_table(
    'content_de',
    Field(
        'startpage',
        type='text',
        requires=IS_EMPTY_OR(
            IS_LENGTH(
                8192, 0,
                error_message=T(
                    '%(name)s can only be up to %(len)s characters long'
                ) % dict(name=T('Startpage'), len='8192')
            )
        )
    )
)

content_en = db.content_en[1]
content_de = db.content_de[1]
